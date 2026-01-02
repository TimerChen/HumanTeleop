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

gsr.txRxPacket()
data = [gsr.getData(i, ADDR_PRESENT_POSITION, LEN_PRESENT_POSITION) for i in IDS]
data = np.array(data, dtype=np.uint32).astype(np.int32)
    
with open('zero_positions.txt', 'w') as f:
    for x in data:
        f.write(f'{x}\n')
