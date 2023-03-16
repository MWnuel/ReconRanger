import psycopg2

conn = psycopg2.connect(
    host="IP",
    port='PORT',
    database="cern",
    user="USER",
    password="PW"
)

cur = conn.cursor()

cur.execute("""SELECT ip.ip, d.hostname, p.port_number, p.port_state, p.service, pi.http_status, p.version, p.extrainfo  FROM ip
    JOIN ip_dns id on ip.ip = id.ip
    JOIN dns d on d.id = id.dns_id
    JOIN ports p on ip.ip = p.ip
    JOIN port_info pi on p.id = pi.port_id
    ORDER BY ip, port_number""")
rows = cur.fetchall()
for row in rows:
    print(row)

conn.commit()
conn.close()