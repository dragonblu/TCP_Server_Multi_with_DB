import os
import sys
import argparse
import threading
import socket
import queue
import time
import pymysql

import GlobalConst
import server_packet
import DB_packet

def main():
    global host
    global port
    global db_host_ip
    global db_host_port
    global db_id
    global db_pw
    global db_name
    global ldb_file

    #parser = argparse.ArgumentParser()
    parser = argparse.ArgumentParser(description='This program is the tcp server whth database. (Local:SQLite3, External:MariaDB or MySQL)')
    parser.add_argument('-ip', metavar='ipaddress', help=' : Please set the server ip address', default='127.0.0.1')
    parser.add_argument('-port', metavar='Port', help=' : Please set the server port number', type=int, required=True)
    parser.add_argument('-db_ip', metavar='DB_ipaddress', help=' : Please set the MariaDB or MySQL ip address', default='127.0.0.1')
    parser.add_argument('-db_port', metavar='DB_Port', help=' : Please set the MariaDB or MySQL port number', type=int, default=3306)
    parser.add_argument('-db_id', metavar='DB_Identifier', help=' : Please set the MariaDB or MySQL id', default='root')
    parser.add_argument('-db_pw', metavar='DB_Password', help=' : Please set the MariaDB or MySQL password', default='')
    parser.add_argument('-db_name', metavar='DB_Name', help=' : Please set the MariaDB or MySQL database name', default='db')
    parser.add_argument('-ldb_file', metavar='LDB_File', help=' : Please set the Local SQLite3 File name', default='tcp_server_multi_with_db.db')
    args = parser.parse_args()

    print('')
    #print(f'argv : ', sys.argv)
    #print(f'args : ', args)
    print(f'args.ip      : ', args.ip)
    print(f'args.port    : ', args.port)
    print(f'args.db_ip   : ', args.db_ip)
    print(f'args.db_port : ', args.db_port)
    print(f'args.db_id   : ', args.db_id)
    print(f'args.db_pw   : ', args.db_pw)
    print(f'args.db_name : ', args.db_name)
    print('')

    host = args.ip
    port = args.port

    db_host_ip      = args.db_ip
    db_host_port    = args.db_port

    db_id   = args.db_id
    db_pw   = args.db_pw
    db_name = args.db_name  

    ldb_file = args.ldb_file

def init_database():
    global sqlite_conn
    global sqlite_curr

    result, sqlite_conn, sqlite_curr = DB_packet.init_sqlite3(ldb_file)
    if result != 0:
        print("Don't create the local database.")
        exit()

class Thread_DB_SQLite3(threading.Thread):
    def __init__(self, q):
        threading.Thread.__init__(self)
        self.flag = threading.Event()
        self.q = q

    def run(self):
        print('[QUEUE] Start Thread.')
        while not self.flag.is_set():
            if self.q.qsize() > 0:
                try:
                    conn = pymysql.connect(host = db_host_ip, port = db_host_port, user = db_id, password = db_pw, db = db_name, charset = 'utf8')
                    cur = conn.cursor()
                    print('[DB] Connection.')

                    while self.q.qsize() > 0:
                        data = self.q.get()
                        
                        device_id, sql = DB_packet.conv_data2sql(data)
                        print('[DB:SQL]', sql)

                        if sql:
                            try:
                                print('[DB:SQL] Execute. (', device_id, ')')
                                cur.execute(sql)
                                conn.commit()

                                print('[DB:SQL] Get Option. (', device_id, ')')
                                sql = DB_packet.get_option2sql(device_id)
                                cur.execute(sql)
                                result = cur.fetchall()

                                DB_packet.set_option_with_SQLite3(sqlite_curr, result)
                            except:
                                print("[DB] Don't execute sql.")

                    conn.close()
                    print('[DB] Disconnection.')
                except:
                    print('[DB] Not connection. (Wait 10 sec)')  
                    time.sleep(10)
        print('[QUEUE] End Thread.')

def threaded_client(connection, addr, id):
    print(f'[CLIENT:{id:03d}:Connect] {addr[0]}:{str(addr[1])}')
    #connection.send(str.encode('Welcome to the server'))
    while True:
        try:
            connection.settimeout(30)
            pre_data = connection.recv(4)

            if not pre_data:
                break

            try:
                server_packet.exec_stx(id, pre_data)
                
                connection.settimeout(5)
                data = connection.recv(server_packet.get_length(pre_data) + 3)
                #print(f'[Client:{id:03d}:Recv]', bytes(data).hex())

                server_packet.exec_etx(id, data)
                    
                # 암호화 확인
                print(f'[Client:{id:03d}:Packet] Check Crypto.')
                opt_crypto, = server_packet.get_option(pre_data)
                
                if opt_crypto:
                    # 암호 해제, DES
                    data_uncrypto = data
                    # 암호화 해제한 데이터 출력
                    print(f'[Client:{id:03d}:Packet] Uncrypto({len(data_uncrypto)}) : ', bytes(data_uncrypto).hex())
                else:
                    data_uncrypto = data
                    print(f'[Client:{id:03d}:Packet] Original({len(data_uncrypto)}) : ', bytes(data_uncrypto).hex())
                
                print(f'[Client:{id:03d}:Packet] Execute.')
                client_id = server_packet.exec_packet(id, connection, data_uncrypto, q)

                print(f'[Client:{id:03d}:Packet] Response.')
                server_packet.exec_response(id, connection, client_id)

            except socket.timeout: # Receive timeout
                print(f'[CLIENT:{id:03d}:Timeout] Receive Error.')
            except Exception as e:
                print(f'[Client:{id:03d}:Packet] Error :', e)

        except socket.timeout: # fail after 30 second of no activity
            print(f'[CLIENT:{id:03d}:Timeout] {addr[0]}:{str(addr[1])}')
            break
    connection.close()
    print(f'[CLIENT:{id:03d}:Disconnect] {addr[0]}:{str(addr[1])}')

if __name__ == "__main__":
    main()
    init_database()

    q = queue.Queue(1000)

    ServerSocket = socket.socket()

    try_count = 0
    while True:
        try_count += 1
        try:
            ServerSocket.bind((host, port))
            break
        except socket.error as e:
            print(str(e))
            time.sleep(1)
            if try_count > 3 :
                exit()

    print('')
    print('Waitting for a Connection.. (' + str(port) +')')
    ServerSocket.listen(5)

    try:
        thread_q = Thread_DB_SQLite3(q)
        thread_q.start()
    except:
        print("Don't create the Queue thread.")
        ServerSocket.close()
        exit()

    while True:
        ServerSocket.settimeout(1)
        try:
            try:
                Client, address = ServerSocket.accept()
            except TimeoutError:
                continue
        except KeyboardInterrupt:
            print("Keyboard interrupt.")
            break;

        try:
            t = threading.Thread(target=threaded_client, args=(Client, address, threading.active_count(), ), daemon=True)
            t.start()
            #print('Thread Number: ' + str(threading.active_count()))
        except:
            print("Don't create the thread.")
            Client.close()

    DB_packet.deinit_sqlite3(sqlite_conn, sqlite_curr)
    ServerSocket.close()

    thread_q.flag.set()
    thread_q.join()

print("Terminate program.")
