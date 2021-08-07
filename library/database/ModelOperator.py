import inspect
from typing import Union
from library.database.BaseModel import BaseModel
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
        try: db.query(f"CREATE TYPE {enum_name} AS ENUM ({enum_values});")
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
    
    def get_create_primary_key_sql(self) -> str:
        primary_str = ','.join(self.cls.primary)
        sql = f"ALTER TABLE {self.cls.table} ADD PRIMARY KEY ({primary_str});"
        return sql

    def get_create_table_sql(self) -> str:
        column_sql_list = list(self.get_columns_sql().values())
        directives_str = ', \n   '.join(column_sql_list)
        return (f"""CREATE TABLE {self.cls.table} ( \n   {directives_str} \n); """)

    def get_indexes_sql(self) -> dict[str,str]:
        index_directives: dict[str,str] = {}
        for index in self.cls.indexes:
            index: Index = index
            index_name = index.gen_name(self.cls.table)
            unique_str = "UNIQUE" if index.unique else ""
            index_directive = f"CREATE {unique_str} INDEX {index_name} ON {self.cls.table} ({index.joined()})"
            index_directives[index_name] = index_directive
        return index_directives

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

class ModelOperatorChecks(ModelOperatorSql):
    def primary_key_matches(self) -> bool:
        rows = self.db.get_all(f"""
        SELECT a.attname, format_type(a.atttypid, a.atttypmod) AS data_type
        FROM   pg_index i
        JOIN   pg_attribute a ON a.attrelid = i.indrelid
                            AND a.attnum = ANY(i.indkey)
        WHERE  i.indrelid = '{self.cls.table}'::regclass
        AND    i.indisprimary;
        """)
        column_names: list[str] = [row[0] for row in rows]
        return sorted(column_names) == sorted(self.cls.primary)

    def get_new_indexes(self) -> tuple[set[str],set[str]]:
        rows = self.db.get_all(f"""
        SELECT
            indexname
        FROM pg_indexes
        WHERE schemaname = 'public'
        AND tablename = '{self.cls.table}';
        """)
        existing_indexes: set[str] = set([
            row[0]
            for row in rows
            if row[0][-5:] != "_pkey"
        ])
        now_indexes = set(self.get_indexes_sql().keys())

        drop_indexes = existing_indexes - now_indexes
        create_indexes = now_indexes - existing_indexes

        return (create_indexes,drop_indexes)

    def exists(self):
        table_names = ModelOperatorUtils.existing_tables(db=self.db)
        return self.cls.table in table_names


class ModelTempTableExists(Exception): pass

def print_if_above_0(message: str, check: Union[list,set]) -> bool:
    if len(check) > 0: print(f"{message}",check)
    return len(check) > 0

def confirm(*message: str, default = True) -> bool:
    message_str = ' '.join(message)
    message_str += " (Y/N) "
    
    res = input(message_str).lower()
    if default == True:
        return res not in ["n","no","nope"]
    else:
        return res in ["y","yes","yep"]

class ModelOperator(ModelOperatorChecks):
    def run_migration(self):
        if not self.exists():
            print("Create Table:",self.cls.table)

        has_new_columns = print_if_above_0("New Columns:",self.new_cols)

        has_update_primary_key = True
        if self.exists():
            has_update_primary_key = not self.primary_key_matches()
            if has_update_primary_key: print(f"Primary Key on ({', '.join(self.cls.primary)})")

        create_indexes, drop_indexes = self.get_new_indexes()
        has_create_indexes = print_if_above_0("Create Indexes:",create_indexes)
        has_drop_indexes = print_if_above_0("Drop Indexes:",drop_indexes)

        if not (has_new_columns or has_update_primary_key or has_create_indexes or has_drop_indexes): return

        if not confirm("Create?"): return
        
        if not self.exists():
            self.db.query(self.get_create_table_sql())
            self.db.conn.commit()
            has_update_primary_key = True
        elif len(self.new_cols) > 1:
            self.db.query(self.get_migrate_table_sql())
            self.db.conn.commit()
            create_indexes, drop_indexes = self.get_new_indexes()
            has_update_primary_key = True

        if has_update_primary_key:
            # Add Try/Except
            try: self.db.query(f"ALTER TABLE {self.cls.table} DROP CONSTRAINT {self.cls.table}_pkey")
            except: pass
            self.db.conn.commit()
            self.db.query(self.get_create_primary_key_sql())
            self.db.conn.commit()

        index_commands: list[str] = []
        for index_name in drop_indexes:
            index_commands.append(f"DROP INDEX {index_name}")

        for index_name, index_sql in self.get_indexes_sql().items():
            if index_name in create_indexes:
                index_commands.append(index_sql)

        if len(index_commands) > 0:
            self.db.query(";\n".join(index_commands))
            self.db.conn.commit()

    def migrate(self):
        self.db.query(self.get_migrate_table_sql())
        self.db.conn.commit()

    def drop_temp_table(self):
        # Add Try/Except
        self.db.query(f"DROP TABLE {self.cls.table}_temp")
        self.db.conn.commit()