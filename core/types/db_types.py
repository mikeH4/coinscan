class numeric(float): pass

class smallint(int): pass

class bigint(int): pass

class serial(int): pass

def enum(*opts: str):
    joined = ', '.join(opts)
    class enum_class(str):
        enum_opts: tuple[str] = opts # type: ignore
        def __new__(cls, string: str):
            if string not in opts:
                raise TypeError(f"Not one of {joined}")
            return super(enum_class, cls).__new__(cls, string)
    return enum_class

PlatformsEnum = enum("coinmarketcap","coingecko")
ChainEnum = enum("bsc","eth")
ChainEnum.enum_opts = ("bsc",)
AddressTypeEnum = enum("token","pair","wa")