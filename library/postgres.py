import psycopg2
import settings

class DB:
    @staticmethod
    def placeholder(l: int):
        return ",".join(['%s'] * l )

    def __init__(self, database=None):
        
        self.conn = None
        self.cursor = None

        if database:
            self.open(database)
    
    def open(self,database):
	
        self.database = database
	
        
        additional_args = {}
        if settings.sandbox != True:
            additional_args = dict(
                user="coinscan",
                password="root"
            )
        self.conn = psycopg2.connect(
            host="localhost",
            database = database,
            **additional_args
        )

        self.cursor = self.conn.cursor()

    def close(self):
        
        if self.conn:
            self.conn.commit()
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
        replace_insert_on:list = False
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
                if key not in replace_insert_on
            ])
            do_conflict = "NOTHING" if ignore_insert else f"UPDATE SET {update_str}"
            sql += f"""
            ON CONFLICT ({', '.join(replace_insert_on)}) DO
            {do_conflict};
            """
    
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

class CreateSQLTables:

    def __init__(self, name):
        self.cmds = []
        self.name = name
    
    def __add__(self,to_add):
        self.cmds.append(to_add)
        return self
    
    def execute(self):
        db = DB(self.name)
        for cmd in self.cmds:
            db.query(cmd)
        db.close()
        return True