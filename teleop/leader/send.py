import numpy as np
import socket, struct
from dynamixel_sdk import PortHandler, PacketHandler, GroupSyncRead

DEST_IP = "127.0.0.1"
DEST_PORT = 5006

PORT  = "/dev/ttyUSB0"
BAUD  = 1000000
IDS   = [1,2,3,4,5,6,7]

ADDR_PRESENT_POSITION = 132
LEN_PRESENT_POSITION  = 4

port = PortHandler(PORT);  port.openPort();  port.setBaudRate(BAUD)
pk   = PacketHandler(2.0)

gsr = GroupSyncRead(port, pk, ADDR_PRESENT_POSITION, LEN_PRESENT_POSITION)
for i in IDS: gsr.addParam(i)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

try:
    while True:
        if gsr.txRxPacket() == 0 and all(gsr.isAvailable(i, ADDR_PRESENT_POSITION, LEN_PRESENT_POSITION) for i in IDS):
            data = [gsr.getData(i, ADDR_PRESENT_POSITION, LEN_PRESENT_POSITION) for i in IDS]
            data = np.array(data, dtype=np.uint32).astype(np.int32) + 4096
        else:
            continue
        packet = struct.pack('!7H', *data)
        sock.sendto(packet, (DEST_IP, DEST_PORT))

except KeyboardInterrupt:
    sock.close()
    port.closePort()
