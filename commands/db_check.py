warnings = []

# All are just to alert us, since as of the time of this script being written, since they should be bug-free

# token_meta has a row for non existent address
# This is happening still, best guess is autocommit on restart service,
# coincides with low (1-2) count
# Will monitor to see if happens without restarting often

# FIX: Wrap in delete query and delete all
# DELETE FROM token_meta WHERE address IN (...query...)
warnings += ["""
SELECT token_meta.address FROM token_meta
LEFT JOIN tokens ON LOWER(tokens.address) = LOWER(token_meta.address)
LEFT JOIN pairs AS pa ON LOWER(pa.pair) = LOWER(token_meta.address)
LEFT JOIN pairs AS pb ON LOWER(pb.token) = LOWER(token_meta.address)
WHERE tokens.address IS NULL
AND pa.pair IS NULL
AND pb.token IS NULL
"""]

# Duplicates with different casing
# Fix: Wrap in brackets and delete all
# DELETE FROM token_meta WHERE address IN (...query...)
# Purposely not filled in query in comment, to prevent regular use
# without checking
warnings += ["""
SELECT
    CASE WHEN tm_a.address = LOWER(tm_b.address)
        THEN tm_b.address ELSE tm_a.address
    END as address
FROM token_meta as tm_a
JOIN token_meta as tm_b ON LOWER(tm_a.address) = LOWER(tm_b.address) AND tm_a.address != tm_b.address
"""]

# Invalid casing, yet no duplicates in token_meta
# FIX: RUN ONLY IF previous have been run, to weed out duplicates
# Force all to lowercase
# UPDATE {table} SET {col} = LOWER(col) WHERE LOWER({col}) != {col};
table_cols = [
    ["token_meta","address"],
    ["tokens","address"],
    ["pairs","token"],
    ["pairs","pair"],
]
for table,col in table_cols:
    warnings += [f"""SELECT {col} FROM {table} WHERE LOWER({col}) != {col};"""]

# Now RUN

from library.postgres import DB

class Status:
    OK = '\033[92m'
    WARNING = '\033[93m'
    ALERT = '\033[91m'
    _RESET = '\033[0m'

def p(msg,status):
    print(status + msg + Status._RESET)

print("")

with DB() as db:
    for sql in warnings:
        rows = db.get_all(sql)
        if len(rows) > 0:
            p(f"ALERT: Query returns {len(rows)} rows for:",Status.ALERT)
            p(sql,Status.WARNING)

print("")
print(f"Completed check of {len(warnings)} warnings")
print("")