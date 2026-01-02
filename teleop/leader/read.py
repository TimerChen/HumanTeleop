import numpy as np
from dynamixel_sdk import PortHandler, PacketHandler, GroupSyncRead

PORT  = "/dev/ttyUSB0"
BAUD  = 1000000
IDS   = [1,2,3,4,5,6,7]

ADDR_PRESENT_POSITION = 132
LEN_PRESENT_POSITION  = 4

port = PortHandler(PORT);  port.openPort();  port.setBaudRate(BAUD)
pk   = PacketHandler(2.0)

gsr = GroupSyncRead(port, pk, ADDR_PRESENT_POSITION, LEN_PRESENT_POSITION)
for i in IDS: gsr.addParam(i)

try:
    while True:
        gsr.txRxPacket()
        data = [gsr.getData(i, ADDR_PRESENT_POSITION, LEN_PRESENT_POSITION) for i in IDS]
        data = np.array(data, dtype=np.uint32).astype(np.int32)
        print(data)

except KeyboardInterrupt:
    port.closePort()