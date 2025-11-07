import socket
import os
import subprocess
import time

# UDP 설정
UDP_IP = "127.0.0.1"
PORT = 50002
MAIN_PORT = 50000

# RB 로봇 TCP 설정
ROBOT_IP = "192.168.0.10"   # ⚠️ 실제 RB 로봇 제어반 IP로 바꾸세요
ROBOT_PORT = 5000           # 명령 포트
MUSIC_COMMAND = 'interface_music_on "test_1", 0,1,10,0,0\n'  # 실행할 명령 (\n 필수)

def send_rb_command(command: str):
    """RB 로봇 제어반으로 TCP 명령 전송"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(2.0)
            s.connect((ROBOT_IP, ROBOT_PORT))
            s.sendall(command.encode('utf-8'))
            response = s.recv(1024).decode('utf-8', errors='ignore').strip()
            print(f"[RB] Sent: {command.strip()}")
            print(f"[RB] Response: {response}")
    except Exception as e:
        print(f"[RB] TCP command send failed: {e}")

# UDP 소켓 준비
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, PORT))

print("[Arm] Ready.")

while True:
    data, addr = sock.recvfrom(1024)
    msg = data.decode().strip()

    if msg.startswith("MOVE_ARM_FOOD1"):
        print("[Arm] Moving arm...")

        # ✅ 여기서 RB 협동로봇에 음악 명령 전송
        send_rb_command(MUSIC_COMMAND)

        # 로봇팔 동작 수행
        arm_path = os.path.expanduser("~/rbpodo_kdh/build/practice1_251015")
        subprocess.run([arm_path], check=True)

        time.sleep(1.5)
        print("[Arm] Done.")
        sock.sendto(b"ARM_DONE_FOOD1", (UDP_IP, MAIN_PORT))

    elif msg.startswith("MOVE_ARM_FOOD2"):
        print("[Arm] Moving arm...")

        # ✅ 여기서 RB 협동로봇에 음악 명령 전송
        send_rb_command(MUSIC_COMMAND)

        arm_path = os.path.expanduser("~/rbpodo_kdh/build/practice2_251015")
        subprocess.run([arm_path], check=True)

        time.sleep(1.5)
        print("[Arm] Done.")
        sock.sendto(b"ARM_DONE_FOOD2", (UDP_IP, MAIN_PORT))
