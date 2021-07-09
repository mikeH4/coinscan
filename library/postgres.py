import psycopg2
from psycopg2.pool import ThreadedConnectionPool
import settings
from signal import *

class DB:
    _pool = None
    _database = None
    _connsettings = None

    @classmethod
    def initialize(cls, database: str):
        if cls._database is not None: raise Exception("Initialize Called")
        cls._database = database

        cls._connsettings = dict(
            host="localhost",
            database=database,
        )
        if settings.sandbox != True:
            cls._connsettings.update(
                user="coinscan",
                password="root"
            )
        
        # cls._pool = ThreadedConnectionPool(
        #     minconn=1,
        #     maxconn=15,
        #     **cls._connsettings
        # )

    # To keep track of open clients, and shut them down
    __active = []

    @staticmethod
    def placeholder(l: int):
        return ",".join(['%s'] * l )

    def __init__(self, auto_commit=True):
        self.conn = None
        self.cursor = None
        self.auto_commit = auto_commit

        self.open()
    
    def open(self):
        DB.__active.append(self)
	
        print(self._connsettings)
        self.conn = psycopg2.connect(**self._connsettings)
        self.cursor = self.conn.cursor()

    def close(self):
        DB.__active.remove(self)
        
        if self.conn:
            if self.auto_commit: self.conn.commit()
            self.cursor.close()
            self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self,exc_type,exc_value,traceback):
        self.close()

    def insert(self,
        table,
        data,
        commit: bool = True,
        ignore_insert=False,
        replace_insert_on:list = False,
        dont_update = []
    ):
        cols = list(data.keys())
        cols_str = ",".join(data.keys())
        placeholder = self.placeholder(len(data))
        
        sql = f"INSERT INTO {table} ({cols_str}) VALUES ({placeholder})"
                
        if replace_insert_on:
            for replace_col in replace_insert_on:
                if replace_col not in cols:
                    raise Exception("replace_insert_on must be of columns inserted")
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
    
        self.query(sql,data.values())
        
        if commit:
            self.conn.commit()

            return self.cursor.lastrowid

    def get(self,sql: str,queries:list = []):
        self.query(sql, queries)
        return self.cursor.fetchone()

    def get_all(self,sql: str,queries:list = []):
        self.query(sql, queries)
        return self.cursor.fetchall()

    def query(self,sql: str,queries:list = []):
        try:
            a = self.cursor.execute(sql, list( queries ) )
        except Exception as error:
            raise Exception("\n" + sql + "\n" + str(error))

    def rollback(self):
        self.query("ROLLBACK;")

    @staticmethod
    def _register_cleanup():
        def clean(*args):
            for db in DB.__active:
                db.close()
            raise SystemExit(0)

        for sig in (SIGABRT, SIGILL, SIGINT, SIGTERM):
            signal(sig, clean)

DB.initialize("tokens")