# CREATE TABLE merp (
# 	id        SERIAL PRIMARY KEY,
# 	chrono    DATERANGE NOT NULL,
# 	person_id INT NOT NULL
# 	--, EXCLUDE USING gist (chrono WITH &&, person_id WITH =)
# );
#
# DROP INDEX idx_merp_test; CREATE INDEX idx_merp_test ON merp (person_id);
# DROP INDEX idx_merp_test; CREATE INDEX idx_merp_test ON merp USING gist (chrono, person_id);
#
# INSERT INTO merp (chrono, person_id)
# SELECT DATERANGE(concat_ws('/', y, m, 1)::date,concat_ws('/', y, m+1, 1)::date), id
# FROM generate_series(1,10000,1) AS id
# JOIN generate_series(2008,2020,1) AS y ON true
# JOIN generate_series(1,12,4) AS m ON true;
#
# SELECT relation::regclass AS relname, * FROM pg_locks ORDER BY pid, relname, mode;

import contextlib
import textwrap
import time

from prettytable import PrettyTable
from sqlalchemy import create_engine
from sqlalchemy.sql.expression import text

CHRONO = "[2000/1/1,2100/1/1)"
TBL = "merp"

eng = create_engine("postgresql+psycopg2://localhost:55432/benzene",
	isolation_level="SERIALIZABLE")

class Tx:
	def __init__(self, name, pers, tx, echo=True):
		self.name = name
		self.pers = pers
		self.tx = tx
		self.echo = echo

	def exec(self, q, *args, **kws):
		res = self.tx.execute(text(q), *args, **kws)
		if not self.echo:
			res.close()
			return

		print(self.name, q)

		if not res.returns_rows:
			return

		t = PrettyTable(res.keys())
		for row in res:
			t.add_row(row)
		print(textwrap.indent(str(t), "\t"))

	def select(self):
		with runtime():
			self.exec("SELECT * FROM " + TBL +" WHERE person_id=:pers AND chrono && :chrono",
				pers=self.pers,
				chrono=CHRONO)

	def insert(self):
		self.exec("INSERT INTO " + TBL + " (person_id, chrono) VALUES (:pers, :chrono)",
			pers=self.pers,
			chrono="[2100/1/1,2101/1/1)")

@contextlib.contextmanager
def runtime(name=None):  # pragma: no cover
    start = time.monotonic()
    yield
    print('{}: {}'.format(
        name if name else 'runtime',
        time.monotonic() - start))

@contextlib.contextmanager
def begin(name, pers, echo=False):
	with eng.begin() as tx:
		yield Tx(name, pers, tx, echo=echo)

def clean():
	with begin("t0", 0, echo=False) as tx, runtime("clean"):
		tx.exec("DELETE FROM " + TBL + " WHERE chrono << :chrono OR chrono >> :chrono",
			chrono=CHRONO)

def read_first():
	with begin("t0", 1) as t0, begin("t1", 10000) as t1:
		t0.select()
		t1.select()

		t0.insert()
		t1.insert()

def interleaving():
	with begin("t0", 1) as t0:
		t0.select()
		t0.insert()

		with begin("t1", 10000) as t1:
			t1.select()
			t1.insert()

def sequential():
	with begin("t0", 1) as t0, begin("t1", 10000) as t1:
		t0.select()
		t0.insert()

		t1.select()
		t1.insert()

def readonly_before():
	with begin("t0", 1) as t0:
		t0.select()

		with begin("t1", 10000) as t1:
			t1.select()

		t0.insert()

def readonly_after():
	with begin("t0", 1) as t0:
		t0.select()
		t0.insert()

		with begin("t1", 10000) as t1:
			t1.select()

funcs = [
	read_first,
	interleaving,
	sequential,
	readonly_before,
	readonly_after,
]

for fn in funcs:
	print(fn.__name__, "###################")
	try:
		clean()
		fn()
	except Exception as e:
		print("failed: " + textwrap.indent("\n" + str(e), "\t"))
	else:
		print("ok")

	print()
