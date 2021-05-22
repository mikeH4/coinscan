from core.Address import Address
from core.Token import Token
from library.postgres import DB
from core.TokenRequest import TokenRequest
from time import time

db = DB("tokens")

ls = db.get("SELECT ip FROM proxies WHERE task = ''")

db.query("""
UPDATE proxies
SET task = 'rescanner'
WHERE task = ''
""")
if ls is not None:
    db.query("""
    UPDATE proxies
    SET task = 'request'
    WHERE ip = %s
    """,[ls[0]])


db.conn.commit()

TokenRequest(
    address=Address("0x27Ae27110350B98d564b9A3eeD31bAeBc82d878d"),
    request_time=time()
).insert_or_update()