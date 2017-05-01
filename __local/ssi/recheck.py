import contextlib
import textwrap
import time

from prettytable import PrettyTable
from sqlalchemy import create_engine
from sqlalchemy.sql.expression import text

eng = create_engine("postgresql+psycopg2://benzene@172.30.64.2/benzene",
	isolation_level="SERIALIZABLE")

class Tx:
	def __init__(self, name, tx, echo=True):
		self.name = name
		self.tx = tx
		self.echo = echo

	def exec(self, q, *args, **kws):
		res = self.tx.execute(text(q), *args, **kws)
		if not self.echo:
			res.close()
			return

		print(self.name, q)

		if not res.returns_rows:
			res.close()
			return

		t = PrettyTable(res.keys())
		for row in res:
			t.add_row(row)
		print(textwrap.indent(str(t), "\t"))

	def commit(self):
		self.tx.connection.commit()

@contextlib.contextmanager
def runtime(name=None):
    start = time.monotonic()
    yield
    print('{}: {}'.format(
        name if name else 'runtime',
        time.monotonic() - start))

@contextlib.contextmanager
def begin(name, echo=True):
	with eng.begin() as tx:
		yield Tx(name, tx, echo=echo)

with begin("clean", echo=False) as tx:
	tx.exec("UPDATE scds SET what=1 WHERE thing=1000")
	tx.exec("UPDATE enrolls SET what=1, recheck=false WHERE thing=1000")

t0 = Tx("t0", eng.begin().conn)
t1 = Tx("t1", eng.begin().conn)

t0.exec("SELECT * FROM scds WHERE thing=1000")
t0.exec("UPDATE scds SET what=10 WHERE thing=1000")
t0.exec("UPDATE enrolls SET recheck=true WHERE thing=1000")

t1.exec("SELECT * FROM scds WHERE thing=1000")
t1.exec("SELECT * FROM enrolls WHERE thing=1000")
t1.exec("UPDATE enrolls SET recheck=false WHERE thing=1000")
t0.commit()
t1.commit()
