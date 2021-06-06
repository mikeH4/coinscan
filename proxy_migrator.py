from time import time
from library.postgres import DB

from library.Proxies import Proxies

with DB("tokens") as db:
    # Check to ensure script has not been run already
    try:
        db.get("SELECT * FROM migrator6_proxies LIMIT 1")
        print("Table exists: Exiting")
        exit(0)
    except Exception as e:
        db.rollback()

    query = db.query("""
    ALTER TABLE proxies RENAME TO migrator6_proxies
    """)
    db.conn.commit()

    for _class in [Proxies]:
        print(_class)
        db.query(_class._db_create())
    
    db.conn.commit()

    rows = db.get_all("SELECT * FROM migrator6_proxies")
    for row in rows:
        ip,agent,apikey,status,task,added = row
        ip,port = ip.split(":")
        Proxies(
            ip=ip,
            port=port,
            agent=agent,
            added=added,
            bscscan_apikey=apikey,
            cmc_apikey="",
        ).insert(db=db)

    Proxies(
        ip="",
        port=0,
        agent=Proxies.random_agent(),
        added=time(),
        bscscan_apikey="",
        cmc_apikey=""
    ).insert(db=db)

    db.conn.commit()