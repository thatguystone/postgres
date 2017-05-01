-- DROP TABLE IF EXISTS merp CASCADE;
-- CREATE EXTENSION IF NOT EXISTS btree_gist;

-- CREATE TABLE merp (
-- 	id        SERIAL,
-- 	chrono    DATERANGE NOT NULL,
-- 	person_id INT NOT NULL
-- ) PARTITION BY LIST ((person_id % 5));

-- CREATE TABLE merp_0 PARTITION OF merp (
-- 	id      PRIMARY KEY,
-- 	EXCLUDE USING gist (chrono WITH &&, person_id WITH =)
-- ) FOR VALUES IN (0);

-- CREATE TABLE merp_1 PARTITION OF merp (
-- 	id      PRIMARY KEY,
-- 	EXCLUDE USING gist (chrono WITH &&, person_id WITH =)
-- ) FOR VALUES IN (1);

-- CREATE TABLE merp_2 PARTITION OF merp (
-- 	id      PRIMARY KEY,
-- 	EXCLUDE USING gist (chrono WITH &&, person_id WITH =)
-- ) FOR VALUES IN (2);

-- CREATE TABLE merp_3 PARTITION OF merp (
-- 	id      PRIMARY KEY,
-- 	EXCLUDE USING gist (chrono WITH &&, person_id WITH =)
-- ) FOR VALUES IN (3);

-- CREATE TABLE merp_4 PARTITION OF merp (
-- 	id      PRIMARY KEY,
-- 	EXCLUDE USING gist (chrono WITH &&, person_id WITH =)
-- ) FOR VALUES IN (4);

-- INSERT INTO merp (chrono, person_id)
-- SELECT DATERANGE(concat_ws('/', y, m, 1)::date,concat_ws('/', y, m+1, 1)::date), id
-- FROM generate_series(1,4,1) AS id
-- JOIN generate_series(2008,2020,1) AS y ON true
-- JOIN generate_series(1,12,4) AS m ON true;

-- vacuum analyze;
-- set enable_seqscan to off;

EXPLAIN ANALYZE SELECT * FROM merp WHERE person_id=2;
-- EXPLAIN ANALYZE SELECT * FROM merp_2 WHERE person_id=2;
