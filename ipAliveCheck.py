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
        if "137.138" not in str(row[0]):        #Already in DB
            print(row[0])
            ip_range = str(row[0])
            network = ipaddress.IPv4Network(ip_range)
            for ip in network:
                is_alive = False
                if "Host is up" in subprocess.check_output(["nmap","-PE", "-PP", "-p T:443,80,8443,22,3389,8449,8000,554,8089,1934,8080,873,7999", str(ip)]).decode("utf-8"):
                    is_alive = True

                query = "INSERT INTO ip (ip, ip_range, is_alive, last_check) VALUES (%s, %s, %s, %s)"
                values = (str(ip), ip_range, is_alive , datetime.now())
                cur.execute(query, values)
                conn.commit()


conn.close()

print('Script finish')
