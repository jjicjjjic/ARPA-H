import socket
import subprocess
import time

UDP_IP = "127.0.0.1"
PORT = 50004
MAIN_PORT = 50000

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, PORT))

print("[Hand] Ready.")

while True:
    data, addr = sock.recvfrom(1024)
    msg = data.decode().strip()

    if msg == "GRASP_FOOD1":
        print("[Hand] Grasping object...")

        # ✅ Conda 초기화 + deactivate + ROS2 환경 불러오기 + 실행
        subprocess.run(
            "source ~/anaconda3/etc/profile.d/conda.sh && conda deactivate && "
            "source /opt/ros/humble/setup.bash && "
            "source ~/hand_ws/install/setup.bash && "
            "ros2 run dg5f_driver grasp_251015.py",
            shell=True,
            executable="/bin/bash",
        )

        time.sleep(1.0)
        print("[Hand] Done grasping.")
        sock.sendto(b"HAND_DONE_FOOD1", (UDP_IP, MAIN_PORT))

    elif msg == "GRASP_FOOD2":
        print("[Hand] Grasping object...")

        # ✅ Conda 초기화 + deactivate + ROS2 환경 불러오기 + 실행
        subprocess.run(
            "source ~/anaconda3/etc/profile.d/conda.sh && conda deactivate && "
            "source /opt/ros/humble/setup.bash && "
            "source ~/hand_ws/install/setup.bash && "
            "ros2 run dg5f_driver release_251015.py",
            shell=True,
            executable="/bin/bash",
        )

        time.sleep(1.0)
        print("[Hand] Done grasping.")
        sock.sendto(b"HAND_DONE_FOOD2", (UDP_IP, MAIN_PORT))
