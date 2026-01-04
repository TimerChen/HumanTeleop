# pip install vassar_feetech_servo_sdk

from vassar_feetech_servo_sdk import ServoController
import scservo_sdk as scs
import socket, struct
import time
import json
import os
import argparse

import numpy as np


DEST_IP = "127.0.0.1"
DEST_PORT = 5006


STS_ADDR_UNLOAD = 0x13
STS_ADDR_MAXV = 14
STS_ADDR_MINV = 15
STS_ADDR_CURV = 62
STS_ADDR_STATUS = 65
STS_ADDR_RESOLUTION = 0x1E

def manual_multi_turn(lastp, curp, minp, maxp, max_v=None):
    """
      Manually set let the motor to be in multi-turn range.
    """
    circle = maxp - minp
    if max_v is None:
        max_v = circle / 2
    if abs(curp - lastp) <= max_v:
        return curp
    
    curp0 = curp - circle
    curp1 = curp + circle
    if abs(curp0 - lastp) <= max_v:
        return curp0
    if abs(curp1 - lastp) <= max_v:
        return curp1
    print(f"[ERROR] too far: {curp} -> {lastp}")
    return lastp
    

def check_status(controller, servo_ids):
    for motor_id in servo_ids:
        status = controller.read_phase(motor_id)
        print(f"Motor {motor_id} phase: {status}")
        
def check_resolution(controller, servo_ids):
    for motor_id in servo_ids:
        
        write(controller, motor_id, STS_ADDR_RESOLUTION, 1)
        res = read(controller, motor_id, STS_ADDR_RESOLUTION)
        print(f"Motor {motor_id} resolution: {res}")
        
def check_voltage(controller, servo_ids):
    status = read(controller, servo_ids[0], STS_ADDR_STATUS)
    print(f"status: {status}")
    
    v0 = read(controller, servo_ids[0], STS_ADDR_CURV)
    v01 = read(controller, servo_ids[1], STS_ADDR_CURV)
    print(f"v0: {v0}")
    print(f"v01: {v01}")

    max_v = read(controller, servo_ids[0], STS_ADDR_MINV)
    max_v1 = read(controller, servo_ids[1], STS_ADDR_MINV)
    print(f"min_v: {max_v}")
    print(f"min_v1: {max_v1}")

    max_v = read(controller, servo_ids[0], STS_ADDR_MAXV)
    max_v1 = read(controller, servo_ids[1], STS_ADDR_MAXV)
    print(f"max_v: {max_v}")
    print(f"max_v1: {max_v1}")
    exit()
    
def read_positions(controller, servo_ids):
# Read all configured servos
    positions = controller.read_all_positions()
    return positions
    # for motor_id, pos in positions.items():
    #     print(f"Motor {motor_id}: {pos} ({pos/4095*100:.1f}%)")
        
def read(connector, sid, addr):
    # value, comm, err = packet.read1ByteTxRx(port, sid, addr)
    value, comm, err = connector.packet_handler.read1ByteTxRx(sid, addr)
    if comm != scs.COMM_SUCCESS:
        raise RuntimeError(f"read {addr} comm fail: {comm}")
    if err != 0:
        print(f"read {addr} servo err: {err} (sid={sid}) value={value}")
    return value

def write(connector, sid, addr, value):
    # comm, err = connector.packet_handler.write1ByteTxRx(sid, addr, value)
    # position = self.scs_toscs(position, 15)
    # txpacket = [acc, self.scs_lobyte(position), self.scs_hibyte(position), 0, 0, self.scs_lobyte(speed), self.scs_hibyte(speed)]
    # comm, err = connector.packet_handler.writeTxRx(sid, addr, len(txpacket), txpacket)
    comm, err = connector.packet_handler.write1ByteTxRx(sid, addr, value)
    if comm != scs.COMM_SUCCESS:
        raise RuntimeError(f"write {addr} comm fail: {comm}")
    if err != 0:
        print(f"write {addr} servo err: {err} (sid={sid}) value={value}")

def calibration(servo_ids, port="/dev/ttyACM0"):
    controller = ServoController(servo_ids=servo_ids, servo_type="sts", port=port)  # or "hls"
    controller.connect()

    # check_status(controller, servo_ids)
    # check_resolution(controller, servo_ids)
    # check_voltage(controller, servo_ids)

    # Set servos to middle position
    # input("[WARNING] Please make sure all servos are in the middle position and press Enter to continue...")
    input("[⚠️提示] 请保证遥控器处于原点位置，按回车键继续校准...")

    success = controller.set_middle_position()
    if success:
        print("All servos calibrated to middle position!")
        
    zero_positions = read_positions(controller, servo_ids)

    controller.disconnect()
    return zero_positions

def load_calib(calib_file, servo_ids, flip_directions, port="/dev/ttyACM0"):
    if not os.path.exists(calib_file):
        zero_positions = calibration(servo_ids, port)
        with open(calib_file, "w") as f:
            json.dump({"zero_positions": zero_positions, "flip_directions": flip_directions}, f, indent=4)
    else:
        with open(calib_file, "r") as f:
            calib_file = json.load(f)
        zero_positions = calib_file['zero_positions']
        flip_directions = calib_file['flip_directions']
        zero_positions = {int(k): v for k, v in zero_positions.items()}
        flip_directions = {int(k): v for k, v in flip_directions.items()}
    return zero_positions, flip_directions


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Send feetech servo positions.')
    parser.add_argument('--ip', type=str, default=DEST_IP, help='Destination IP address')
    parser.add_argument('--port', type=int, default=DEST_PORT, help='Destination port number')
    parser.add_argument('--calib',type=str, default=None, help='Calibrate servos')
    parser.add_argument('--echo', action='store_true', help='Echo servo positions')
    parser.add_argument('--device', type=str, default="/dev/ttyACM0", help='Serial device name')
    
    
    args = parser.parse_args()
    
    
    # Initialize controller with your servo configuration
    servo_ids = [1, 2, 3, 4, 5, 6, 7]
    flip_directions = {
        1: -1,
        2: 1,
        3: 1,
        4: -1,
        5: -1,
        6: -1,
        7: 1,
    }

    zero_positions, flip_directions = load_calib(args.calib, servo_ids, flip_directions, args.device)

    # Using context manager
    lastps = {motor_id: None for motor_id in servo_ids}

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ECHO = args.echo
    
    try:
        with ServoController(servo_ids, "sts", port=args.device) as controller:
            while True:
                if ECHO:
                    print("\033[H\033[J", end="")
                    print()
                positions = controller.read_all_positions()
                data = np.zeros(len(servo_ids), dtype=np.int32)
                i = 0
                for motor_id, pos in positions.items():
                    if lastps[motor_id] is None:
                        lastps[motor_id] = pos
                        continue
                    pos = manual_multi_turn(lastps[motor_id], pos, 0, 4096)
                    lastps[motor_id] = pos
                    
                    pos_norm = pos - zero_positions[motor_id]
                    pos_norm = pos_norm * flip_directions[motor_id]
                    data[i] = pos_norm
                    i += 1
                    
                    turns = pos_norm / 4096.0
                    degrees = turns * 360.0
                    if ECHO:
                        print(f"Motor {motor_id}: {pos_norm} turns={turns:.4f} deg={degrees:.2f}")
                    
                if ECHO:
                    time.sleep(0.1)
                packet = struct.pack(f'!{len(servo_ids)}l', *data)
                sock.sendto(packet, (args.ip, args.port))

    except KeyboardInterrupt:
        sock.close()