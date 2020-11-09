import socket
import sys
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # create IP4 UDP socket
while True:
    msg = input().encode() # get domain from user
    s.sendto(msg, (sys.argv[1], int(sys.argv[2]))) # send the domain to server (got as arguments)
    data, addr = s.recvfrom(1024) # recive answer
    print(data.decode().split(',')[1]) # print IP
s.close()
