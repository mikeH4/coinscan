import sqlite3

class DB:
    @staticmethod
    def placeholder(l: list):
        return ",".join(['?'] * l )

    def __init__(self, name=None):
        
        self.conn = None
        self.cursor = None

        if name:
            self.open(name)

    def open(self,name):
        
        try:
            self.conn = sqlite3.connect(name)
            self.cursor = self.conn.cursor()

        except sqlite3.Error as e:
            print("Error connecting to database!")

    def close(self):
        
        if self.conn:
            self.conn.commit()
            self.cursor.close()
            self.conn.close()

    def __enter__(self):
        
        return self

    def __exit__(self,exc_type,exc_value,traceback):
        
        self.close()
      
    def insert(self,table,data, commit: bool = True, ignore_insert=False):
        cols = ",".join(data.keys())
        placeholder = self.placeholder(len(data))
        
        or_ignore = ""
        if ignore_insert:
            or_ignore = "OR IGNORE"
        sql = f"INSERT {or_ignore} INTO {table} ({cols}) VALUES ({placeholder})"
                
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
