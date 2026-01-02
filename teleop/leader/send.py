"""
teleop.leader.send 的 Docstring
python teleop/leader/send.py --device /dev/ttyUSB0 --ip 127.0.0.1 --port 8080
"""

import numpy as np
import socket, struct
from dynamixel_sdk import PortHandler, PacketHandler, GroupSyncRead, GroupSyncWrite, COMM_SUCCESS
import argparse
import os
import json

DEST_IP = "127.0.0.1"
DEST_PORT = 5006

PORT  = "/dev/ttyUSB0"
BAUD  = 1000000
IDS   = [1,2,3,4,5,6,7]

flip_directions = {
    1: 1,
    2: -1,
    3: 1,
    4: 1,
    5: 1,
    6: 1,
    7: 1,
}

ADDR_PRESENT_POSITION = 132
LEN_PRESENT_POSITION  = 4
ADDR_GOAL_POSITION = 116
ADDR_POS_P_GAIN = 84

# Control table addresses (X-series, Protocol 2.0)
ADDR_TORQUE_ENABLE     = 64
ADDR_POSITION_P_GAIN   = 84
ADDR_GOAL_POSITION     = 116
ADDR_PRESENT_POSITION  = 132


TRIGGER_DXL_ID = 7
TORQUE_OFF = 0
TORQUE_ON = 1
P_GAIN = 100

def read_zero_position(device):
    port = PortHandler(device);  port.openPort();  port.setBaudRate(BAUD)
    pk   = PacketHandler(2.0)
    
    # 1) Disable
    comm_result, dxl_error = pk.write1ByteTxRx(port, TRIGGER_DXL_ID, ADDR_TORQUE_ENABLE, TORQUE_OFF)
    _check_dxl(pk, comm_result, dxl_error, context=" enable torque")
    
    input("reset the position of trigger")

    # 2) Read the zero position
    gsr = GroupSyncRead(port, pk, ADDR_PRESENT_POSITION, LEN_PRESENT_POSITION)
    for i in IDS: gsr.addParam(i)

    gsr.txRxPacket()
    data = [gsr.getData(i, ADDR_PRESENT_POSITION, LEN_PRESENT_POSITION) for i in IDS]
    data = np.array(data, dtype=np.uint32).astype(np.int32)
    
    enable_trigger(port, pk, data[-1])
    
    return data

# def enable_trigger(port, pk, zero_pos_trigger):
#     """
#     read position of id=7, , set goal position = pos+400, position p gain = 100.
#     """
#     gsr = GroupSyncWrite(port, pk, ADDR_GOAL_POSITION, LEN_PRESENT_POSITION)
#     gsr.addParam(7)
#     gsr.txRxPacket()
#     data = gsr.getData(7, ADDR_GOAL_POSITION, LEN_PRESENT_POSITION) 

def _check_dxl(pk, comm_result, dxl_error, context=""):
    if comm_result != COMM_SUCCESS:
        raise RuntimeError(f"[DXL COMM FAIL]{context}: {pk.getTxRxResult(comm_result)}")
    if dxl_error != 0:
        raise RuntimeError(f"[DXL HW ERROR]{context}: {pk.getRxPacketError(dxl_error)}")

