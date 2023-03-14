import psycopg2
import ipaddress
from datetime import datetime
from multiprocessing.pool import ThreadPool
import nmap
import sys
from futures3.thread import ThreadPoolExecutor

#apt-get install python-nmap
#pip install futures3  --break-system-packages

conn = psycopg2.connect(
    host="x",
    port='x',
    database="cern",
    user="x",
    password="x"
)

def donmap(ip, cur: psycopg2):  
    nm = nmap.PortScanner()
    nm.scan(hosts=str(ip), arguments='-sS -sV -F -T5')
    #nm.scan(hosts=str(ip), arguments='-sS -sV -F -sU -T5') with UDP 
    is_alive = False
    
    for host in nm.all_hosts():
        #UPDATE Last IP Scann
        if nm[host].state() == "up":
            is_alive = True
        hostname = nm[host].hostname()
        if len(hostname) > 1:
            cur.execute("SELECT id FROM dns WHERE hostname=%s", (hostname,)) #get hostname from dns-table
            hostname_exists = cur.fetchone()
            inserted_id = 1
            if not hostname_exists: #if hostname not in dns-table --> insert and get ID
                cur.execute("INSERT INTO dns (hostname) VALUES (%s) RETURNING id", (hostname,))
                inserted_id = int(cur.fetchone()[0])
                conn.commit()
            else: #else get ID
                inserted_id = int(hostname_exists[0])
            
            #Check if hostname and ip are in dns_ip-table   
            cur.execute("INSERT INTO ip_dns (dns_id, ip) VALUES (%s, %s) ON CONFLICT DO NOTHING", (inserted_id, ip, ))    
            conn.commit()
   
        if 'tcp' in nm[host]: #If there are some TCP ports
            for port in nm[host]['tcp']:
                
                cur.execute("SELECT id FROM ports WHERE ip=%s AND port_number=%s AND port_type=%s", (ip, int(port), 'tcp', ))
                port_exists = cur.fetchone() 
                if nm[host]['tcp'][port]['state'] == 'open':    
                    if not port_exists:
                        query = "INSERT INTO ports (ip, port_number, port_type, port_state, service, version, extrainfo) VALUES (%s, %s, %s, %s, %s, %s, %s)"
                        values = (str(ip), int(port), 'tcp', str(nm[host]['tcp'][port]['state']), str(nm[host]['tcp'][port]['name']), str(nm[host]['tcp'][port]['product'] + ' ' + nm[host]['tcp'][port]['version']), str(nm[host]['tcp'][port]['extrainfo']))
                        cur.execute(query, values)
                    else:
                        id = int(port_exists[0])
                        query =  "UPDATE ports SET (port_state, service, version, extrainfo) = (%s,%s,%s,%s) where id = %s "
                        values = ( str(nm[host]['tcp'][port]['state']), str(nm[host]['tcp'][port]['name']), str(nm[host]['tcp'][port]['product'] + ' ' + nm[host]['tcp'][port]['version']), str(nm[host]['tcp'][port]['extrainfo']), id,)
                        cur.execute(query, values)
                       
                    conn.commit()
                    continue
                if not port_exists:          
                    query = "INSERT INTO ports (ip, port_number, port_type, port_state) VALUES (%s, %s, %s, %s)"
                    values = (str(ip), int(port), 'tcp', str(nm[host]['tcp'][port]['state']))
                    cur.execute(query, values)
                else:
                    id = int(port_exists[0]) 
                    query =  "UPDATE ports SET (port_state, service, version, extrainfo) = (%s,%s,%s,%s) where id = %s "
                    values = ( str(nm[host]['tcp'][port]['state']), '', '', '', id,)
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
    
    query =  "UPDATE ip SET (is_alive,  last_check) = (%s,%s) where ip = %s "
    values = (is_alive, datetime.now(), ip, )
    cur.execute(query, values)
    conn.commit()

   
def PRINTE(string, set_cur: psycopg2):
    print(string)

def main(): #getting IPSubnet in args
    args = sys.argv[1:]
    get_cursor = conn.cursor()
    get_cursor.execute("Select ip.ip from ip where ip_range = %s", (args[0],))
    iparray = get_cursor.fetchall()
    conn.commit()
    with ThreadPoolExecutor(max_workers=100) as executor:
        for ip in iparray:
            executor.submit(donmap, ip[0], conn.cursor())
    print('Script finish')
    
if __name__ == '__main__':
    main()
    conn.close()