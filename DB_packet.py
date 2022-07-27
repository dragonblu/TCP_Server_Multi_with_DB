
import sqlite3
import struct

table_name = 'test'

def init_sqlite3(file):
    print('[DB:SQLite3] LIB Version :', sqlite3.version)
    print('[DB:SQLite3] DB Version :', sqlite3.sqlite_version)

    if not file:
        print('[DB:SQLite3] Not valid the file name.')
        return -1,

    #isolation_level=None:auto commit 설정 commit() 함수 실행 없이 자동으로 commit 됨.
    conn = sqlite3.connect(file, isolation_level=None)
    curr = conn.cursor()

    try:
        # First Read.
        curr.execute("SELECT * FROM {}".format(table_name))
        '''
        result = curr.fetchall()

        if result:
            for data in result:
                print(data)
        else:
            print("[DB:SQLite3] Faild to get data.")
        '''
    except sqlite3.OperationalError:
        # Create Table.
        print("[DB:SQLite3] Create Table.")
        curr.execute("CREATE TABLE IF NOT EXISTS '{}'(id INTEGER, name TEXT, age INTEGER)".format(table_name))
    
    return 0, conn, curr

def deinit_sqlite3(conn, curr):
    curr.close()
    conn.close()

def conv_data2sql(data : bytearray):
    try:
        """
        data_id  = struct.unpack('H', data[0:2]) # unsigned short (2 bytes)
        data_s01 = struct.unpack('f', data[2:6]) # float (4 bytes)
        data_s02 = struct.unpack('f', data[6:10]) # float (4 bytes)
        data_s03 = struct.unpack('f', data[10:14]) # float (4 bytes)
        data_s04 = struct.unpack('f', data[14:18]) # float (4 bytes)
        data_s05 = struct.unpack('f', data[18:22]) # float (4 bytes)
        data_s06 = struct.unpack('f', data[22:26]) # float (4 bytes)
        data_v01 = struct.unpack('f', data[26:30]) # float (4 bytes)
        data_v02 = struct.unpack('f', data[30:34]) # float (4 bytes)
        data_v03 = struct.unpack('f', data[34:38]) # float (4 bytes)
        data_v04 = struct.unpack('f', data[38:42]) # float (4 bytes)
        data_t01 = struct.unpack('f', data[42:46]) # float (4 bytes)
        data_h01 = struct.unpack('f', data[46:50]) # float (4 bytes)
        """

        #data_id, = struct.unpack('H', data[0:2])
        #data_s01, data_s02, data_s03, data_s04, data_s05, data_s06, data_v01, data_v02, data_v03, data_v04, data_t01, data_h01 = struct.unpack('ffffffffffff', data[2:50])

        data_id, data_s01, data_s02, data_s03, data_s04, data_s05, data_s06, data_v01, data_v02, data_v03, data_v04, data_t01, data_h01 = struct.unpack('<H12f', data)

        print('[STRUCT] Unpack. :', data_id, data_s01, data_s02, data_s03, data_s04, data_s05, data_s06, data_v01, data_v02, data_v03, data_v04, data_t01, data_h01)

        return data_id, 'insert into data_list (id, s01, s02, s03, s04, s05, s06, v01, v02, v03, v04, t01, h01) values ({:d},{:.6f},{:.6f},{:.6f},{:.6f},{:.6f},{:.6f},{:.6f},{:.6f},{:.6f},{:.6f},{:.6f},{:.6f})'.format(data_id, data_s01, data_s02, data_s03, data_s04, data_s05, data_s06, data_v01, data_v02, data_v03, data_v04, data_t01, data_h01)
    except:
        print('[STRUCT] Error unpack.')
        return 0, ''

def get_option2sql(device_id):
    return 'select * from device_list where id={:d} limit 1'.format(device_id)

def set_option_with_SQLite3(curr, option_data):
    if option_data:
        for data in option_data:
            print(data)
    else:
        print("[DB:SQL] Faild to get data.")
        return -1
    return 0