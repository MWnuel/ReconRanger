import psycopg2
import ipaddress
from datetime import datetime
from multiprocessing.pool import ThreadPool
import nmap
from futures.thread import ThreadPoolExecutor

#apt-get install python-nmap
#pip install futures3  --break-system-packages


conn = psycopg2.connect(
    host="IP",
    port='PORT',
    database="cern",
    user="USER",
    password="PW"
)

def donmap(ip, cur: psycopg2):
    
    nm = nmap.PortScanner()
    nm.scan(hosts=str(ip), arguments='-sS -sV -F -T5')
    #nm.scan(hosts='128.141.22.68', arguments='-sS -sV -F -sU -T5') with UDP

    for host in nm.all_hosts():
        hostname = nm[host].hostname()
        if len(hostname) > 1:
            cur.execute("SELECT id FROM dns WHERE hostname=%s", (hostname,))
            hostname_exists = cur.fetchone()
            inserted_id = 1
            if not hostname_exists:
                cur.execute("INSERT INTO dns (hostname) VALUES (%s) RETURNING id", (hostname,))
                inserted_id = int(cur.fetchone()[0])
                conn.commit()
            else:
                inserted_id = int(hostname_exists[0])
            cur.execute("INSERT INTO ip_dns (dns_id, ip) VALUES (%s, %s)", (inserted_id, ip ))    
            conn.commit()

        if 'tcp' in nm[host]:
            for port in nm[host]['tcp']:
                if nm[host]['tcp'][port]['state'] == 'open':    
                    query = "INSERT INTO ports (ip, port_number, port_type, port_state, service, version, extrainfo) VALUES (%s, %s, %s, %s, %s, %s, %s)"
                    values = (str(ip), int(port), 'tcp', str(nm[host]['tcp'][port]['state']), str(nm[host]['tcp'][port]['name']), str(nm[host]['tcp'][port]['product'] + ' ' + nm[host]['tcp'][port]['version']), str(nm[host]['tcp'][port]['extrainfo']))
                    cur.execute(query, values)
                    conn.commit()
                    continue          
                query = "INSERT INTO ports (ip, port_number, port_type, port_state) VALUES (%s, %s, %s, %s)"
                values = (str(ip), int(port), 'tcp', str(nm[host]['tcp'][port]['state']))
                cur.execute(query, values)
                conn.commit()
       
#        if 'udp' in nm[host]:   
#            for port in nm[host]['udp']:
#                if nm[host]['udp'][port]['state'] == 'open':    
#                    query = "INSERT INTO ports (ip, port_number, port_type, port_state, service, version, extrainfo) VALUES (%s, %s, %s, %s, %s, %s, %s)"
#                    values = (str(ip), int(port), 'udp', str(nm[host]['udp'][port]['state']), str(nm[host]['udp'][port]['name']), str(nm[host]['udp'][port]['product'] + nm[host]['udp'][port]['version']), str(nm[host]['udp'][port]['extrainfo']))
#                    set_cur.execute(query, values)
#                    conn.commit()
#                    continue          
#                query = "INSERT INTO ports (ip, port_number, port_type, port_state) VALUES (%s, %s, %s, %s)"
#                values = (str(ip), int(port), 'udp', str(nm[host]['udp'][port]['state']))
#                set_cur.execute(query, values)
#                conn.commit()
               
def PRINTE(string, set_cur: psycopg2):
    print(string)

def main():
    get_cursor = conn.cursor()
    get_cursor.execute('Select ip.ip from ip where is_alive=true')
    iparray = get_cursor.fetchall()
    conn.commit()

    with ThreadPoolExecutor(max_workers=100) as executor:
        for ip in iparray:
            get_cursor.execute("SELECT * from ip_dns WHERE ip=%s", (ip,))
            if not get_cursor.fetchone():
                executor.submit(donmap, ip[0], conn.cursor())
                #executor.submit(PRINTE, ip, conn.cursor())
    print('Script finish')
    
if __name__ == '__main__':
    main()
    conn.close()