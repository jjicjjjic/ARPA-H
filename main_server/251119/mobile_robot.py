import socket
import time
import subprocess
import os

UDP_IP = "127.0.0.1"
PORT = 50001
MAIN_PORT = 50000

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, PORT))

print("[Mobile] Ready.")

while True:
    data, addr = sock.recvfrom(1024)
    msg = data.decode().strip()
    if msg == "move_to_bed_start_main":
        print("[Mobile] move_to_bed_start")
        # arm_path = os.path.expanduser("~/rbpodo_kdh/build/practice1_251015")
        # subprocess.run([arm_path], check=True)
        time.sleep(2)  # 이동 시뮬레이션
        print("[Mobile] move_to_bed_finish")
        sock.sendto(b"move_to_bed_finish_mobile", (UDP_IP, MAIN_PORT))

    elif msg == "dock_on_start_main":
        print("[Mobile] dock_on_start")
        # arm_path = os.path.expanduser("~/rbpodo_kdh/build/practice1_251015")
        # subprocess.run([arm_path], check=True)
        time.sleep(2)  # 이동 시뮬레이션
        print("[Mobile] dock_on_finish")
        sock.sendto(b"dock_on_finish_mobile", (UDP_IP, MAIN_PORT))

    elif msg == "dock_off_start_main":
        print("[Mobile] dock_off_start")
        # arm_path = os.path.expanduser("~/rbpodo_kdh/build/practice1_251015")
        # subprocess.run([arm_path], check=True)
        time.sleep(2)  # 이동 시뮬레이션
        print("[Mobile] dock_off_finish")
        sock.sendto(b"dock_off_finish_mobile", (UDP_IP, MAIN_PORT))

    elif msg == "move_to_charger_start_main":
        print("[Mobile] move_to_charger_start")
        # arm_path = os.path.expanduser("~/rbpodo_kdh/build/practice1_251015")
        # subprocess.run([arm_path], check=True)
        time.sleep(2)  # 이동 시뮬레이션
        print("[Mobile] move_to_charger_finish")
        sock.sendto(b"move_to_charger_finish_mobile", (UDP_IP, MAIN_PORT))

    elif msg == "move_to_gap1_start_main":
        print("[Mobile] move_to_gap1_start")
        # arm_path = os.path.expanduser("~/rbpodo_kdh/build/practice1_251015")
        # subprocess.run([arm_path], check=True)
        time.sleep(2)  # 이동 시뮬레이션
        print("[Mobile] move_to_gap1_finish")
        sock.sendto(b"move_to_gap1_finish_mobile", (UDP_IP, MAIN_PORT))
