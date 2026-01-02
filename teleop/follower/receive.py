import numpy as np
import socket, struct

PORT = 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('127.0.0.1', PORT))

try:
    while True:
        data, addr = sock.recvfrom(4096)
        data = struct.unpack('!7H', data)
        data = np.array(data, dtype=np.uint16).astype(np.int32) - 4096
        print(data)

except KeyboardInterrupt:
    sock.close()
