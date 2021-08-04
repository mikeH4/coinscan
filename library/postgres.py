from typing import Optional
import psycopg2
from psycopg2.pool import ThreadedConnectionPool
import settings
from signal import *
import atexit

class PostgresDBException(Exception):
    pgcode: str
    pgerror: str

class DB:
    _pools:dict[str,ThreadedConnectionPool] = dict( # type: ignore
        blockchain= None,
        tokens= None,
    )
    _initialized: bool = False

    @classmethod
    def initialize(cls):
        if cls._initialized: raise PostgresDBException("Initialize Called")
        cls._initialized = True

        for dbname in cls._pools.keys():
            connsettings = dict()
            if settings.sandbox != True:
                connsettings.update(
                    user="coinscan",
                    password="root"
                )
        
            cls._pools[dbname] = ThreadedConnectionPool(
                host="localhost",
                database=dbname,
                minconn=1,
                maxconn=120,
                **connsettings
            )
        # DB._register_cleanup()

    # To keep track of open clients, and shut them down
    __active = []

    @staticmethod
    def placeholder(l: int):
        return ",".join(['%s'] * l )

    def __init__(self, dbname: str = "blockchain", auto_commit: bool = True):
        self.auto_commit = auto_commit
        
        if dbname not in self._pools.keys():
            raise PostgresDBException(f"{dbname} is not one of {','.join(self._pools.keys())}")
        DB.__active.append(self)
	
        print(f"Using Pool {dbname}, Active: {len(DB.__active)}")

        self.pool = self._pools[dbname]
        self.conn = self.pool.getconn()
        self.cursor = self.conn.cursor()

    def close(self):
        DB.__active.remove(self)
        
        if self.auto_commit: self.conn.commit()
        self.cursor.close()
        self.conn.close()
        self.pool.putconn(self.conn)

    def __enter__(self):
        return self

    def __exit__(self,exc_type,exc_value,traceback):
        self.close()

    def insert(self,
        table,
        data: dict[str,str],
        commit: bool = False,
        ignore_insert: bool = False,
        replace_insert_on: list[str] = None,
        dont_update = []
    ):
        cols = list(data.keys())
        cols_str = ",".join(data.keys())
        placeholder = self.placeholder(len(data))
        
        sql = f"INSERT INTO {table} ({cols_str}) VALUES ({placeholder})"
                
        if replace_insert_on is not None:
            for replace_col in replace_insert_on:
                if replace_col not in cols:
                    raise PostgresDBException("replace_insert_on must be of columns inserted")
            update_str = ", ".join([
                (f"{key} = excluded.{key}")
                for key in cols
                if key not in replace_insert_on and key not in dont_update
            ])
            do_conflict = f"UPDATE SET {update_str}"
            sql += f"""
            ON CONFLICT ({', '.join(replace_insert_on)}) DO
            {do_conflict};
            """
        elif ignore_insert:
            sql += "ON CONFLICT DO NOTHING"
    
        self.query(sql,list(data.values()))
        
        if commit:
            self.conn.commit()

            return self.cursor.lastrowid

    def get(self, sql: str, queries: list = []) -> Optional[tuple]:
        self.query(sql, queries)
        return self.cursor.fetchone()

    def get_all(self, sql: str, queries:list = []) -> list[tuple]:
        self.query(sql, queries)
        return self.cursor.fetchall()

    def query(self,sql: str,queries:list = []) -> Optional[tuple]:
        try:
            a = self.cursor.execute(sql, list( queries ) )
        except psycopg2.Error as error:
            e = PostgresDBException("\n" + sql + "\n" + str(error))
            e.pgcode = error.pgcode
            e.pgerror = error.pgerror
            raise e

    def rollback(self):
        self.query("ROLLBACK;")

    @staticmethod
    def _register_cleanup():
        def clean(*args):
            for db in DB.__active:
                db.close()
            for dbname in DB._pools.keys():
                DB._pools[dbname].closeall()
            raise SystemExit(0)

        atexit.register(clean)
        for sig in (SIGABRT, SIGILL, SIGINT, SIGTERM):
            signal(sig, clean)

DB.initialize()