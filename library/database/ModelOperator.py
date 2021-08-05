from library.database.BaseModel import BaseModel
from typing import Any
import inspect
from library.database.postgres import DB
from library.database.Index import Index
from library.database.mappings import (
    postgres_defaults,
    postgres_types
)

class ModelOperatorUtils:
    @staticmethod
    def get_enum_name (opts: list[str], *, db: DB):
        enum_values = ','.join([f"'{opt}'" for opt in opts])
        enum_name = 'enum_' + '_'.join(opts)
        try:
            with DB(auto_commit=True) as db: db.query(f"CREATE TYPE {enum_name} AS ENUM ({enum_values});")
        except Exception: print("Type Exists ",enum_name)
        
        return enum_name
    
    _table_names: list[str]
    @classmethod
    def existing_tables(cls, *, db: DB) -> list[str]:
        if hasattr(cls,"_table_names"): return getattr(cls,"_table_names")
        
        rows = db.get_all("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
        """)
        cls._table_names: list[str] = [row[0] for row in rows]
        return cls._table_names

class ModelOperatorSql:
    cls: BaseModel
    parameters: dict[str,inspect.Parameter]
    new_cols: list[str]
    db: DB

    def __init__(self, class_to_map: BaseModel, *, db: DB) -> None:
        self.db = db

        self.cls = class_to_map
        self.parameters = dict(inspect.signature(self.cls.__init__).parameters)
        del self.parameters["self"]

        # New Cols
        sql = f"""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = {db.placeholder(1)}
        """
        old_column_names: list[str] = [
            row[0]
            for row
            in db.get_all(sql,[self.cls.table])
        ]

        self.new_cols: list[str] = list(set(self.parameters.keys()) - set(old_column_names))

    def get_columns_sql(self) -> dict[str,str]:
        columns_sql: dict[str,str] = dict()
        for column_name, parameter in self.parameters.items():
            if hasattr(parameter.annotation,"enum_opts"):
                col_type = ModelOperatorUtils.get_enum_name(
                    parameter.annotation.enum_opts,
                    db=self.db
                )
            else:
                col_type = postgres_types[parameter.annotation].format(colname=column_name)
            
            is_null = parameter.default is None
            nullable_str = '' if is_null else 'NOT '
            columns_sql[column_name] = (f"{column_name} {col_type} {nullable_str} NULL" )
        
        return columns_sql
    
    def get_primary_key_sql(self) -> str:
        return f"PRIMARY KEY({','.join(self.cls.primary)})"

    def get_create_table_sql(self) -> str:
        column_sql_list = list(self.get_columns_sql().values())
        sql_directives = column_sql_list + [self.get_primary_key_sql()]
        directives_str = ', \n   '.join(sql_directives)
        return (f"""CREATE TABLE {self.cls.table} ( \n   {directives_str} \n); """)

    def get_indexes_sql(self) -> str:
        index_directives = []
        for index in self.cls.indexes:
            index: Index = index
            index_name = index.gen_name(self.cls.table)
            unique_str = "UNIQUE" if index.unique else ""
            index_directive = f"CREATE {unique_str} INDEX {index_name} ON {self.cls.table} ({index.joined()})"
            index_directives.append(index_directive)
        return "\n" + '\n'.join(index_directives)

    def get_column_names_string(self) -> str:
        return ",".join(self.parameters.keys())

    def get_new_columns_with_defaults_string(self) -> str:
        return ",".join([
            attr
            if attr not in self.new_cols
                else str(postgres_defaults[_parameter.annotation])
            for attr,_parameter
                in self.parameters.items()
        ])
    
    def get_migrate_table_sql(self):
        table = self.cls.table
        column_names = self.get_column_names_string()
        new_columns = self.get_new_columns_with_defaults_string()
        syntax = f"""
        ALTER TABLE {table} RENAME TO {table}_temp;
        {self.get_create_table_sql()};
        INSERT INTO {table} ({column_names}) SELECT {new_columns} FROM {self.cls.table}_temp;
        """
        return syntax

class ModelOperator(ModelOperatorSql):
    def exists(self):
        table_names = ModelOperatorUtils.existing_tables(db=self.db)
        return self.cls.table in table_names
    
    def needs_migration(self):
        return len(self.new_cols) > 0

    def create(self):
        self.db.query(self.get_create_table_sql())
        self.db.conn.commit()

    def migrate(self):
        self.db.query(self.get_migrate_table_sql())
        self.db.conn.commit()

    def drop_temp(self):
        self.db.query(f"DROP TABLE {self.cls.table}_temp")
        self.db.conn.commit()