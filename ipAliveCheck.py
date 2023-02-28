import psycopg2
import ipaddress
from datetime import datetime

conn = psycopg2.connect(
    host="IP",
    port='PORT',
    database="cern",
    user="USER",
    password="PW"
)
ip_range = 'IP_RANGE'


network = ipaddress.IPv4Network('ip_range')

for ip in network:
    is_alive = False
    ##CHECK IF IP is Alive
    query = "INSERT INTO ip (ip, ip_range, is_alive, last_check) VALUES (%s, %s, %s, %s)"
    values = (ip, ip_range, is_alive , datetime.now())
    cur.execute(query, values)

conn.commit()
conn.close()