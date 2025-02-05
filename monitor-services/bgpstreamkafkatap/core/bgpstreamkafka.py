import multiprocessing as mp
import os
import signal
import time

import _pybgpstream
import pytricia
import redis
import requests
import ujson as json
from artemis_utils import get_ip_version
from artemis_utils import get_logger
from artemis_utils.constants import CONFIGURATION_HOST
from artemis_utils.constants import DATABASE_HOST
from artemis_utils.constants import MAX_DATA_WORKER_WAIT_TIMEOUT
from artemis_utils.constants import PREFIXTREE_HOST
from artemis_utils.constants import START_TIME_OFFSET
from artemis_utils.envvars import MON_TIMEOUT_LAST_BGP_UPDATE
from artemis_utils.envvars import RABBITMQ_URI
from artemis_utils.envvars import REDIS_HOST
from artemis_utils.envvars import REDIS_PORT
from artemis_utils.envvars import REST_PORT
from artemis_utils.rabbitmq import create_exchange
from artemis_utils.redis import ping_redis
from artemis_utils.updates import key_generator
from artemis_utils.updates import MformatValidator
from artemis_utils.updates import normalize_msg_path
from kombu import Connection
from kombu import Producer
from tornado.ioloop import IOLoop
from tornado.web import Application
from tornado.web import RequestHandler

# install as described in https://bgpstream.caida.org/docs/install/pybgpstream

# logger
log = get_logger()

# shared memory object locks
shared_memory_locks = {
    "data_worker": mp.Lock(),
    "monitored_prefixes": mp.Lock(),
    "host": mp.Lock(),
    "port": mp.Lock(),
    "topic": mp.Lock(),
    "config_timestamp": mp.Lock(),
}

# global vars
redis = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)
SERVICE_NAME = "bgpstreamkafkatap"

# TODO: introduce redis-based restart logic (if no data is received within certain time frame)


def start_data_worker(shared_memory_manager_dict):
    shared_memory_locks["data_worker"].acquire()
    if not shared_memory_manager_dict["data_worker_configured"]:
        shared_memory_locks["data_worker"].release()
        return "not configured, will not start"
    if shared_memory_manager_dict["data_worker_running"]:
        log.info("data worker already running")
        shared_memory_locks["data_worker"].release()
        return "already running"
    shared_memory_locks["data_worker"].release()
    data_worker_process = mp.Process(
        target=run_data_worker_process, args=(shared_memory_manager_dict,)
    )
    data_worker_process.start()
    shared_memory_locks["data_worker"].acquire()
    shared_memory_manager_dict["data_worker_process"] = data_worker_process.pid
    shared_memory_locks["data_worker"].release()
    return "instructed to start"


def run_data_worker_process(shared_memory_manager_dict):
    try:
        with Connection(RABBITMQ_URI) as connection:
            shared_memory_locks["data_worker"].acquire()
            data_worker = BGPStreamKafkaDataWorker(
                connection, shared_memory_manager_dict
            )
            shared_memory_manager_dict["data_worker_should_run"] = True
            shared_memory_manager_dict["data_worker_running"] = True
            shared_memory_locks["data_worker"].release()
            log.info("data worker started")
            data_worker.run()
    except Exception:
        log.exception("exception")
    finally:
        shared_memory_locks["data_worker"].acquire()
        shared_memory_manager_dict["data_worker_running"] = False
        shared_memory_locks["data_worker"].release()
        log.info("data worker stopped")


def stop_data_worker(shared_memory_manager_dict):
    shared_memory_locks["data_worker"].acquire()
    shared_memory_manager_dict["data_worker_should_run"] = False
    shared_memory_locks["data_worker"].release()
    # make sure that data worker is stopped
    time_waiting = 0
    while True:
        if not shared_memory_manager_dict["data_worker_running"]:
            break
        time.sleep(1)
        time_waiting += 1
        if time_waiting == MAX_DATA_WORKER_WAIT_TIMEOUT:
            log.error(
                "timeout expired during stop-waiting, will kill process non-gracefully"
            )
            if shared_memory_manager_dict["data_worker_process"] is not None:
                os.kill(
                    shared_memory_manager_dict["data_worker_process"], signal.SIGKILL
                )
                shared_memory_locks["data_worker"].acquire()
                shared_memory_manager_dict["data_worker_process"] = None
                shared_memory_locks["data_worker"].release()
            shared_memory_locks["data_worker"].acquire()
            shared_memory_manager_dict["data_worker_running"] = False
            shared_memory_locks["data_worker"].release()
            return "killed"
    message = "instructed to stop"
    return message


