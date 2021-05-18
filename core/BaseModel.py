from core.Address import Address
from library.postgres import DB

class ModelOperator:
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
        return {
            attr:(f"{attr} {self.mapping[_type]} NOT NULL" )
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
            attr if attr not in self.new_cols else self.defaults[_class]
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
        if str(bases[0]) != "<class 'core.BaseModel.BaseModel'>":
            return None

        cls.keys = list(cls.__init__.__annotations__.keys())
        cls.keys.remove("return") 

    def __call__(self, *args, **kwargs):
        for key,_class in self.__init__.__annotations__.items():
            if key == "return":
                continue
            setattr(self,key,_class(kwargs[key]))
        return super().__call__(**kwargs)

# abstract
class BaseModel(metaclass=BaseModelMetaClass):
    table = None
    primary = []

    __model_operator = None

    def dict(self):
        return {key:getattr(self,key) for key in self.keys}

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