def enable_trigger(port, pk, zero_pos_trigger):
    """
    read position of id=7, enable torque control, set goal position = pos+400, position p gain = 100.

    Assumptions:
      - Protocol 2.0 (PacketHandler(2.0))
      - X-series control table (e.g., XM430/XL430):
        Torque Enable(64, 1B), Position P Gain(84, 2B),
        Goal Position(116, 4B), Present Position(132, 4B).
    """

    # 1) Read present position (before torque on)
    # pos_before, comm_result, dxl_error = pk.read4ByteTxRx(port, DXL_ID, ADDR_PRESENT_POSITION)
    # _check_dxl(pk, comm_result, dxl_error, context=" read present position (before torque)")

    # 2) Enable torque
    comm_result, dxl_error = pk.write1ByteTxRx(port, TRIGGER_DXL_ID, ADDR_TORQUE_ENABLE, TORQUE_ON)
    _check_dxl(pk, comm_result, dxl_error, context=" enable torque")

    # NOTE: In Position Control Mode, turning torque on can reset Present Position on some X-series.
    # So read again after torque on.
    # pos, comm_result, dxl_error = pk.read4ByteTxRx(port, DXL_ID, ADDR_PRESENT_POSITION)
    # _check_dxl(pk, comm_result, dxl_error, context=" read present position (after torque)")

    # 3) Set Position P Gain = 100
    comm_result, dxl_error = pk.write2ByteTxRx(port, TRIGGER_DXL_ID, ADDR_POSITION_P_GAIN, P_GAIN)
    _check_dxl(pk, comm_result, dxl_error, context=" set position P gain")

    # 4) Set goal position
    # if zero_pos_trigger:
    #     goal_pos = 0
    # else:
    goal_pos = int(zero_pos_trigger) + 400

    comm_result, dxl_error = pk.write4ByteTxRx(port, TRIGGER_DXL_ID, ADDR_GOAL_POSITION, goal_pos)
    _check_dxl(pk, comm_result, dxl_error, context=" write goal position")

    # return {
    #     "id": DXL_ID,
    #     "pos_before_torque": int(pos_before),
    #     "pos_after_torque": int(pos),
    #     "goal_pos": int(goal_pos),
    #     "p_gain": int(P_GAIN),
    # }


def load_calib(calib_file, flip_directions, device):
    if not os.path.exists(calib_file):
        zero_positions = read_zero_position(device).tolist()
        with open(calib_file, "w") as f:
            json.dump({"zero_positions": zero_positions, "flip_directions": flip_directions}, f, indent=4)
            
    else:
        with open(calib_file, "r") as f:
            calib_file = json.load(f)
        zero_positions = calib_file['zero_positions']
        flip_directions = calib_file['flip_directions']
        # zero_positions = {int(k): v for k, v in zero_positions.items()}
        flip_directions = {int(k): v for k, v in flip_directions.items()}
    zero_positions = np.array(zero_positions)
    return zero_positions, flip_directions


if __name__ == "__main__":
    # set
    parser = argparse.ArgumentParser(description='Send servo positions to follower.')
    parser.add_argument('--ip', type=str, default=DEST_IP, help='Destination IP')
    parser.add_argument('--port', type=int, default=DEST_PORT, help='Destination port')
    parser.add_argument('--device', type=str, default=PORT, help='Serial device name')
    parser.add_argument('--calib', type=str, default="calib_cjx.json")
    args = parser.parse_args()
    
    
    zero_positions, flip_directions = load_calib(args.calib, flip_directions, args.device)
    
    port = PortHandler(args.device)
    port.openPort()
    port.setBaudRate(BAUD)
    pk   = PacketHandler(2.0)

    gsr = GroupSyncRead(port, pk, ADDR_PRESENT_POSITION, LEN_PRESENT_POSITION)
    for i in IDS: gsr.addParam(i)

    print(f"[INFO] waiting for socket {args.ip} {args.port}")
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        while True:
            if gsr.txRxPacket() == 0 and all(gsr.isAvailable(i, ADDR_PRESENT_POSITION, LEN_PRESENT_POSITION) for i in IDS):
                data = [gsr.getData(i, ADDR_PRESENT_POSITION, LEN_PRESENT_POSITION) for i in IDS]
                data = np.array(data, dtype=np.uint32).astype(np.int32) - zero_positions
                for i in range(7):
                    data[i] = data[i] * flip_directions[i+1]
            else:
                continue
            packet = struct.pack('!7l', *data)
            sock.sendto(packet, (args.ip, args.port))

    except KeyboardInterrupt:
        sock.close()
        port.closePort()