def configure_bgpstreamkafka(msg, shared_memory_manager_dict):
    config = msg
    try:
        # check newer config
        config_timestamp = shared_memory_manager_dict["config_timestamp"]
        if config["timestamp"] > config_timestamp:
            # get monitors
            r = requests.get("http://{}:{}/monitors".format(DATABASE_HOST, REST_PORT))
            monitors = r.json()["monitors"]

            # check if "bgpstreamkafka" is configured at all
            if "bgpstreamkafka" not in monitors:
                stop_msg = stop_data_worker(shared_memory_manager_dict)
                log.info(stop_msg)
                shared_memory_locks["data_worker"].acquire()
                shared_memory_manager_dict["data_worker_configured"] = False
                shared_memory_locks["data_worker"].release()
                return {"success": True, "message": "data worker not in configuration"}

            # check if the worker should run (if configured)
            should_run = shared_memory_manager_dict["data_worker_should_run"]

            # make sure that data worker is stopped
            stop_msg = stop_data_worker(shared_memory_manager_dict)
            log.info(stop_msg)

            # get monitored prefixes
            r = requests.get(
                "http://{}:{}/monitoredPrefixes".format(PREFIXTREE_HOST, REST_PORT)
            )
            shared_memory_locks["monitored_prefixes"].acquire()
            shared_memory_manager_dict["monitored_prefixes"] = r.json()[
                "monitored_prefixes"
            ]
            shared_memory_locks["monitored_prefixes"].release()

            # get kafka host, port and topic
            shared_memory_locks["host"].acquire()
            shared_memory_manager_dict["host"] = str(monitors["bgpstreamkafka"]["host"])
            shared_memory_locks["host"].release()

            shared_memory_locks["port"].acquire()
            shared_memory_manager_dict["port"] = str(monitors["bgpstreamkafka"]["port"])
            shared_memory_locks["port"].release()

            shared_memory_locks["topic"].acquire()
            shared_memory_manager_dict["topic"] = str(
                monitors["bgpstreamkafka"]["topic"]
            )
            shared_memory_locks["topic"].release()

            # signal that data worker is configured
            shared_memory_locks["data_worker"].acquire()
            shared_memory_manager_dict["data_worker_configured"] = True
            shared_memory_locks["data_worker"].release()

            shared_memory_locks["config_timestamp"].acquire()
            shared_memory_manager_dict["config_timestamp"] = config["timestamp"]
            shared_memory_locks["config_timestamp"].release()

            # start the data worker only if it should be running
            if should_run:
                start_msg = start_data_worker(shared_memory_manager_dict)
                log.info(start_msg)

        return {"success": True, "message": "configured"}
    except Exception:
        log.exception("exception")
        return {"success": False, "message": "error during data worker configuration"}


class ConfigHandler(RequestHandler):
    """
    REST request handler for configuration.
    """

    def initialize(self, shared_memory_manager_dict):
        self.shared_memory_manager_dict = shared_memory_manager_dict

    def get(self):
        """
        Provides current configuration primitives (in the form of a JSON dict) to the requester.
        Format:
        {
            "data_worker_should_run": <bool>,
            "data_worker_configured": <bool>,
            "monitored_prefixes": <list>,
            "host": <str>,
            "port": <str>,
            "topic": <str>,
            "config_timestamp": <timestamp>
        }
        """
        ret_dict = {}

        ret_dict["data_worker_should_run"] = self.shared_memory_manager_dict[
            "data_worker_should_run"
        ]
        ret_dict["data_worker_configured"] = self.shared_memory_manager_dict[
            "data_worker_configured"
        ]

        ret_dict["monitored_prefixes"] = self.shared_memory_manager_dict[
            "monitored_prefixes"
        ]

        ret_dict["host"] = self.shared_memory_manager_dict["host"]

        ret_dict["port"] = self.shared_memory_manager_dict["port"]

        ret_dict["topic"] = self.shared_memory_manager_dict["topic"]

        ret_dict["config_timestamp"] = self.shared_memory_manager_dict[
            "config_timestamp"
        ]

        self.write(ret_dict)

    def post(self):
        """
        Handler for posted configuration from configuration.
        Note that for performance reasons the eventual needed elements
        are collected from the prefix tree service.
        :return: {"success": True|False, "message": <message>}
        """
        try:
            msg = json.loads(self.request.body)
            self.write(configure_bgpstreamkafka(msg, self.shared_memory_manager_dict))
        except Exception:
            self.write(
                {"success": False, "message": "error during data worker configuration"}
            )


