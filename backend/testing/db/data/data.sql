COPY bgp_updates (key, prefix, origin_as, peer_asn, as_path, service, type, communities, "timestamp", hijack_key, handled, matched_prefix, orig_path) FROM stdin;
61abd848862ccf957d11fc9726ee1602	139.5.46.0/24	133720	8283	{8283,6453,4755,45194,133720,133720,133720}	ripe-ris|rrc03	A	[[6453, 2000], [6453, 2100], [6453, 2104], [6453, 10002], [8283, 1], [8283, 101]]	2019-02-23 16:59:05.62	{a}	t	139.0.0.0/8	null
c641d5cc2529b9fc3df8316b2b1b8d87	139.5.236.0/24	136334	8283	{8283,6453,4755,45194,136334}	ripe-ris|rrc03	A	[[6453, 2000], [6453, 2100], [6453, 2104], [6453, 10002], [8283, 1], [8283, 101]]	2019-02-23 16:59:05.75	{b}	t	139.0.0.0/8	null
4e7eed3e86a4cdaf2165b2e56ad016b4	139.5.237.0/24	136334	8283	{8283,6453,4755,45194,136334}	ripe-ris|rrc03	A	[[6453, 2000], [6453, 2100], [6453, 2104], [6453, 10002], [8283, 1], [8283, 101]]	2019-02-23 16:59:05.75	{c}	t	139.0.0.0/8	null
79fccbbcfcb6b8aadf9a91b5560b5abe	139.5.238.0/24	136334	8283	{8283,6453,4755,45194,136334}	ripe-ris|rrc03	A	[[6453, 2000], [6453, 2100], [6453, 2104], [6453, 10002], [8283, 1], [8283, 101]]	2019-02-23 16:59:05.75	{d}	t	139.0.0.0/8	null
3e79b39bfd7862a0c757b31501d16bbf	139.5.239.0/24	136334	8283	{8283,6453,4755,45194,136334}	ripe-ris|rrc03	A	[[6453, 2000], [6453, 2100], [6453, 2104], [6453, 10002], [8283, 1], [8283, 101]]	2019-02-23 16:59:05.75	{e}	t	139.0.0.0/8	null
ca7a6987045334df736c0569e3aa17fc	139.5.29.0/24	133720	8283	{8283,6453,4755,45194,133720}	ripe-ris|rrc03	A	[[6453, 2000], [6453, 2100], [6453, 2104], [6453, 10002], [8283, 1], [8283, 101]]	2019-02-23 16:59:05.76	{f}	t	139.0.0.0/8	null
d6581b8e5efc20c67404683ea16d9f04	139.5.45.0/24	133720	8283	{8283,6453,4755,45194,133720}	ripe-ris|rrc03	A	[[6453, 2000], [6453, 2100], [6453, 2104], [6453, 10002], [8283, 1], [8283, 101]]	2019-02-23 16:59:05.76	{g}	t	139.0.0.0/8	null
4a647d51626bad5763a659215cf93b24	139.5.24.0/24	133720	8283	{8283,6453,4755,45194,133720}	ripe-ris|rrc03	A	[[6453, 2000], [6453, 2100], [6453, 2104], [6453, 10002], [8283, 1], [8283, 101]]	2019-02-23 16:59:05.76	{h}	t	139.0.0.0/8	null
b4b5125fe7f7530a2aad50a5b6dbbde4	139.5.16.0/22	133676	8283	{8283,6453,4755,133676}	ripe-ris|rrc03	A	[[6453, 2000], [6453, 2100], [6453, 2104], [6453, 10002], [8283, 1], [8283, 101]]	2019-02-23 16:59:05.76	{i}	t	139.0.0.0/8	null
\.

