# [Ethernet::TCP] Server Test Application
<p align="left">
    <img alt="Python" src ="https://img.shields.io/badge/Python-3776AB.svg?&style=for-the-badge&logo=Python&logoColor=white">
</p>

## 프로그램 설명
> TCP Server 예제 소스입니다.
> struct 모듈을 이용하여 이진데이터를 생성하였습니다.
> 이진데이터 Checksum을 위해 CRC-16을 사용하였습니다.

## Versions
|      Version     |    Date    |  Note                                                  |
| :--------------: | :--------: | :----------------------------------------------------: |
|       0.1.0      | 2022-07-27 |  First                                                 |

## Global Constance (GlobalConst.py)
``` Python
Server_Address = "127.0.0.1"
Server_Port = 5000
```
## 순환 중복 검사(CRC, Cyclic Redundancy Check)
### CRC-16
``` Python
# Optimized CRC-16 calculation.
# 다항식(Polynomial): x^16 + x^15 + x^2 + 1 (0xa001)<br>
# Initial value: 0xffff
# This CRC is normally used in disk-drive controllers.
def crc16(data : bytearray):
    if not data:
        return 0
    
    crc = 0xFFFF
    for x in data:
        crc ^= x
        for j in range(8):
            if ((crc & 0x01) == 1):
                crc = (crc >> 1) ^ 0xA001
            else:
                crc = (crc >> 1)
    
    return crc
```

# License
-