class HealthHandler(RequestHandler):
    """
    REST request handler for health checks.
    """

    def initialize(self, shared_memory_manager_dict):
        self.shared_memory_manager_dict = shared_memory_manager_dict

    def get(self):
        """
        Extract the status of a service via a GET request.
        :return: {"status" : <unconfigured|running|stopped>}
        """
        status = "stopped"
        shared_memory_locks["data_worker"].acquire()
        if self.shared_memory_manager_dict["data_worker_running"]:
            status = "running"
        elif not self.shared_memory_manager_dict["data_worker_configured"]:
            status = "unconfigured"
        shared_memory_locks["data_worker"].release()
        self.write({"status": status})


class ControlHandler(RequestHandler):
    """
    REST request handler for control commands.
    """

    def initialize(self, shared_memory_manager_dict):
        self.shared_memory_manager_dict = shared_memory_manager_dict

    def post(self):
        """
        Instruct a service to start or stop by posting a command.
        Sample request body
        {
            "command": <start|stop>
        }
        :return: {"success": True|False, "message": <message>}
        """
        try:
            msg = json.loads(self.request.body)
            command = msg["command"]
            # start/stop data_worker
            if command == "start":
                message = start_data_worker(self.shared_memory_manager_dict)
                self.write({"success": True, "message": message})
            elif command == "stop":
                message = stop_data_worker(self.shared_memory_manager_dict)
                self.write({"success": True, "message": message})
            else:
                self.write({"success": False, "message": "unknown command"})
        except Exception:
            log.exception("Exception")
            self.write({"success": False, "message": "error during control"})


class BGPStreamKafkaTap:
    """
    BGPStream Kafka Tap REST Service.
    """

    def __init__(self):
        # initialize shared memory
        shared_memory_manager = mp.Manager()
        self.shared_memory_manager_dict = shared_memory_manager.dict()
        self.shared_memory_manager_dict["data_worker_running"] = False
        self.shared_memory_manager_dict["data_worker_should_run"] = False
        self.shared_memory_manager_dict["data_worker_configured"] = False
        self.shared_memory_manager_dict["monitored_prefixes"] = list()
        self.shared_memory_manager_dict["host"] = ""
        self.shared_memory_manager_dict["port"] = ""
        self.shared_memory_manager_dict["topic"] = ""
        self.shared_memory_manager_dict["config_timestamp"] = -1
        self.shared_memory_manager_dict["data_worker_process"] = None

        log.info("service initiated")

    def make_rest_app(self):
        return Application(
            [
                (
                    "/config",
                    ConfigHandler,
                    dict(shared_memory_manager_dict=self.shared_memory_manager_dict),
                ),
                (
                    "/control",
                    ControlHandler,
                    dict(shared_memory_manager_dict=self.shared_memory_manager_dict),
                ),
                (
                    "/health",
                    HealthHandler,
                    dict(shared_memory_manager_dict=self.shared_memory_manager_dict),
                ),
            ]
        )

    def start_rest_app(self):
        app = self.make_rest_app()
        app.listen(REST_PORT)
        log.info("REST worker started and listening to port {}".format(REST_PORT))
        IOLoop.current().start()


