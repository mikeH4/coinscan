
from library.postgres import DB

db = DB("tokens")

burnt_address = "0x0000000000000000000000000000000000000000"
dead_address =  "0x000000000000000000000000000000000000dead"

burnt_contracts = [row[0] for row in db.get_all(f"SELECT contract FROM holders WHERE holder = '{burnt_address}'")]
dead_contracts = [  row[0] for row in db.get_all(f"SELECT contract FROM holders WHERE holder = '{dead_address}'")]

intersection = set(burnt_contracts).intersection(set(dead_contracts))

for addr in list(intersection):
    burned = int(db.get(f"SELECT holding FROM holders WHERE contract = '{addr}' AND holder = '{burnt_address}'")[0])
    deaded = int(db.get(f"SELECT holding FROM holders WHERE contract = '{addr}' AND holder = '{dead_address}'")[0])
    total = burned+deaded

    print(addr,total)
    db.query(f"DELETE FROM holders WHERE contract = '{addr}' AND holder = '{dead_address}'")
    db.query(f"UPDATE holders SET holding = {total} WHERE contract = '{addr}' AND holder = '{burnt_address}'")

db.query(f"UPDATE holders SET holder = '{burnt_address}' WHERE holder = '{dead_address}'")

db.conn.commit()