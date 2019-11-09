BEGIN;

CREATE TABLE dbase03table (
	id INTEGER PRIMARY KEY,
	point_id TEXT,
	type TEXT,
	shape TEXT,
	circular_d TEXT,
	non_circul TEXT,
	flow_prese TEXT,
	condition TEXT,
	comments TEXT,
	date_visit DATE,
	time TEXT,
	max_pdop DECIMAL(10, 5),
	max_hdop DECIMAL(10, 5),
	corr_type TEXT,
	rcvr_type TEXT,
	gps_date DATE,
	gps_time TEXT,
	update_sta TEXT,
	feat_name TEXT,
	datafile TEXT,
	unfilt_pos DECIMAL(20, 10),
	filt_pos DECIMAL(20, 10),
	data_dicti TEXT,
	gps_week DECIMAL(12, 6),
	gps_second DECIMAL(24, 12),
	gps_height DECIMAL(32, 16),
	vert_prec DECIMAL(32, 16),
	horz_prec DECIMAL(32, 16),
	std_dev DECIMAL(32, 16),
	northing DECIMAL(32, 16),
	easting DECIMAL(32, 16)
);

INSERT INTO dbase03table VALUES (0,'0507121','CMP','circular','12','','no','Good','','2005-07-12','10:56:30am',5.2,2.0,'Postprocessed Code','GeoXT','2005-07-12','10:56:52am','New','Driveway','050712TR2819.cor',2,2,'MS4',1331,226625.000,1131.323,3.1,1.3,0.897088,557904.898,2212577.192);
INSERT INTO dbase03table VALUES (1,'0507122','CMP','circular','12','','no','Good','','2005-07-12','10:57:34am',4.9,2.0,'Postprocessed Code','GeoXT','2005-07-12','10:57:37am','New','Driveway','050712TR2819.cor',1,1,'MS4',1331,226670.000,1125.142,2.8,1.3,NULL,557997.831,2212576.868);
INSERT INTO dbase03table VALUES (2,'0507123','CMP','circular','12','','no','Good','','2005-07-12','10:59:03am',5.4,4.4,'Postprocessed Code','GeoXT','2005-07-12','10:59:12am','New','Driveway','050712TR2819.cor',1,1,'MS4',1331,226765.000,1127.570,2.2,3.5,NULL,558184.757,2212571.349);
INSERT INTO dbase03table VALUES (3,'0507125','CMP','circular','12','','no','Good','','2005-07-12','11:02:43am',3.4,1.5,'Postprocessed Code','GeoXT','2005-07-12','11:03:12am','New','Driveway','050712TR2819.cor',1,1,'MS4',1331,227005.000,1125.364,3.2,1.6,NULL,558703.723,2212562.547);
INSERT INTO dbase03table VALUES (4,'05071210','CMP','circular','15','','no','Good','','2005-07-12','11:15:20am',3.7,2.2,'Postprocessed Code','GeoXT','2005-07-12','11:14:52am','New','Driveway','050712TR2819.cor',1,1,'MS4',1331,227705.000,1118.605,1.8,2.1,NULL,558945.763,2212739.979);
INSERT INTO dbase03table VALUES (5,'05071216','CMP','circular','12','','no','Good','','2005-07-12','12:13:23pm',4.4,1.8,'Postprocessed Code','GeoXT','2005-07-12','12:13:57pm','New','Driveway','050712TR2819.cor',1,1,'MS4',1331,231250.000,1117.390,3.1,1.2,NULL,559024.234,2212856.927);
INSERT INTO dbase03table VALUES (6,'05071217','CMP','circular','12','','no','Good','','2005-07-12','12:16:46pm',4.4,1.8,'Postprocessed Code','GeoXT','2005-07-12','12:17:12pm','New','Driveway','050712TR2819.cor',1,1,'MS4',1331,231445.000,1125.714,3.2,1.3,NULL,559342.534,2213340.161);
INSERT INTO dbase03table VALUES (7,'05071219','CMP','circular','12','','no','Plugged','','2005-07-12','12:22:55pm',4.4,1.8,'Postprocessed Code','GeoXT','2005-07-12','12:22:22pm','New','Driveway','050712TR2819.cor',1,1,'MS4',1331,231755.000,1110.786,2.5,1.1,NULL,559578.776,2213560.247);
INSERT INTO dbase03table VALUES (8,'05071224','CMP','circular','12','','no','Good','','2005-07-12','12:37:17pm',4.1,1.7,'Postprocessed Code','GeoXT','2005-07-12','12:38:32pm','New','Driveway','050712TR2819.cor',1,1,'MS4',1331,232725.000,1077.924,2.8,1.4,NULL,560582.575,2213759.022);
INSERT INTO dbase03table VALUES (9,'05071225','CMP','circular','12','','no','Good','','2005-07-12','12:39:48pm',4.0,1.7,'Postprocessed Code','GeoXT','2005-07-12','12:39:52pm','New','Driveway','050712TR2819.cor',1,1,'MS4',1331,232805.000,1082.990,2.0,1.0,NULL,560678.501,2213716.657);
INSERT INTO dbase03table VALUES (10,'05071229','CMP','circular','12','','no','Good','','2005-07-12','12:49:05pm',3.7,1.7,'Postprocessed Code','GeoXT','2005-07-12','12:49:07pm','New','Driveway','050712TR2819.cor',1,1,'MS4',1331,233360.000,1096.860,2.4,1.2,NULL,560126.094,2213720.301);
INSERT INTO dbase03table VALUES (11,'05071231','CMP','circular','12','','no','Plugged','','2005-07-12','12:53:58pm',3.0,1.6,'Postprocessed Code','GeoXT','2005-07-12','12:54:02pm','New','Driveway','050712TR2819.cor',1,1,'MS4',1331,233655.000,1105.113,1.8,1.1,NULL,559952.331,2213689.001);
INSERT INTO dbase03table VALUES (12,'05071232','CMP','circular','12','','no','Plugged','','2005-07-12','12:55:47pm',3.5,1.7,'Postprocessed Code','GeoXT','2005-07-12','12:55:47pm','New','Driveway','050712TR2819.cor',2,2,'MS4',1331,233760.000,1101.939,2.1,1.1,1.223112,559870.352,2213661.918);
INSERT INTO dbase03table VALUES (13,'05071236','CMP','circular','12','','no','Plugged','','2005-07-12','01:08:40pm',3.3,1.6,'Postprocessed Code','GeoXT','2005-07-12','01:08:42pm','New','Driveway','050712TR2819.cor',1,1,'MS4',1331,234535.000,1125.517,1.8,1.2,NULL,559195.031,2213046.199);

COMMIT;