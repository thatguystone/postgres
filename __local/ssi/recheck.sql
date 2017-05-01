DROP TABLE IF EXISTS scds;
CREATE TABLE scds (
	id    SERIAL PRIMARY KEY,
	thing INT,
	what  INT
);

DROP TABLE IF EXISTS enrolls;
CREATE TABLE enrolls (
	id      SERIAL PRIMARY KEY,
	thing   INT,
	what    INT,
	recheck BOOL
);

INSERT INTO scds (thing, what)
	SELECT thing, what
		FROM generate_series(1,100000) AS thing
		CROSS JOIN generate_series(1,10) AS what;

INSERT INTO enrolls (thing, what, recheck)
	SELECT thing, what, what % 2 = 1
	FROM scds;

CREATE INDEX ON scds (thing);
CREATE INDEX ON enrolls (thing);
