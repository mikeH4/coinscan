from library.postgres import DB

with DB("tokens") as db:
    # Remove orphaned, this is just to alert us, since as of the time of this script being written.
    # this was completely clean
    sql = """
    SELECT token_meta.address FROM token_meta
    LEFT JOIN tokens ON LOWER(tokens.address) = LOWER(token_meta.address)
    LEFT JOIN pairs AS pa ON LOWER(pa.pair) = LOWER(token_meta.address)
    LEFT JOIN pairs AS pb ON LOWER(pb.token) = LOWER(token_meta.address)
    WHERE
        tokens.address IS NULL
    AND pa.pair IS NULL
    AND pb.token IS NULL
    """

    # Remove duplicates with different casing
    sql = """
    DELETE FROM token_meta WHERE address IN (
        SELECT
            CASE WHEN tm_a.address = LOWER(tm_b.address)
                THEN tm_b.address ELSE tm_a.address
            END as address
        FROM token_meta as tm_a
        JOIN token_meta as tm_b ON LOWER(tm_a.address) = LOWER(tm_b.address) AND tm_a.address != tm_b.address
    )
    """