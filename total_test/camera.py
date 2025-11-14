import socket
import subprocess
import time

UDP_IP = "127.0.0.1"
PORT = 50003
MAIN_PORT = 50000

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, PORT))

print("[Camera] Ready.")

while True:
    data, addr = sock.recvfrom(1024)
    msg = data.decode().strip()

    if msg == "find_spoon_position_start_main":
        print("[Camera] find_spoon_position_start")
        env_python = "/home/nrel/anaconda3/envs/aruco_env/bin/python"
        aruco_script = "/home/nrel/aruco/aruco_multi_6d_kdh.py"
        # try:
        #     print("[Camera] Running aruco script in aruco_env...")
        #     subprocess.run(
        #         [env_python, aruco_script],
        #         check=True
        #     )
        # except subprocess.CalledProcessError as e:
        #     print(f"[Camera] Error while running aruco_env script: {e}")
        time.sleep(1.0)
        print("[Camera] find_spoon_position_finish")
        #send spoon position to arm and move arm
        #
        #
        #
        sock.sendto(b"find_spoon_position_finish_camera", (UDP_IP, MAIN_PORT))

    elif msg == "find_mouth_position_for_meal_start_main":
        print("[Camera] find_mouth_position_for_meal_start")
        env_python = "/home/nrel/anaconda3/envs/aruco_env/bin/python"
        aruco_script = "/home/nrel/aruco/aruco_multi_6d_kdh.py"
        # try:
        #     print("[Camera] Running aruco script in aruco_env...")
        #     subprocess.run(
        #         [env_python, aruco_script],
        #         check=True
        #     )
        # except subprocess.CalledProcessError as e:
        #     print(f"[Camera] Error while running aruco_env script: {e}")
        time.sleep(1.0)
        print("[Camera] find_mouth_position_for_meal_finish")
        #send mouth position to arm and move arm
        #
        #
        #
        sock.sendto(b"find_mouth_position_for_meal_finish_camera", (UDP_IP, MAIN_PORT))

    elif msg == "find_comoral_position_start_main":
        print("[Camera] find_comoral_position_start")
        env_python = "/home/nrel/anaconda3/envs/aruco_env/bin/python"
        aruco_script = "/home/nrel/aruco/aruco_multi_6d_kdh.py"
        # try:
        #     print("[Camera] Running aruco script in aruco_env...")
        #     subprocess.run(
        #         [env_python, aruco_script],
        #         check=True
        #     )
        # except subprocess.CalledProcessError as e:
        #     print(f"[Camera] Error while running aruco_env script: {e}")
        time.sleep(1.0)
        print("[Camera] find_comoral_position_finish")
        #send spoon position to arm and move arm
        #
        #
        #
        sock.sendto(b"find_comoral_position_finish_camera", (UDP_IP, MAIN_PORT))

    elif msg == "find_mouth_position_for_brush_start_main":
        print("[Camera] find_mouth_position_for_brush_start")
        env_python = "/home/nrel/anaconda3/envs/aruco_env/bin/python"
        aruco_script = "/home/nrel/aruco/aruco_multi_6d_kdh.py"
        # try:
        #     print("[Camera] Running aruco script in aruco_env...")
        #     subprocess.run(
        #         [env_python, aruco_script],
        #         check=True
        #     )
        # except subprocess.CalledProcessError as e:
        #     print(f"[Camera] Error while running aruco_env script: {e}")
        time.sleep(1.0)
        print("[Camera] find_mouth_position_for_brush_finish")
        #send mouth position to arm and move arm
        #
        #
        #
        sock.sendto(b"find_mouth_position_for_brush_finish_camera", (UDP_IP, MAIN_PORT))

    elif msg == "CAPTURE_FOOD":
        print("[Camera] Capturing image...")
        env_python = "/home/nrel/anaconda3/envs/aruco_env/bin/python"
        aruco_script = "/home/nrel/aruco/aruco_multi_6d_kdh.py"
        try:
            print("[Camera] Running aruco script in aruco_env...")
            subprocess.run(
                [env_python, aruco_script],
                check=True
            )
        except subprocess.CalledProcessError as e:
            print(f"[Camera] Error while running aruco_env script: {e}")
        time.sleep(1.0)
        print("[Camera] Image captured.")
        sock.sendto(b"CAMERA_DONE_FOOD", (UDP_IP, MAIN_PORT))
