import inspect
from typing import Optional
from library.database.Index import Index
from library.database.postgres import DB
from contextlib import contextmanager

class BaseModelMetaClass(type):
    def __init__(cls, name, bases, namespace, **kwargs):
        if len(bases) < 1:
            return None
        if str(bases[0]) != "<class 'library.BaseModel.BaseModel'>":
            return None

        params = dict(inspect.signature(cls.__init__).parameters)
        del params["self"]
        cls.keys = list(params.keys())

    def __call__(cls, *args, **kwargs):
        self = super().__call__(**kwargs)
        for name, param in inspect.signature(cls.__init__).parameters.items():
            if name == "self": continue
            _class = param.annotation
            if name not in kwargs and not isinstance(param.default,inspect._empty): # type: ignore
                val = param.default
            else:
                val = None if kwargs[name] is None else _class(kwargs[name])
            setattr(self, name, val)
        cls.__init__(self,**kwargs)
        return self

# abstract
class BaseModel(metaclass=BaseModelMetaClass):
    table: str    
    primary: list[str] = []
    indexes: list[Index] = []

    keys: list[str]

    @classmethod
    def _from_row(cls,row):
        obj = cls(**{key:row[i] for i,key in enumerate(cls.keys)})
        return obj

    def dict(self):
        return {key:getattr(self,key) for key in self.keys}

    @staticmethod
    def limit_cond(limit: Optional[int]):
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

    @staticmethod
    @contextmanager
    def with_db(db: Optional[DB] = None, commit: bool = False):
        _db = db if db is not None else DB()
        yield _db
        if db is None:
            _db.close()
        elif commit:
            _db.conn.commit()