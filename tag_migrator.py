from library.postgres import DB

with DB("tokens") as db:
    sql = """
    INSERT INTO address_info
    (address,bscscan_tag,updated,added)
    SELECT
    holder,TRIM(string_agg(distinct(holder_tag),'')),max(updated_time),max(updated_time)
    FROM holders
    GROUP BY holders.holder
    """
    db.query(sql)

    sql = "ALTER TABLE holders DROP COLUMN holder_tag"
    db.query(sql)