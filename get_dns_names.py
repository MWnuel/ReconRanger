import socket
import ipaddress
import threading

import psycopg2
def get_dns_names(network: ipaddress.IPv4Network, con: psycopg2.connect()):
    for ip in network:
        try:
            name, alias, addresslist = socket.gethostbyaddr(str(ip))
        except socket.herror:
            name = "NONE"
        print(str(ip) + " - " + name)

        if name not "NONE":
            query = "INSERT INTO dns (host_name, domain_name) VALUES (%s, %s)"
            values = (name, name)
            cur.execute(query, values)
            con.commit()

            query = "SELECT id FROM dns WHERE host_name = %s"
            values = (name)
            cur.execute(query, values)
            dns_id = cur.fetchone()

            query = "INSERT INTO ip_dns (dns_id, ip) VALUES (%s, %s)"
            values = (dns_id, ip)
            cur.execute(query, values)
            con.commit()

conn = psycopg2.connect(
    host="IP",
    port='PORT',
    database="cern",
    user="USER",
    password="PW"
)

t1 = threading.Thread(target=get_dns_names, args=(ipaddress.IPv4Network("137.138.121.0/25"), conn,))
t2 = threading.Thread(target=get_dns_names, args=(ipaddress.IPv4Network("137.138.121.128/25"), conn,))

t1.start()
t2.start()
t1.join()
t2.join()

conn.close()