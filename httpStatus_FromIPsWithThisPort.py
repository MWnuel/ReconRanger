import psycopg2
import ipaddress
from datetime import datetime
from multiprocessing.pool import ThreadPool
import nmap
import sys
from futures3.thread import ThreadPoolExecutor
import requests

#apt-get install python-nmap
#pip install futures3  --break-system-packages

conn = psycopg2.connect(
    host="x",
    port='x',
    database="cern",
    user="x",
    password="x"
)

def getStatus(portid, ip, hostname, port, cur: psycopg2):
    http = 'http://'
    if port == 443:
        http = 'https://'
    if port == 8443:
        http = 'https://'
    try:
        requests.packages.urllib3.disable_warnings()
        response = requests.get(f"{http}{hostname}:{port}", verify=False )     
        http_status = response.status_code
        query = "INSERT INTO port_info (port_id,  http_status) VALUES (%s, %s)"
        values = (int(portid), int(http_status))
        cur.execute(query, values)
        conn.commit()
        
    except requests.exceptions.RequestException as e:
        query = "INSERT INTO port_info (port_id, other_infos) VALUES (%s, %s)"
        values = (portid, 'Error')
        cur.execute(query, values)
        conn.commit()    


def main():
    args = sys.argv[1:] # get PortNumber --> 80, 443 or 8443
    port = int(args[0])
    get_cursor = conn.cursor()
    get_cursor.execute("""SELECT p.id, ip.ip, hostname FROM ip
    JOIN ip_dns id on ip.ip = id.ip
    JOIN dns d on d.id = id.dns_id
    JOIN ports p on ip.ip = p.ip
    WHERE p.port_state = 'open' and p.port_number = %s""", (port,))
    iparray = get_cursor.fetchall()
    conn.commit()
    with ThreadPoolExecutor(max_workers=30) as executor:
        for ip in iparray:
            #executor.submit(PRINTE, ip[0], conn.cursor())
            executor.submit(getStatus, ip[0], ip[1], ip[2], port, conn.cursor())

    print('Script finish')
    
if __name__ == '__main__':
    main()
    conn.close()