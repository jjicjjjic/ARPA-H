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
    if msg == "m1_mobile": # move_to_bed_start_main
        print("[Mobile] m1_mobile")
        subprocess.run(
            "cd ~/mdrobot_py && "
            "python move_to_bed.py",
            shell=True,
            executable="/bin/bash",
        )
        time.sleep(2)
        sock.sendto(b"m2", (UDP_IP, MAIN_PORT))

    elif msg == "m2_mobile": # dock_on_start_main
        print("[Mobile] m2_mobile")
        # arm_path = os.path.expanduser("~/rbpodo_kdh/build/practice1_251015")
        # subprocess.run([arm_path], check=True)
        time.sleep(2)  # 이동 시뮬레이션
        sock.sendto(b"M 22 29", (UDP_IP, MAIN_PORT))
        time.sleep(20)
        sock.sendto(b"m3", (UDP_IP, MAIN_PORT))

    elif msg == "r11_mobile": # dock_off_start_main
        print("[Mobile] r11_mobile")
        # arm_path = os.path.expanduser("~/rbpodo_kdh/build/practice1_251015")
        # subprocess.run([arm_path], check=True)
        time.sleep(2)  # 이동 시뮬레이션
        sock.sendto(b"H", (UDP_IP, MAIN_PORT))
        time.sleep(20)
        sock.sendto(b"r12", (UDP_IP, MAIN_PORT))

    elif msg == "r12_mobile": # move_to_charger_start_main
        print("[Mobile] r12_mobile")
        subprocess.run(
            "cd ~/mdrobot_py && "
            "python move_to_charger.py",
            shell=True,
            executable="/bin/bash",
        )
        time.sleep(2)
        sock.sendto(b"r13", (UDP_IP, MAIN_PORT))

    elif msg == "f1_mobile": # move_to_gap1_start_main
        print("[Mobile] f1_mobile")
        subprocess.run(
            "cd ~/mdrobot_py && "
            "python move_to_bed.py",
            shell=True,
            executable="/bin/bash",
        )
        time.sleep(1)
        sock.sendto(b"f2", (UDP_IP, MAIN_PORT))

    elif msg == "f5_mobile": # move_to_charger_start_main
        print("[Mobile] f5_mobile")
        subprocess.run(
            "cd ~/mdrobot_py && "
            "python move_to_charger.py",
            shell=True,
            executable="/bin/bash",
        )
        time.sleep(2)
        sock.sendto(b"f6", (UDP_IP, MAIN_PORT))
