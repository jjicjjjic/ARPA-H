import socket
import time

UDP_IP = "127.0.0.1"
PORT = 50001
MAIN_PORT = 50000

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, PORT))

print("[Mobile] Ready.")

while True:
    data, addr = sock.recvfrom(1024)
    msg = data.decode().strip()
    if msg == "MOVE_FOOD":
        print("[Mobile] Moving...")
        time.sleep(2)  # 이동 시뮬레이션
        print("[Mobile] Done moving.")
        sock.sendto(b"MOBILE_FOOD_DONE", (UDP_IP, MAIN_PORT))