COPY hijacks (key, type, prefix, hijack_as, peers_seen, peers_withdrawn, num_peers_seen, asns_inf, num_asns_inf, time_started, time_last, time_ended, mitigation_started, time_detected, under_mitigation, resolved, active, ignored, withdrawn, outdated, configured_prefix, timestamp_of_config, comment, seen) FROM stdin;
a	S|0|-	139.5.46.0/24	133720	{263584,328145,8283,58511}	{}	4	{263584,263321,57866,45194,58511,328145,4755,1299,6453,3257,8283,3356,3549}	13	2019-02-17 11:08:28	2019-02-23 16:59:05.000062	\N	\N	2019-02-17 12:08:30.138569	f	f	t	f	f	f	139.0.0.0/8	2019-02-17 12:08:14.060917		f
b	S|0|-	139.5.236.0/24	136334	{263584,58511,52720,328145,8283}	{}	5	{263584,263321,52873,57866,45194,58511,52720,328145,4755,1299,6453,3356,3257,8283,12956,3549}	16	2019-02-17 11:08:21	2019-02-23 16:59:05.000075	\N	\N	2019-02-17 12:08:28.67352	f	f	t	f	f	f	139.0.0.0/8	2019-02-17 12:08:14.060917		f
c	S|0|-	139.5.237.0/24	136334	{263584,58511,52720,328145,8283}	{}	5	{263584,263321,52873,57866,45194,58511,52720,328145,4755,1299,6453,3356,3257,8283,12956,3549}	16	2019-02-17 11:08:21	2019-02-23 16:59:05.000075	\N	\N	2019-02-17 12:08:28.668269	f	f	t	f	f	f	139.0.0.0/8	2019-02-17 12:08:14.060917		f
d	S|0|-	139.5.238.0/24	136334	{263584,58511,52720,328145,8283}	{}	5	{263584,263321,52873,57866,45194,58511,52720,328145,4755,1299,6453,3356,3257,8283,12956,3549}	16	2019-02-17 11:08:21	2019-02-23 16:59:05.000075	\N	\N	2019-02-17 12:08:28.663092	f	f	t	f	f	f	139.0.0.0/8	2019-02-17 12:08:14.060917		f
e	S|0|-	139.5.239.0/24	136334	{263584,58511,52720,328145,8283,16735}	{}	6	{263584,12956,3257,52873,57866,45194,174,58511,52720,328145,4755,1299,6453,263321,8283,3356,3549,16735}	18	2019-02-17 11:08:21	2019-02-23 16:59:05.000075	\N	\N	2019-02-17 12:08:28.65761	f	f	t	f	f	f	139.0.0.0/8	2019-02-17 12:08:14.060917		f
f	S|0|-	139.5.29.0/24	133720	{263584,58511,52720,328145,8283}	{}	5	{263584,263321,52873,57866,45194,58511,52720,328145,4755,1299,6453,3356,3257,8283,12956,3549}	16	2019-02-17 11:08:23	2019-02-23 16:59:05.000076	\N	\N	2019-02-17 12:08:28.714184	f	f	t	f	f	f	139.0.0.0/8	2019-02-17 12:08:14.060917		f
g	S|0|-	139.5.45.0/24	133720	{263584,58511,52720,328145,8283}	{}	5	{263584,263321,52873,57866,45194,58511,52720,328145,4755,1299,6453,3356,3257,8283,12956,3549}	16	2019-02-17 11:08:28	2019-02-23 16:59:05.000076	\N	\N	2019-02-17 12:08:30.144024	f	f	t	f	f	f	139.0.0.0/8	2019-02-17 12:08:14.060917		f
h	S|0|-	139.5.24.0/24	133720	{263584,58511,52720,328145,8283}	{}	5	{263584,263321,52873,57866,45194,58511,52720,328145,4755,1299,6453,3356,3257,8283,12956,3549}	16	2019-02-17 11:08:24	2019-02-23 16:59:05.000076	\N	\N	2019-02-17 12:08:29.703244	f	f	t	f	f	f	139.0.0.0/8	2019-02-17 12:08:14.060917		f
i	S|0|-	139.5.16.0/22	133676	{263584,58511,52720,328145,8283}	{}	5	{263584,263321,52873,57866,58511,52720,328145,4755,1299,6453,3356,3257,8283,12956,3549}	15	2019-02-17 11:08:24	2019-02-23 16:59:05.000076	\N	\N	2019-02-17 12:08:29.771792	f	f	t	f	f	f	139.0.0.0/8	2019-02-17 12:08:14.060917		f
\.
