import socket
import time

UDP_IP = "127.0.0.1"
OUT_PORT = 5004
IN_PORT = 5005
buf = 1024
timeout = 3

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

info = "need file"
sock.sendto(info.encode(), (UDP_IP, OUT_PORT))
time.sleep(0.01)
info = "end"
sock.sendto(info.encode(), (UDP_IP, OUT_PORT))
sock.close()


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, IN_PORT))
while True:
    print("wait for message")
    data, addr = sock.recvfrom(1024)
    if data.decode("utf-8") == "image saved":
        print("load base image")
        break

info = "fake is ready"
sock.sendto(info.encode(), (UDP_IP, OUT_PORT))
time.sleep(0.01)
info = "end"
sock.sendto(info.encode(), (UDP_IP, OUT_PORT))
sock.close()

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, IN_PORT))

while True:
    print("wait for message")
    data, addr = sock.recvfrom(1024)
    if data.decode("utf-8") == "got fake":
        print("fake image")
        break