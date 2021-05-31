from library.postgres import DB

db = DB("tokens")
db.query("UPDATE listings SET token=LOWER(token)")
db.query("UPDATE token_requests SET address=LOWER(address)")
db.query("UPDATE holders SET contract=LOWER(contract)")
db.query("UPDATE tokens SET address=LOWER(address)")

db.conn.commit()