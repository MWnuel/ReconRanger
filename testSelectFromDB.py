import psycopg2

conn = psycopg2.connect(
    host="IP",
    port='PORT',
    database="cern",
    user="USER",
    password="PW"
)

cur = conn.cursor()

cur.execute("SELECT * FROM ip_ranges")
rows = cur.fetchall()
for row in rows:
    print(row)

conn.commit()
conn.close()

