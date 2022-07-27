import socket
import os
import queue
import struct
from bitstring import BitArray

import CRC16

def exec_stx(id, data : bytearray):
    if not data:
        #print(f'[Client:{id:03d}:STX] Data is empty.')
        raise ValueError('[STX] Data is empty.')

    if data[0] == 0x02:
        print(f'[Client:{id:03d}:STX] Pass.')
    else:
        #print(f'[Client:{id:03d}:STX] Fail.')
        raise SyntaxError('[STX] Fail.')
    
def get_option(data : bytearray):
    # 7 6 5 4 3 2 1 0
    # x x x x x x x Crypto

    Opt_Crypto   = BitArray(bytes=data, length=1, offset=15).uint
    Opt_Reserved = BitArray(bytes=data, length=7, offset=8).uint

    return Opt_Crypto, 

def get_length(data : bytearray):
    packet_length = int.from_bytes(data[2:4], "little")
    return packet_length

def exec_etx(id, data : bytearray):

    if not data:
        #print(f'[Client:{id:03d}:ETX] Data is empty.')
        raise ValueError('[ETX] Data is empty.')

    tail_data = data[-3:]

    if tail_data[2] == 0x03:
        print(f'[Client:{id:03d}:ETX] Pass.')

        crc_data = CRC16.crc16(data[:-3])
        print(f'[Client:{id:03d}:ETX] Calculate CRC16 ({hex(crc_data)})')

        if (int.from_bytes(tail_data[0:2], "little") == crc_data):
            print(f'[Client:{id:03d}:ETX] CRC16 Pass.')
        else:
            #print(f'[Client:{id:03d}:ETX] CRC16 Fail.')
            raise SyntaxError('[ETX:CRC16] Fail.')
    else:
        #print(f'[Client:{id:03d}:ETX] Fail.')
        raise SyntaxError('[ETX] Fail.')

def exec_packet(id, connection, data : bytearray, q):
    if not data:
        #print(f'[Client:{id:03d}:Packet] Data is empty')
        raise ValueError('Data is empty.')

    # 원본데이터 출력
    #print(f'[Client:{id:03d}:Packet] IN({len(data)}) : ', bytes(data).hex())

    q_data = data[:-3]

    if len(q_data) == 50:
        # 큐에 데이터 넣기
        q.put(q_data)

        data_id, data_s01, data_s02, data_s03, data_s04, data_s05, data_s06, data_v01, data_v02, data_v03, data_v04, data_t01, data_h01 = struct.unpack('<H12f', q_data)
        return data_id

    #print(f'[Client:{id:03d}:Packet] Data is not valid.')
    raise ValueError('Data is not valid.')

def exec_response(id, connection, client_id):
    # SQLite3 데이터 확인

    # 응답패킷 생성

    # 응답
    print(f'[Client:{id:03d}:Response] ACK.')
    connection.sendall(str.encode('ACK'))