class BGPStreamKafkaDataWorker:
    """
    RabbitMQ Producer for the BGPStream Kafka tap Service.
    """

    def __init__(self, connection, shared_memory_manager_dict):
        self.connection = connection
        self.shared_memory_manager_dict = shared_memory_manager_dict
        self.prefixes = self.shared_memory_manager_dict["monitored_prefixes"]
        self.host = shared_memory_manager_dict["host"]
        self.port = shared_memory_manager_dict["port"]
        self.topic = shared_memory_manager_dict["topic"]

        # EXCHANGES
        self.update_exchange = create_exchange(
            "bgp-update", self.connection, declare=True
        )

        log.info("data worker initiated")

    def run(self):
        # update redis
        ping_redis(redis)
        redis.set("bgpstreamkafka_seen_bgp_update", "1", ex=MON_TIMEOUT_LAST_BGP_UPDATE)

        # create a new bgpstream instance and a reusable bgprecord instance
        stream = _pybgpstream.BGPStream()

        # set kafka data interface
        stream.set_data_interface("kafka")

        # set host connection details
        stream.set_data_interface_option(
            "kafka", "brokers", "{}:{}".format(self.host, self.port)
        )

        # set topic
        stream.set_data_interface_option("kafka", "topic", self.topic)

        # filter prefixes
        for prefix in self.prefixes:
            stream.add_filter("prefix", prefix)

        # build monitored prefix tree
        prefix_tree = {"v4": pytricia.PyTricia(32), "v6": pytricia.PyTricia(128)}
        for prefix in self.prefixes:
            ip_version = get_ip_version(prefix)
            prefix_tree[ip_version].insert(prefix, "")

        # filter record type
        stream.add_filter("record-type", "updates")

        # filter based on timing (if end=0 --> live mode)
        # Bypass for https://github.com/FORTH-ICS-INSPIRE/artemis/issues/411#issuecomment-661325802
        start_time = int(time.time()) - START_TIME_OFFSET
        if "BGPSTREAM_TIMESTAMP_BYPASS" in os.environ:
            log.warn(
                "Using BGPSTREAM_TIMESTAMP_BYPASS, meaning BMP timestamps are thrown away from BGPStream"
            )
            start_time = 0
        stream.add_interval_filter(start_time, 0)

        # set live mode
        stream.set_live_mode()

        # start the stream
        stream.start()

        # start producing
        validator = MformatValidator()
        with Producer(self.connection) as producer:
            while True:
                if not self.shared_memory_manager_dict["data_worker_should_run"]:
                    break

                # get next record
                try:
                    rec = stream.get_next_record()
                except BaseException:
                    continue

                if (rec.status != "valid") or (rec.type != "update"):
                    continue

                # get next element
                try:
                    elem = rec.get_next_elem()
                except BaseException:
                    continue

                while elem:
                    if not self.shared_memory_manager_dict["data_worker_should_run"]:
                        break

                    if elem.type in {"A", "W"}:
                        redis.set(
                            "bgpstreamkafka_seen_bgp_update",
                            "1",
                            ex=MON_TIMEOUT_LAST_BGP_UPDATE,
                        )
                        this_prefix = str(elem.fields["prefix"])
                        service = "bgpstreamkafka|{}".format(str(rec.collector))
                        type_ = elem.type
                        if type_ == "A":
                            as_path = elem.fields["as-path"].split(" ")
                            communities = [
                                {
                                    "asn": int(comm.split(":")[0]),
                                    "value": int(comm.split(":")[1]),
                                }
                                for comm in elem.fields["communities"]
                            ]
                        else:
                            as_path = []
                            communities = []
                        timestamp = float(rec.time)
                        if timestamp == 0:
                            timestamp = time.time()
                            log.debug("fixed timestamp: {}".format(timestamp))
                        peer_asn = elem.peer_asn

                        ip_version = get_ip_version(this_prefix)
                        if this_prefix in prefix_tree[ip_version]:
                            msg = {
                                "type": type_,
                                "timestamp": timestamp,
                                "path": as_path,
                                "service": service,
                                "communities": communities,
                                "prefix": this_prefix,
                                "peer_asn": peer_asn,
                            }
                            try:
                                if validator.validate(msg):
                                    msgs = normalize_msg_path(msg)
                                    for msg in msgs:
                                        key_generator(msg)
                                        log.debug(msg)
                                        producer.publish(
                                            msg,
                                            exchange=self.update_exchange,
                                            routing_key="update",
                                            serializer="ujson",
                                        )
                                else:
                                    log.warning(
                                        "Invalid format message: {}".format(msg)
                                    )
                            except BaseException:
                                log.exception(
                                    "Error when normalizing BGP message: {}".format(msg)
                                )
                    try:
                        elem = rec.get_next_elem()
                    except BaseException:
                        continue


def main():
    # initiate BGPStream Kafka tap service with REST
    bgpStreamKafkaTapService = BGPStreamKafkaTap()

    # try to get configuration upon start (it is OK if it fails, will get it from POST)
    # (this is needed because service may restart while configuration is running)
    try:
        r = requests.get("http://{}:{}/config".format(CONFIGURATION_HOST, REST_PORT))
        conf_res = configure_bgpstreamkafka(
            r.json(), bgpStreamKafkaTapService.shared_memory_manager_dict
        )
        if not conf_res["success"]:
            log.info(
                "could not get configuration upon startup, will get via POST later"
            )
    except Exception:
        log.info("could not get configuration upon startup, will get via POST later")

    # start REST within main process
    bgpStreamKafkaTapService.start_rest_app()


if __name__ == "__main__":
    main()
