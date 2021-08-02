from typing import Any, Optional
from core.types.db_types import bigint, numeric, serial,smallint
from core.types.AddressHash import AddressHash,BlockOrTransactionHash
from library.postgres import DB
from contextlib import contextmanager
import inspect

def escape_brackets(s: str):
    return s.replace("{","{{").replace("}","}}")

class ModelOperator:
    mapping = {
        str: "TEXT",
        AddressHash: f"VARCHAR(42) CHECK ({{colname}} ~ '{escape_brackets(AddressHash.regex)}' )",
        BlockOrTransactionHash: f"VARCHAR(66) CHECK ({{colname}} ~ '{escape_brackets(BlockOrTransactionHash.regex)}' )",
        int: "INTEGER",
        numeric: "NUMERIC",
        smallint: "SMALLINT",
        bigint: "BIGINT",
        float: "DECIMAL",
        bool: "BOOLEAN",
        serial: "BIGSERIAL"
    }
    defaults = {
        str: "''",
        AddressHash: "NULL",
        BlockOrTransactionHash: "NULL",
        int: 0,
        numeric: 0,
        smallint: "SMALLINT",
        bigint: "BIGINT",
        float: 0,
        bool: False,
    }

    cols: dict[str,inspect.Parameter]

    def __init__(self, class_to_map: Any) -> None:
        self.cls = class_to_map
        self.cols = dict(inspect.signature(self.cls.__init__).parameters)
        del self.cols["self"]

        with DB() as db:
            # New Cols
            sql = f"""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = {db.placeholder(1)}
            """
            old_cols: list[str] = [row[0] for row in db.get_all(sql,[self.cls.table])]

        self.new_cols = list(set(self.cols) - set(old_cols))
    
    def get_enum (self, opts: list[str]):
        enum_values = ','.join([f"'{opt}'" for opt in opts])
        enum_name = 'enum_' + '_'.join(opts)
        try:
            with DB(auto_commit=True) as db: db.query(f"CREATE TYPE {enum_name} AS ENUM ({enum_values});")
        except Exception: print("Type Exists ",enum_name)
        
        return enum_name

    def attribute_columns(self) -> dict[str,str]:
        strings: dict[str,str] = dict()
        for col, param in self.cols.items():
            
            if hasattr(param.annotation,"enum_opts"):
                col_type = self.get_enum(param.annotation.enum_opts)
            else:
                col_type = self.mapping[param.annotation].format(colname=col)
            
            is_null = param.default is None
            nullable_str = '' if is_null else 'NOT '
            strings[col] = (f"{col} {col_type} {nullable_str} NULL" )
        return strings
    
    def primary_key_syntax(self) -> str:
        return f"PRIMARY KEY({','.join(self.cls.primary)})"

    def create_table_syntax(self, tablename: str = None):
        if tablename is None:
            tablename = self.cls.table

        col_list = list(self.attribute_columns().values()) + [self.primary_key_syntax()]
        cols = ', \n   '.join(col_list)
        return (f"""CREATE TABLE {tablename} ( \n   {cols} \n); """)

    def create_indexes_syntax(self) -> str:
        index_cmd = []
        for index in self.cls.indexes:
            index: Index = index
            unique_str = "UNIQUE" if index.unique else ""
            index_cmd.append(f"CREATE {unique_str} INDEX {index.gen_name(self.cls.table)} ON {self.cls.table} ({index.joined()})")
        return "\n" + '\n'.join(index_cmd)

    def col_string(self):
        return ",".join(self.cols.keys())

    def filled_old_col_string(self):
        return ",".join([
            attr
            if attr not in self.new_cols
                else str(self.defaults[_parameter.annotation])
            for attr,_parameter
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
        if "return" in cls.keys: cls.keys.remove("return") 

    def __call__(cls, *args, **kwargs):
        self = super().__call__(**kwargs)
        for key,_class in cls.__init__.__annotations__.items():
            if key == "return":
                continue
            val = None if kwargs[key] is None else _class(kwargs[key])
            setattr(self,key,val)
        cls.__init__(self,**kwargs)
        return self

class Index:
    def __init__(self,
        *,
        cols: list[str],
        unique: bool = False
    ):
        self.cols = cols
        self.unique = unique

    def gen_name(self, table: str):
        return f"idx_gener_{table}_" + "_".join(self.cols)

    def joined(self):
        return ','.join(self.cols)

# abstract
class BaseModel(metaclass=BaseModelMetaClass):
    table: str    
    primary: list[str] = []

    indexes: list[Index] = []

    __model_operator = None

    keys: list[str]

    @classmethod
    def _from_row(cls,row):
        obj = cls(**{key:row[i] for i,key in enumerate(cls.keys)})
        return obj

    def dict(self):
        return {key:getattr(self,key) for key in self.keys}

    @staticmethod
    def limit_cond(limit: Optional[int]):
        """
        Also does offset if tuple/list is passed in
        """
        limit_cond = ""
        if limit is not None:
            if isinstance(limit,(tuple,list)):
                limit_cond = f"LIMIT {int(limit[0])} OFFSET {int(limit[1])}"
            else:
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
        return cls._mo().create_table_syntax() + cls._mo().create_indexes_syntax()

    @classmethod
    def _db_recreate(cls):
        return cls._mo().recreate_syntax() + cls._mo().create_indexes_syntax()

    @classmethod
    def _db_new_cols(cls):
        return cls._mo().new_cols

    @staticmethod
    @contextmanager
    def with_db(db: Optional[DB] = None, commit: bool = False):
        _db = db if db is not None else DB()
        yield _db
        if db is None:
            _db.close()
        elif commit:
            _db.conn.commit()