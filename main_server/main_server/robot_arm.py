import socket
import os
import subprocess
import time

UDP_IP = "127.0.0.1"
PORT = 50002
MAIN_PORT = 50000

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, PORT))

print("[Arm] Ready.")

while True:
    data, addr = sock.recvfrom(1024)
    msg = data.decode().strip()
    if msg.startswith("MOVE_ARM_FOOD1"):
        print("[Arm] Moving arm...")
        arm_path = os.path.expanduser("~/rbpodo_kdh/build/practice1_251015")
        subprocess.run([arm_path], check=True)
        time.sleep(1.5)
        print("[Arm] Done.")
        sock.sendto(b"ARM_DONE_FOOD1", (UDP_IP, MAIN_PORT))
    elif msg.startswith("MOVE_ARM_FOOD2"):
        print("[Arm] Moving arm...")
        arm_path = os.path.expanduser("~/rbpodo_kdh/build/practice2_251015")
        subprocess.run([arm_path], check=True)
        time.sleep(1.5)
        print("[Arm] Done.")
        sock.sendto(b"ARM_DONE_FOOD2", (UDP_IP, MAIN_PORT))
