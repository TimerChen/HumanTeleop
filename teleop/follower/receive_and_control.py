import time
import numpy as np
import socket, struct
from piper_sdk import C_PiperInterface_V2
import argparse

# user='lyk'
user='cjx'

# MSG_MODE = 'gello'
MSG_MODE = 'custom_so101'
CTL_MODE = 'mit'


CAN  = "can0"
FILE = "right.txt"
if user=='lyk':
    FILE = "zero_positions_lyk.txt"
elif user=='cjx':
    FILE = "zero_positions_cjx.txt"
PORT = 5006

def init_piper(can, ctrl_mode):
    piper = C_PiperInterface_V2(can)
    piper.ConnectPort()
    while(not piper.EnablePiper()):
        time.sleep(0.01)
    piper.EmergencyStop(0)
    # disable and clear error
    piper.GripperCtrl(0, 1000, 0x02, 0)
    # enable gripper
    piper.GripperCtrl(0, 1000, 0x01, 0)
    if ctrl_mode == 'mit':
        piper.MotionCtrl_2(0x01, 0x01, 100, 0xAD)
    else:
        piper.MotionCtrl_2(0x01, 0x01, 30, 0x00)
    return piper
    
def disable_piper(piper):
    piper.EmergencyStop(1)
    time.sleep(2)
    while piper.DisablePiper():
        time.sleep(0.01)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Receive and control the piper robot.')
    parser.add_argument('--user', type=str, default=user, help='User name (lyk or cjx)')
    parser.add_argument('--port', type=int, default=PORT, help='Port number')
    parser.add_argument('--can', type=str, default=CAN, help='CAN interface name')
    parser.add_argument('--ctrl_mode', type=str, default=CTL_MODE, help='Control mode (mit or custom_so101)', choices=['mit', 'spd'])
    parser.add_argument('--msg_mode', type=str, default=MSG_MODE, help='Message mode (gello or custom_so101)', choices=['gello', 'custom_so101'])
    args = parser.parse_args()
    user = args.user
    
    piper = init_piper(args.can, args.ctrl_mode)

    # load zero positions
    if args.msg_mode == "gello":
        with open(FILE, 'r') as f:
            zero_positions = np.array(f.readlines(), dtype=np.int32)

    # receive and control
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('0.0.0.0', args.port))

    try:
        while True:
            print("\033[H\033[J", end="")
            print()
            data, addr = sock.recvfrom(4096)
            if MSG_MODE == 'gello':
                exit()
                data = struct.unpack('!7H', data)
                data = np.array(data, dtype=np.uint16).astype(np.int32) - 4096

                offsets = data - zero_positions

                joints_target_deg = np.round(offsets[:6] * 87.890625).astype(np.int32)
                if user == 'cjx':
                    joints_target_deg[1] = -joints_target_deg[1]
                piper.JointCtrl(*joints_target_deg)
                piper.GripperCtrl(int(offsets[6] * 400), 1000, 0x01, 0)
            else:
                
                data = struct.unpack('!7l', data)
                offsets = np.array(data, dtype=np.int32)
                offsets = offsets / 4096.0 * 360.0
                joints_target_deg = np.round(offsets*1000).astype(np.int32)
                
                print("joint:", joints_target_deg[:6])
                print("gripper:", int(joints_target_deg[6]))

                piper.JointCtrl(*joints_target_deg[:6])
                piper.GripperCtrl(int(joints_target_deg[6]*2), 1000, 0x01, 0)

    except KeyboardInterrupt:
        disable_piper(piper)
        sock.close()
