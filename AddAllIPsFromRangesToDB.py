import psycopg2
import ipaddress
from datetime import datetime
import subprocess

conn = psycopg2.connect(
    host="IP",
    port='PORT',
    database="cern",
    user="USER",
    password="PW"
)
cur = conn.cursor()

cur.execute("SELECT ip_range FROM ip_ranges")
rows = cur.fetchall()
for row in rows:
    if ":" not in str(row[0]):      #Ignore IPv6
        ip_range = str(row[0])
        network = ipaddress.IPv4Network(ip_range)
        for ip in network:
            is_alive = False
            query = "INSERT INTO ip (ip, ip_range, is_alive, last_check) VALUES (%s, %s, %s, %s)"
            values = (str(ip), ip_range, is_alive , datetime.now())
            cur.execute(query, values)
            conn.commit()
conn.close()
print('Script finish')
