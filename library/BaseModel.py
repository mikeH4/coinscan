from core.types.db_types import numeric
from core.types.Address import Address,BlockOrTransactionHash
from library.postgres import DB
from contextlib import contextmanager

class ModelOperator:
    mapping = {
        str: "TEXT",
        Address: "VARCHAR(42)",
        BlockOrTransactionHash: "VARCHAR(66)",
        int: "INTEGER",
        numeric: "NUMERIC",
        float: "DECIMAL",
        bool: "BOOLEAN"
    }
    defaults = {
        str: "''",
        Address: "NULL",
        BlockOrTransactionHash: "NULL",
        int: 0,
        numeric: 0,
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
        return {
            attr:(f"{attr} {self.mapping[_type]} {'' if attr in self.cls.null_cols else 'NOT '} NULL" )
            for attr,_type
            in self.cols.items()
        }
    
    def primary_key_syntax(self) -> str:
        return [f"PRIMARY KEY({','.join(self.cls.primary)})"]

    def create_table_syntax(self,tablename:str = None):
        if tablename is None:
            tablename = self.cls.table

        col_list = list(self.attribute_columns().values()) + self.primary_key_syntax()
        cols = ', \n   '.join(col_list)
        return (f"""CREATE TABLE {tablename} ( \n   {cols} \n); """)

    def col_string(self):
        return ",".join(self.cols.keys())

    def filled_old_col_string(self):
        return ",".join([
            attr if attr not in self.new_cols else str(self.defaults[_class])
            for attr,_class
            in self.cols.items()
        ])
    
    def recreate_syntax(self):
        tbl = self.cls.table
        syntax = f"""
        ALTER TABLE {tbl} RENAME TO {tbl}_temp;
        {self.create_table_syntax(tbl)};
        INSERT INTO {tbl} ({self.col_string()}) SELECT {self.filled_old_col_string()} FROM {tbl}_temp;
        """
        return syntax

class BaseModelMetaClass(type):
    def __init__(cls, name, bases, namespace, **kwargs):
        if len(bases) < 1:
            return None
        if str(bases[0]) != "<class 'library.BaseModel.BaseModel'>":
            return None

        cls.keys = list(cls.__init__.__annotations__.keys())
        cls.keys.remove("return") 

    def __call__(cls, *args, **kwargs):
        self = super().__call__(**kwargs)
        for key,_class in cls.__init__.__annotations__.items():
            if key == "return":
                continue
            val = None if kwargs[key] is None else _class(kwargs[key])
            setattr(self,key,val)
        return self

# abstract
class BaseModel(metaclass=BaseModelMetaClass):
    table = None
    primary = []
    null_cols = []

    __model_operator = None

    @classmethod
    def _from_row(cls,row):
        obj = cls(**{key:row[i] for i,key in enumerate(cls.keys)})
        return obj

    def dict(self):
        return {key:getattr(self,key) for key in self.keys}

    @staticmethod
    def limit_cond(limit):
        limit_cond = ""
        if limit is not None:
            limit_cond = f"LIMIT {int(limit)}"
        return limit_cond
    
    @staticmethod
    def before_cond(before,timestamp_key = "updated"):
        before_cond = ""
        if before is not None:
            before_cond = f" WHERE {timestamp_key} < {int(before)}"
        return before_cond

    @classmethod
    def _mo(cls):
        if cls.__model_operator is None:
            cls.__model_operator = ModelOperator(cls)
        return cls.__model_operator
    @classmethod
    def _db_create(cls):
        return cls._mo().create_table_syntax()

    @classmethod
    def _db_recreate(cls):
        return cls._mo().recreate_syntax()

    @classmethod
    def _db_new_cols(cls):
        return cls._mo().new_cols

    @staticmethod
    @contextmanager
    def with_db(db=None):
        _db = db if db is not None else DB("tokens")
        yield _db
        if db is None:
            _db.close()