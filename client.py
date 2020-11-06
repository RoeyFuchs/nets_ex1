import socket
import sys
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
while True:
    msg = input().encode()
    s.sendto(msg, (sys.argv[1], int(sys.argv[2])))
    data, addr = s.recvfrom(1024)
    print(data.decode(), addr)
s.close()
