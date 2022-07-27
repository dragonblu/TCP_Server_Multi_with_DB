
# Optimized CRC-16 calculation.
# Polynomial: x^16 + x^15 + x^2 + 1 (0xa001)<br>
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
