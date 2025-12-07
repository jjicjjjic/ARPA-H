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

    if msg == "m5_hand": # grasp_spoon_start_main
        print("[Hand] m5_hand")
        subprocess.run(
            "source ~/anaconda3/etc/profile.d/conda.sh && conda deactivate && "
            "cd ~/hand_3g/src/DELTO_ROS2/delto_3f_driver/delto_3f_driver && "
            "python comoral_grasp1.py",
            shell=True,
            executable="/bin/bash",
        )
        time.sleep(1)
        subprocess.run(
            "source ~/anaconda3/etc/profile.d/conda.sh && conda deactivate && "
            "cd ~/hand_3g/src/DELTO_ROS2/delto_3f_driver/delto_3f_driver && "
            "python comoral_grasp2.py",
            shell=True,
            executable="/bin/bash",
        )
        time.sleep(0.1)
        sock.sendto(b"m6", (UDP_IP, MAIN_PORT))

    elif msg == "c2_hand": # grasp_comoral_start_main
        print("[Hand] c2_hand")
        subprocess.run(
            "source ~/anaconda3/etc/profile.d/conda.sh && conda deactivate && "
            "cd ~/hand_3g/src/DELTO_ROS2/delto_3f_driver/delto_3f_driver && "
            "python comoral_grasp1.py",
            shell=True,
            executable="/bin/bash",
        )
        time.sleep(1)
        subprocess.run(
            "source ~/anaconda3/etc/profile.d/conda.sh && conda deactivate && "
            "cd ~/hand_3g/src/DELTO_ROS2/delto_3f_driver/delto_3f_driver && "
            "python comoral_grasp2.py",
            shell=True,
            executable="/bin/bash",
        )
        time.sleep(1)
        sock.sendto(b"c3", (UDP_IP, MAIN_PORT))

    elif msg == "c6_hand": # release_comoral_start_main
        print("[Hand] c6_hand")
        subprocess.run(
            "source ~/anaconda3/etc/profile.d/conda.sh && conda deactivate && "
            "cd ~/hand_3g/src/DELTO_ROS2/delto_3f_driver/delto_3f_driver && "
            "python default.py",
            shell=True,
            executable="/bin/bash",
        )
        time.sleep(1)
        sock.sendto(b"c7", (UDP_IP, MAIN_PORT))

################# Brush finish #############################

################# Reposition start #########################

    elif msg == "r1_hand": # cushion_before_main
        print("[Hand] r1_hand")
        subprocess.run(
            "source ~/anaconda3/etc/profile.d/conda.sh && conda deactivate && "
            "cd ~/hand_3g/src/DELTO_ROS2/delto_3f_driver/delto_3f_driver && "
            "python cushion_before.py",
            shell=True,
            executable="/bin/bash",
        )
        time.sleep(1)

    elif msg == "r2_hand": # grasp_cushion1_start_main
        print("[Hand] r2_hand")
        subprocess.run(
            "source ~/anaconda3/etc/profile.d/conda.sh && conda deactivate && "
            "cd ~/hand_3g/src/DELTO_ROS2/delto_3f_driver/delto_3f_driver && "
            "python comoral_grasp2.py",
            shell=True,
            executable="/bin/bash",
        )
        time.sleep(1)
        sock.sendto(b"r3", (UDP_IP, MAIN_PORT))


    elif msg == "r4_hand": # release_cushion1_start_main
        print("[Hand] r4_hand")
        subprocess.run(
            "source ~/anaconda3/etc/profile.d/conda.sh && conda deactivate && "
            "cd ~/hand_3g/src/DELTO_ROS2/delto_3f_driver/delto_3f_driver && "
            "python cushion_before.py",
            shell=True,
            executable="/bin/bash",
        )
        time.sleep(1)
        sock.sendto(b"r5", (UDP_IP, MAIN_PORT))

    elif msg == "r6_hand": # grasp_cushion2_start_main
        print("[Hand] r6_hand")
        subprocess.run(
            "source ~/anaconda3/etc/profile.d/conda.sh && conda deactivate && "
            "cd ~/hand_3g/src/DELTO_ROS2/delto_3f_driver/delto_3f_driver && "
            "python comoral_grasp2.py",
            shell=True,
            executable="/bin/bash",
        )
        time.sleep(1)
        sock.sendto(b"r7", (UDP_IP, MAIN_PORT))

    elif msg == "r8_hand": # release_cushion2_start_main
        print("[Hand] r8_hand")
        subprocess.run(
            "source ~/anaconda3/etc/profile.d/conda.sh && conda deactivate && "
            "cd ~/hand_3g/src/DELTO_ROS2/delto_3f_driver/delto_3f_driver && "
            "python cushion_before.py",
            shell=True,
            executable="/bin/bash",
        )
        time.sleep(1)
        sock.sendto(b"r9", (UDP_IP, MAIN_PORT))
