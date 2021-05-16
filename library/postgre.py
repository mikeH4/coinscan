import psycopg

conn = psycopg.connect("dbname=tokens user=postgres")

cur = conn.cursor()

cur.execute("SELECT * FROM tokens")

records = cur.fetchall()
