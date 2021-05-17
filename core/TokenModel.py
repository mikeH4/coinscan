from core.Address import Address
from library.postgres import DB

class TokenModel:
    mapping = {
        str: "TEXT",
        Address: "VARCHAR(42)",
        int: "INTEGER",
        float: "FLOAT",
        bool: "BOOLEAN"
    }
    defaults = {
        str: "''",
        Address: None,
        int: 0,
        float: 0,
        bool: False
    }

    def __init__(self, class_to_map) -> None:
        self.cls = class_to_map
        self.cols = dict(self.cls.__init__.__annotations__)
        del self.cols["return"]

        with DB("tokens") as db:
            # New Cols
            sql = f"""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = {db.placeholder(1)}
            """
            old_cols = [row[0] for row in db.get_all(sql,[self.cls.table])]

        self.new_cols = list(set(self.cols) - set(old_cols))

    def attribute_columns(self) -> dict:
        primary = self.cls.primary
        return {
            attr:(f"{attr} {self.mapping[_type]} NOT NULL" + (" PRIMARY KEY" if attr in primary else ""))
            for attr,_type
            in self.cols.items()
        }

    def create_table_syntax(self,tablename:str = None):
        if tablename is None:
            tablename = self.cls.table
        cols = ', \n   '.join(self.attribute_columns().values())
        return (f"""CREATE TABLE {tablename} ( \n   {cols} \n); """)

    def col_string(self):
        return ",".join(self.cols.keys())

    def filled_old_col_string(self):
        return ",".join([
            attr if attr not in self.new_cols else self.defaults[_class]
            for attr,_class
            in self.cols.items()
        ])
    
    def recreate(self):
        tbl = self.cls.table
        syntax = f"""
        ALTER TABLE {tbl} RENAME TO {tbl}_temp;
        {self.create_table_syntax(tbl)};
        INSERT INTO {tbl} ({self.col_string()}) SELECT {self.filled_old_col_string()} FROM {tbl}_temp;
        """
        return syntax