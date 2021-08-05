from core.types.db_types import bigint, numeric, serial, smallint
from core.types.AddressHash import AddressHash, BlockOrTransactionHash

def escape_brackets(s: str): return s.replace("{","{{").replace("}","}}")

postgres_types = {
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
postgres_defaults = {
    str: "''",
    AddressHash: "NULL",
    BlockOrTransactionHash: "NULL",
    int: 0,
    numeric: 0,
    smallint: 0,
    bigint: 0,
    float: 0,
    bool: False,
}
py_defaults = {
    str: "",
    AddressHash: None,
    BlockOrTransactionHash: None,
    int: 0,
    numeric: 0,
    smallint: 0,
    bigint: 0,
    float: 0,
    bool: False,
}