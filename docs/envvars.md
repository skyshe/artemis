This page contains information about the env variables set in the [.env file](https://github.com/FORTH-ICS-INSPIRE/artemis/blob/master/.env).

## Docker specific configs
Prefix for the container name (use only letters and numbers for the project name):
```
COMPOSE_PROJECT_NAME=artemis
```
Current version of the Database; used for migrations:
```
DB_VERSION=8
```
Enabled GUI:
```
GUI_ENABLED=true
```
System version (tags are automatically appended to the containers):
```
SYSTEM_VERSION=release-1.1.0
```
Use historical data (old, non-real-time bgp-updates):
```
HISTORIC=false
```

## Redis config

Redis IP and Port:
```
REDIS_HOST=redis
REDIS_PORT=6379
```

## API config

Postgrest container IP and PORT (containers have their name as hostname):
```
API_HOST=postgrest
API_PORT=3000
```

## Monitor-specific configs
Unique ID to be used for RIPE RIS BGP update streaming (recommended: use ASN)
```
RIS_ID=8522
```
Timeout (in seconds) since last seen BGP update for monitors (e.g., RIPE RIS, BGPStream RV, exaBGP, betaBMP, etc.).
If no update has been received by one of the monitors during this interval, the respective monitor is restarted. Historical monitors are excluded for obvious reasons.
```
MON_TIMEOUT_LAST_BGP_UPDATE=3600
```

## DB config (used by all containers)
Database IP and PORT:
```
DB_HOST=postgres
DB_PORT=5432
```
Default DB name, user, pass and schema:
```
DB_NAME=artemis_db
DB_USER=artemis_user
DB_PASS=Art3m1s
DB_SCHEMA=public
```
Database auto-backup (true or false) and auto-clean (how many hours before to remove) of non-hijack BGP updates:
```
DB_AUTOCLEAN=24 # deactivation with "false" (no autocleaning, keep everything)
DB_BACKUP=true
```
Characterization of "dormant hijacks (ongoing hijacks that have not been updated within so many hours as the variable states):
```
DB_HIJACK_DORMANT=24 # deactivation with "false" (no dormant hijack characterization)
```

## Frontend config
Listening address for frontend container (this is mapped from nginx so it can be left as is):
```
BIND_IP=0.0.0.0
```
Port where webapp is deployed:
```
WEBAPP_PORT=8000
```
Default credentials for admin user (**WARNING: please change the default ones before deploying!**):
```
ADMIN_USER=admin
ADMIN_PASS=admin123
ADMIN_EMAIL=admin@admin
```
Javascript Script version to avoid browser caching:
```
JS_VERSION=0.1.0
```
Web host name (used for connect-src CSP policy, typically the DNS name or IP address of the ARTEMIS server)
```
ARTEMIS_WEB_HOST=artemis.com
```
Number of GUnicorn workers that serve frontend:
```
GUNICORN_WORKERS=4
```

## Rabbitmq config
RabbitMQ IP, port, user and password:
```
RABBITMQ_HOST=rabbitmq
RABBITMQ_PORT=5672
RABBITMQ_USER=guest
RABBITMQ_PASS=guest
```
RabbitMQ thread pool size:
```
RABBITMQ_IO_THREAD_POOL_SIZE=128
```

## Hasura config
Hasura IP and port:
```
HASURA_HOST=graphql
HASURA_PORT=8080
```

Enable/Disable hasura CLI:
```
HASURA_GUI=false
```

## Secret keys
Master password for Hasura (**WARNING: please change the default one before deploying!**):
```
HASURA_SECRET_KEY=@rt3m1s.
```
Secret keys and password salt (**WARNING: please change the default ones before deploying**):
```
JWT_SECRET_KEY=44fe431cdc896ccab691ad0599f4e0a12690ce1ededebe57b825823bc6b4d24f
FLASK_SECRET_KEY=76f8bae45e807865955344c1a58882d38c8ceb4f855f58091642b7d48290af97
SECURITY_PASSWORD_SALT=06a4b397fc7045eac527c2aec3ff46cee5ce30016c760f238c26e79902fe67b6
```

## Community log filter
Custom log filter for logging on syslog (or email or other logs) only hijacks with a certain annotation, see [this page](https://bgpartemis.readthedocs.io/en/latest/commannotations/):
```
HIJACK_LOG_FILTER=[{"community_annotation":"critical"},{"community_annotation":"NA"}]
```

## Hijack log fields to log
```
HIJACK_LOG_FIELDS=["prefix","hijack_as","type","time_started","time_last","peers_seen","configured_prefix","timestamp_of_config","asns_inf","time_detected","key","community_annotation","end_tag","hijack_url"]
```

## Withdrawn hijack peer threshold
(percentage of monitor peers that have seen hijack updates, required to see corresponding withdrawals to declare a hijack as withdrawn)
```
WITHDRAWN_HIJACK_THRESHOLD=80
```
## RPKI configuration
RPKI_VALIDATOR_ENABLED=false # set to true only if you have or spawn a working RPKI validator
RPKI_VALIDATOR_HOST=routinator # change to the IP of the validator of your choice
RPKI_VALIDATOR_PORT=3323 # change to the preferred port (default for RTR protocol)

## Auto-recovery of intended process states
AUTO_RECOVER_PROCESS_STATE=true # flag to signal whether ARTEMIS should auto-enforce intended process state (running/stopped) on startup

## Notes on decoupling env file from current location
Note that at the current time, it is not advised to move the `.env` file to another folder because it is still an ongoing issue to support external .env files in the docker-compose repository
[docker/compose#6170](https://github.com/docker/compose/issues/6170). However, since we deal with environment variables, you can delete the `.env` file and actually import them through another script that is located somewhere else. if [this issue](https://github.com/docker/compose/pull/6535) gets merged, then you can use a different env file with --env-file. Otherwise, you can run it with something like:
```
env $(cat path/to/env) docker-compose up
```
For more information please check also [this issue](https://github.com/FORTH-ICS-INSPIRE/artemis/issues/96).
