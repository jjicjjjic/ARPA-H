import socket
import threading
import time
import tkinter as tk
from tkinter import ttk
import subprocess
import os
import serial

# UDP_IP = "127.0.0.1"
BIND_IP = "0.0.0.0"
TARGET_IP="127.0.0.1"
MAIN_PORT = 50000
MODULES = {"mobile": 50001, "arm": 50002, "camera": 50003, "hand": 50004, "robotUI": 50005}
task_mode = "default"
chewing_start_num = 0
chewing_end_num = 0
food_num = 0
pressure_on = 0
vision_reposition = 0
vision_fall_start = 0
vision_fall_finish = 0

status = {name: "Idle" for name in MODULES}
start_times = {name: None for name in MODULES}
durations = {name: None for name in MODULES}

recv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# recv_sock.bind((UDP_IP, MAIN_PORT))
recv_sock.bind((BIND_IP, MAIN_PORT))
recv_sock.settimeout(0.1)

def send_command(target, message):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # sock.sendto(message.encode(), (UDP_IP, MODULES[target]))
    sock.sendto(message.encode(), (TARGET_IP, MODULES[target]))
    sock.close()
    print(f"[Send] {target}: {message}")

class RobotGUI:
    def __init__(self):
        # ---------------------------
        # Arduino Serial Connect 추가
        # ---------------------------
        # try:
        #     # 리눅스 예: '/dev/ttyACM0'
        #     # 윈도우 예: 'COM6'
        #     self.arduino = serial.Serial('/dev/ttyUSB0', 115200, timeout=0.1)
        #     print("[Arduino] Serial connected successfully")
        # except Exception as e:
        #     self.arduino = None
        #     print(f"[Arduino] Serial connection failed: {e}")

        try:
            self.arduino_UI = serial.Serial('/dev/ttyUSB1', 115200, timeout=0.1)
            print("[Arduino MAIN] connected: /dev/ttyUSB1")
        except:
            self.arduino_UI = None

        try:
            self.arduino_docking = serial.Serial('/dev/ttyACM0', 9600, timeout=0.1)
            print("[Arduino SENSOR] connected: /dev/ttyACM0")
        except:
            self.arduino_docking = None


        # ---------------------------
        # 기존 GUI 초기화 부분
        # ---------------------------
        self.root = tk.Tk()
        self.root.title("Robot System Monitor (Unified Command Input)")
        self.root.geometry("650x480")
        self.root.configure(bg="white")
        self.chewing_start_num = 1
        self.chewing_end_num = 0
        self.food_num = 1
        self.pressure_on = 0
        self.vision_reposition = 0
        self.vision_fall_start = 0
        self.vision_fall_finish = 0
        self.task_mode = "meal"

        ttk.Label(self.root, text="Robot System Monitor", font=("Arial", 15, "bold")).pack(pady=10)

        # --- TreeView for module status ---
        self.tree = ttk.Treeview(self.root, columns=("Status", "Duration (s)"), show="headings", height=6)
        self.tree.heading("Status", text="Status")
        self.tree.heading("Duration (s)", text="Duration (s)")
        self.tree.column("Status", anchor="center", width=120)
        self.tree.column("Duration (s)", anchor="center", width=120)
        self.tree.pack(pady=5)

        for name in MODULES.keys():
            self.tree.insert("", tk.END, iid=name, values=[status[name], "—"])

        self.countdown_label = ttk.Label(self.root, text="Next step countdown: —", font=("Arial", 12))
        self.countdown_label.pack(pady=10)

        # --- Command entry box ---
        ttk.Label(self.root, text="Type a command and press Enter:", font=("Arial", 11)).pack(pady=5)
        self.command_entry = ttk.Entry(self.root, width=50)
        self.command_entry.pack(pady=5)
        self.command_entry.bind("<Return>", self.process_input)

        self.feedback_box = tk.Text(self.root, height=8, width=70)
        self.feedback_box.pack(pady=10)
        self.feedback_box.insert(tk.END, "Command log:\n")
        self.feedback_box.configure(state="disabled")

    # -----------------------------------
    # 공통 로그 함수
    def log(self, msg):
        self.feedback_box.configure(state="normal")
        self.feedback_box.insert(tk.END, msg + "\n")
        self.feedback_box.configure(state="disabled")
        self.feedback_box.see(tk.END)
        print(msg)

    # -----------------------------------
    # 공통 command handler (keyboard + UDP 모두 이 함수 사용)
    def handle_command(self, cmd):
        # chewing_num = 1
        """모든 입력(UDP/키보드)을 여기서 처리"""
        cmd = cmd.strip()
        if not cmd:
            return

        self.log(f"[Command] {cmd}")

    # ------------------------------------------------- Main -----------------------------------------------------------------------------

    # ------------------------------------------------- Meal -----------------------------------------------------------------------------

        if cmd == "button1_on" and self.task_mode == "default":
            self.start_sequence()
            self.task_mode = "meal"
            # self.start_next("arm", "move_to_bed_start_sound")
            # self.mark_done("arm")
            # self.countdown(0.01)
            # self.start_next("mobile", "move_to_bed_start_main")
            # subprocess.run(os.path.expanduser("~/ccmedia/ccmedia_R01"), shell=True, check=True)

        # elif cmd == "move_to_bed_finish_mobile" and self.task_mode == "meal":
        #     self.mark_done("mobile")
        #     self.countdown(0.01)
        #     self.start_next("arm", "move_to_bed_finish_sound")
        #     self.countdown(0.01)
        #     self.start_next("arm", "dock_on_start_sound")
        #     self.countdown(0.01)
        #     self.start_next("mobile", "dock_on_start_main")

        # elif cmd == "dock_on_finish_mobile" and self.task_mode == "meal":
        #     self.mark_done("mobile")
        #     self.countdown(0.01)
        #     self.start_next("arm", "dock_on_finish_sound")

        elif cmd == "button2_on" and self.task_mode == "meal":
            self.start_next("arm", "meal_start_sound")
            subprocess.run([os.path.expanduser("~/ccmedia/ccmedia_R02")], check=True)
            self.countdown(1)
            self.start_next("arm", "move_to_spoon_start_main")

        elif cmd == "move_to_spoon_finish_arm" and self.task_mode == "meal":
            self.mark_done("arm")
            self.countdown(0.01)
            self.start_next("hand", "grasp_spoon_start_main")

        elif cmd == "grasp_spoon_finish_hand" and self.task_mode == "meal":
            self.mark_done("hand")
            self.countdown(0.01)
            self.start_next("arm", "move_to_food1_start_main")
            self.food_num = 1

        elif cmd == "move_to_food1_finish_arm" and self.task_mode == "meal":
            self.mark_done("arm")
            self.countdown(6)
            self.start_next("arm", "chewing_sound")
            self.countdown(6)
            self.chewing_start_num = 1

        elif cmd == "chewing_sound_finish_arm" and self.chewing_start_num == 1 and self.food_num == 1:
            self.start_next("arm", "move_from_food1_to_fix_start_main")

        elif cmd == "move_from_food1_to_fix_finish_arm" and self.task_mode == "meal":
            self.mark_done("arm")
            self.countdown(0.01)
            self.start_next("arm", "move_to_food2_start_main")
            self.food_num = 2
            self.countdown(6)
            self.chewing_end_num = 1

        elif cmd == "move_to_food2_finish_arm" and self.chewing_end_num == 1 and self.food_num == 2:
            self.mark_done("arm")
            self.countdown(1)
            self.start_next("arm", "move_from_food2_to_mouth_start_main")

        elif cmd == "move_from_food2_to_mouth_finish_arm" and self.chewing_end_num == 1 and self.food_num == 2:
            self.mark_done("arm")
            self.countdown(6)
            self.start_next("arm", "chewing_sound")
            self.countdown(6)
            self.chewing_start_num = 2

        elif cmd == "chewing_sound_finish_arm" and self.chewing_start_num == 2 and self.food_num == 2:
            self.start_next("arm", "move_from_mouth2_to_fix_start_main")

        elif cmd == "move_from_mouth2_to_fix_finish_arm" and self.task_mode == "meal":
            self.mark_done("arm")
            self.countdown(0.01)
            self.start_next("arm", "move_to_food3_start_main")
            self.food_num = 3
            self.countdown(6)
            self.chewing_end_num = 2

        elif cmd == "move_to_food3_finish_arm" and self.chewing_end_num == 2 and self.food_num == 3:
            self.mark_done("arm")
            self.countdown(1)
            self.start_next("arm", "move_from_food3_to_mouth_start_main")

        elif cmd == "move_from_food3_to_mouth_finish_arm" and self.chewing_end_num == 2 and self.food_num == 3:
            self.mark_done("arm")
            self.countdown(6)
            self.start_next("arm", "chewing_sound")
            self.countdown(6)
            self.chewing_start_num = 3

        elif cmd == "chewing_sound_finish_arm" and self.chewing_start_num == 3 and self.food_num == 3:
            self.start_next("arm", "move_from_mouth3_to_fix_start_main")

        elif cmd == "move_from_mouth3_to_fix_finish_arm" and self.task_mode == "meal":
            self.mark_done("arm")
            self.countdown(0.01)
            self.start_next("arm", "move_to_food4_start_main")
            self.food_num = 4
            self.countdown(6)
            self.chewing_end_num = 3

        elif cmd == "move_to_food4_finish_arm" and self.chewing_end_num == 3 and self.food_num == 4:
            self.mark_done("arm")
            self.countdown(1)
            self.start_next("arm", "move_from_food4_to_mouth_start_main")

        elif cmd == "move_from_food4_to_mouth_finish_arm" and self.chewing_end_num == 3 and self.food_num == 4:
            self.mark_done("arm")
            self.countdown(6)
            self.start_next("arm", "chewing_sound")
            self.countdown(6)
            self.chewing_start_num = 4

        elif cmd == "chewing_sound_finish_arm" and self.chewing_start_num == 4 and self.food_num == 4:
            self.start_next("arm", "move_from_mouth4_to_fix_start_main")

        elif cmd == "move_from_mouth4_to_fix_finish_arm" and self.task_mode == "meal":
            self.mark_done("arm")
            self.countdown(0.01)
            self.start_next("arm", "move_to_food5_start_main")
            self.food_num = 5
            self.countdown(6)
            self.chewing_end_num = 4

        elif cmd == "move_to_food5_finish_arm" and self.chewing_end_num == 4 and self.food_num == 5:
            self.mark_done("arm")
            self.countdown(1)
            self.start_next("arm", "move_from_food5_to_mouth_start_main")

        elif cmd == "move_from_food5_to_mouth_finish_arm" and self.chewing_end_num == 4 and self.food_num == 5:
            self.mark_done("arm")
            self.countdown(6)
            self.start_next("arm", "chewing_sound")
            self.countdown(6)
            self.chewing_start_num = 5

        elif cmd == "chewing_sound_finish_arm" and self.chewing_start_num == 5 and self.food_num == 5:
            self.start_next("arm", "move_from_mouth5_to_fix_start_main")

        elif cmd == "move_from_mouth5_to_fix_finish_arm" and self.task_mode == "meal":
            self.mark_done("arm")
            self.countdown(0.01)
            self.start_next("arm", "move_to_food6_start_main")
            self.food_num = 6
            self.countdown(6)
            self.chewing_end_num = 5

        elif cmd == "move_to_food6_finish_arm" and self.chewing_end_num == 5 and self.food_num == 6:
            self.mark_done("arm")
            self.countdown(1)
            self.start_next("arm", "move_from_food6_to_mouth_start_main")

        elif cmd == "move_from_food6_to_mouth_finish_arm" and self.chewing_end_num == 5 and self.food_num == 6:
            self.mark_done("arm")
            self.countdown(6)
            self.start_next("arm", "chewing_sound")
            self.countdown(6)
            self.chewing_start_num = 6

        elif cmd == "chewing_sound_finish_arm" and self.chewing_start_num == 6 and self.food_num == 6:
            self.start_next("arm", "move_from_mouth6_to_fix_start_main")
        

        elif cmd == "chewing_start_outside" and self.task_mode == "meal":
            print("chewing_start_outside success")
            
        elif cmd == "chewing_end_outside" and self.task_mode == "meal":
            print("chewing_end_outside success")

            
######################################################
        elif cmd == "chewing_problem_outside" and self.task_mode == "meal":
            print("chewing_problem_outside success")
            self.start_next("arm", "chewing_problem_sound")
            self.countdown(5)
#########################################################

        elif cmd == "button2_off" and self.task_mode == "meal":
            self.mark_done("arm")
            subprocess.run([os.path.expanduser("~/ccmedia/ccmedia_R03")], check=True)
            self.countdown(0.01)
            self.start_next("arm", "move_from_food_to_default_arm_start_main")
            self.countdown(1.5)
            self.start_next("arm", "meal_finish_sound")
            self.task_mode = "default"

########################## Meal finish #############################

########################## Brush start #############################

        elif cmd == "button3_on" and self.task_mode == "default":
            self.task_mode = "brush"
            subprocess.run([os.path.expanduser("~/ccmedia/ccmedia_R06")], check=True)
            self.countdown(0.01)
            self.start_next("arm", "brush_start_sound")
            self.countdown(0.01)
            self.start_next("arm", "move_from_default_to_comoral_start_main")

        elif cmd == "move_from_default_to_comoral_finish_arm" and self.task_mode == "brush":
            self.mark_done("arm")
            self.countdown(0.01)
            self.start_next("hand", "grasp_comoral_start_main")

        elif cmd == "grasp_comoral_finish_hand" and self.task_mode == "brush":
            self.mark_done("hand")
            self.countdown(0.01)
            self.start_next("arm", "move_cormal_to_mouth_start_main")

        elif cmd == "move_cormal_to_mouth_finish_arm" and self.task_mode == "brush":
            self.mark_done("arm")
            self.countdown(0.01)
            self.start_next("arm", "bite_cormal_sound")

        elif cmd == "button3_off" and self.task_mode == "brush":
            self.start_next("arm", "brush_finish_sound")
            subprocess.run([os.path.expanduser("~/ccmedia/ccmedia_R07")], check=True)
            self.countdown(0.01)
            self.start_next("arm", "move_from_mouth_to_comoral_start_main")

        elif cmd == "move_from_mouth_to_comoral_finish_arm" and self.task_mode == "brush":
            self.mark_done("arm")
            self.countdown(0.01)
            self.start_next("hand", "release_comoral_start_main")

        elif cmd == "release_comoral_finish_hand" and self.task_mode == "brush":
            self.mark_done("hand")
            self.countdown(0.01)
            self.start_next("arm", "move_from_comoral_to_default_start_main")
            self.countdown(0.01)
            self.start_next("arm", "brush_finish_sound")
            self.task_mode = "default"

# -------------------- mobile robot go home --------------------------------------------

        elif cmd == "button1_off":
            self.mark_done("arm")
            self.start_next("arm", "dock_off_start_sound")
            self.countdown(0.01)
            self.start_next("mobile", "dock_off_start_main")

        elif cmd == "dock_off_finish_mobile":
            self.mark_done("mobile")
            self.countdown(0.01)
            self.start_next("arm", "dock_off_finish_sound")
            self.countdown(0.01)
            self.start_next("arm", "move_to_charger_start_sound")
            self.countdown(0.01)
            self.start_next("mobile", "move_to_charger_start_main")

        elif cmd == "move_to_charger_finish_mobile":
            self.mark_done("mobile")
            self.countdown(0.01)
            self.start_next("arm", "move_to_charger_finish_sound")

##################### Brush finish #############################

##################### Reposition start #########################

        elif cmd == "change_pressure_outside" and self.task_mode == "default":
            print("pressure_outside success")
            self.pressure_on = 1
            self.task_mode == "reposition"

        elif cmd == "button1_on" and self.pressure_on == 1 and self.task_mode == "reposition":
            self.start_next("arm", "move_to_bed_start_sound")
            subprocess.run(os.path.expanduser("~/ccmedia/ccmedia_R09"), shell=True, check=True)
            self.mark_done("mobile")
            self.countdown(0.01)
            self.start_next("mobile", "move_to_bed_start_main")

        elif cmd == "move_to_bed_finish_mobile" and self.task_mode == "reposition":
            self.mark_done("mobile")
            self.countdown(0.01)
            self.start_next("arm", "move_to_bed_finish_sound")
            self.countdown(1.5)
            self.start_next("arm", "dock_on_start_sound")
            self.countdown(0.01)
            self.start_next("mobile", "dock_on_start_main")

        elif cmd == "dock_on_finish_mobile" and self.task_mode == "reposition":
            self.mark_done("mobile")
            self.countdown(0.01)
            self.start_next("arm", "dock_on_finish_sound")

        elif cmd == "button4_on" and self.task_mode == "reposition":
            subprocess.run([os.path.expanduser("~/ccmedia/ccmedia_R10")], check=True)
            self.countdown(0.01)
            self.start_next("arm", "reposition_start_sound")
            self.countdown(1.5)
            self.start_next("arm", "move_from_default_to_cushion1_start_main")
            self.countdown(0.01)
            self.start_next("hand", "cushion_before_main")

        elif cmd == "change_vision_outside" and self.task_mode == "reposition":
            print("change vision outside success")
            self.vision_reposition = 1

        elif cmd == "move_from_default_to_cushion1_finish_arm" and self.vision_reposition == 1 and self.task_mode == "reposition":
            self.countdown(0.01)
            self.start_next("hand", "grasp_cushion1_start_main")

        elif cmd == "grasp_cushion1_finish_hand" and self.task_mode == "reposition":
            self.mark_done("hand")
            self.countdown(0.01)
            self.start_next("arm", "move_from_cushion1_to_back_start_main")

        elif cmd == "move_from_cushion1_to_back_finish_arm" and self.task_mode == "reposition":
            self.mark_done("arm")
            self.countdown(0.01)
            self.start_next("hand", "release_cushion1_start_main")

        elif cmd == "release_cushion1_finish_hand" and self.task_mode == "reposition":
            self.mark_done("hand")
            self.countdown(0.01)
            self.start_next("arm", "move_from_back_to_cushion2_start_main")

        elif cmd == "move_from_back_to_cushion2_finish_arm" and self.task_mode == "reposition":
            self.mark_done("arm")
            self.countdown(0.01)
            self.start_next("hand", "grasp_cushion2_start_main")

        elif cmd == "grasp_cushion2_finish_hand" and self.task_mode == "reposition":
            self.mark_done("hand")
            self.countdown(0.01)
            self.start_next("arm", "move_from_cushion2_to_leg_start_main")

        elif cmd == "move_from_cushion2_to_leg_finish_arm" and self.task_mode == "reposition":
            self.mark_done("arm")
            self.countdown(0.01)
            self.start_next("hand", "release_cushion2_start_main")

        elif cmd == "release_cushion2_finish_hand" and self.task_mode == "reposition":
            self.mark_done("hand")
            self.countdown(0.01)
            self.start_next("arm", "move_from_leg_to_fix_start_main")

        elif cmd == "button4_off" and self.task_mode == "reposition":
            subprocess.run([os.path.expanduser("~/ccmedia/ccmedia_R11")], check=True)
            self.mark_done("arm")
            self.countdown(0.01)
            self.start_next("arm", "reposition_finish_sound")
            self.countdown(1.5)
            self.start_next("arm", "move_from_back_to_default_start_main")
            subprocess.run([os.path.expanduser("~/ccmedia/ccmedia_R12")], check=True)
            self.task_mode = "default"

#################### Reposition finish #########################

################### Fall prevention start ######################

        elif cmd == "fall1_outside" and self.task_mode == "default":
            print("fall1_outside success")
            self.vision_fall_start = 1
            self.task_mode == "fall"

        elif cmd == "fall2_outside" and self.task_mode == "default":
            print("fall2_outside success")
            self.vision_fall_start = 2
            self.task_mode == "fall"

        elif cmd == "fall3_outside" and self.task_mode == "default":
            print("fall3_outside success")
            self.vision_fall_start = 3
            self.task_mode == "fall"

        elif cmd == "fall_finish_outside" and self.task_mode == "fall":
            print("fall_finish_outside success")
            self.vision_fall_finish = 1

        elif self.vision_fall_start == 1 and self.task_mode == "fall":
            self.start_next("arm", "move_to_bed_start_sound")
            self.arduino_UI.write(b"button1_on_pc\n")
            subprocess.run([os.path.expanduser("~/ccmedia/ccmedia_R16")], check=True)
            self.countdown(0.01)
            self.start_next("mobile", "move_to_gap1_start_main")

        elif self.vision_fall_start == 2 and self.task_mode == "fall":
            self.start_next("arm", "move_to_bed_start_sound")
            self.arduino_UI.write(b"button1_on_pc\n")
            subprocess.run([os.path.expanduser("~/ccmedia/ccmedia_R16")], check=True)
            self.countdown(0.01)
            self.start_next("mobile", "move_to_gap2_start_main")

        elif self.vision_fall_start == 3 and self.task_mode == "fall":
            self.start_next("arm", "move_to_bed_start_sound")
            self.arduino_UI.write(b"button1_on_pc\n")
            subprocess.run([os.path.expanduser("~/ccmedia/ccmedia_R16")], check=True)
            self.countdown(0.01)
            self.start_next("mobile", "move_to_gap3_start_main")

        elif cmd == "move_to_gap1_finish_mobile" and self.vision_fall_start == 1 and self.task_mode == "fall":
            self.mark_done("mobile")
            self.countdown(0.01)
            self.start_next("arm", "prevent_fall1_posture_start_main")
            self.countdown(0.01)
            self.start_next("arm", "dock_on_start_sound")
            self.countdown(0.01)
            self.start_next("mobile", "dock_on_start_main")
            self.countdown(5)

        elif cmd == "move_to_gap2_finish_mobile" and self.vision_fall_start == 2 and self.task_mode == "fall":
            self.mark_done("mobile")
            self.countdown(0.01)
            self.start_next("arm", "prevent_fall2_posture_start_main")
            self.countdown(0.01)
            self.start_next("arm", "dock_on_start_sound")
            self.countdown(0.01)
            self.start_next("mobile", "dock_on_start_main")
            self.countdown(5)

        elif cmd == "move_to_gap3_finish_mobile" and self.vision_fall_start == 3 and self.task_mode == "fall":
            self.mark_done("mobile")
            self.countdown(0.01)
            self.start_next("arm", "prevent_fall3_posture_start_main")
            self.countdown(0.01)
            self.start_next("arm", "dock_on_start_sound")
            self.countdown(0.01)
            self.start_next("mobile", "dock_on_start_main")
            self.countdown(5)

        elif cmd == "dock_on_finish_mobile" and self.task_mode == "fall":
            self.mark_done("mobile")
            self.countdown(0.01)
            self.start_next("arm", "dock_on_finish_sound")

        elif cmd == "prevent_fall1_posture_finish_arm" and self.task_mode == "fall":
            self.mark_done("mobile")
            self.countdown(0.01)
            self.start_next("arm", "warning_sound")

        elif cmd == "prevent_fall2_posture_finish_arm" and self.task_mode == "fall":
            self.mark_done("mobile")
            self.countdown(0.01)
            self.start_next("arm", "warning_sound")

        elif cmd == "prevent_fall3_posture_finish_arm" and self.task_mode == "fall":
            self.mark_done("mobile")
            self.countdown(0.01)
            self.start_next("arm", "warning_sound")

        elif self.vision_fall_start == 1 and self.vision_fall_finish == 1 and self.task_mode == "fall":
            self.countdown(0.01)
            self.start_next("arm", "move_from_gap1_to_default_main")

        elif self.vision_fall_start == 2 and self.vision_fall_finish == 1 and self.task_mode == "fall":
            self.countdown(0.01)
            self.start_next("arm", "move_from_gap2_to_default_main")

        elif self.vision_fall_start == 3 and self.vision_fall_finish == 1 and self.task_mode == "fall":
            self.countdown(0.01)
            self.start_next("arm", "move_from_gap3_to_default_main")


################################################################

        # elif cmd == "button1_off":
        #     # self.mark_done("arm")
        #     self.countdown(1)
        #     self.start_next("mobile", "dock_off_start_main")
        #     self.countdown(1)
        #     self.start_next("arm", "dock_off_start_sound")

        # elif cmd == "dock_off_finish_mobile":
        #     self.mark_done("mobile")
        #     self.countdown(1)
        #     self.start_next("arm", "dock_off_finish_sound")
        #     self.countdown(1)
        #     self.start_next("mobile", "move_to_charger_start_main")
        #     self.countdown(1)
        #     self.start_next("arm", "move_to_charger_start_sound")

        # elif cmd == "move_to_charger_finish_mobile":
        #     self.mark_done("mobile")
        #     self.countdown(1)
        #     self.start_next("arm", "move_to_charger_finish_sound")

        ################linear motor order (PC -> Arduino) ###################

        elif cmd == "M 22 29":
            if self.arduino_docking:
                self.arduino_docking.write(b"M 22 29\n")
            self.log("[PC → Linear motor] Docking ON")

        elif cmd == "H":
            if self.arduino_docking:
                self.arduino_docking.write(b"H\n")
            self.log("[PC → Linear motor] Docking OFF")

        ################### Button Order (PC → Arduino) ######################

        elif cmd == "button1_on_pc":
            if self.arduino_UI:
                self.arduino_UI.write(b"button1_on_pc\n")
            self.log("[PC → Arduino] LED1 ON")

        elif cmd == "button1_off_pc":
            if self.arduino_UI:
                self.arduino_UI.write(b"button1_off_pc\n")
            self.log("[PC → Arduino] LED1 OFF")

        elif cmd == "button2_on_pc":
            if self.arduino_UI:
                self.arduino_UI.write(b"button2_on_pc\n")
            self.log("[PC → Arduino] LED2 ON")

        elif cmd == "button2_off_pc":
            if self.arduino_UI:
                self.arduino_UI.write(b"button2_off_pc\n")
            self.log("[PC → Arduino] LED2 OFF")

        elif cmd == "button3_on_pc":
            if self.arduino_UI:
                self.arduino_UI.write(b"button3_on_pc\n")
            self.log("[PC → Arduino] LED3 ON")

        elif cmd == "button3_off_pc":
            if self.arduino_UI:
                self.arduino_UI.write(b"button3_off_pc\n")
            self.log("[PC → Arduino] LED3 OFF")

        elif cmd == "button4_on_pc":
            if self.arduino_UI:
                self.arduino_UI.write(b"button4_on_pc\n")
            self.log("[PC → Arduino] LED4 ON")

        elif cmd == "button4_off_pc":
            if self.arduino_UI:
                self.arduino_UI.write(b"button4_off_pc\n")
            self.log("[PC → Arduino] LED4 OFF")


        else:
            self.log("[Unknown command] No action taken.")


    # -----------------------------------
    def process_input(self, event):
        """키보드 입력 처리"""
        cmd = self.command_entry.get()
        self.command_entry.delete(0, tk.END)
        self.handle_command(cmd)

    # -----------------------------------
    def listen_feedback(self):
        """UDP 수신 처리"""
        while True:
            try:
                data, _ = recv_sock.recvfrom(1024)
                msg = data.decode().strip()
                self.handle_command(msg)
            except socket.timeout:
                pass

    # -----------------------------------
    def update_gui(self):
        color_map = {"Idle": "#D3D3D3", "Working": "#FFD700", "Done": "#90EE90"}
        for name in MODULES.keys():
            st = status[name]
            dur = durations[name] if durations[name] is not None else "—"
            self.tree.item(name, values=[st, dur])
            self.tree.tag_configure(name, background=color_map.get(st, "white"))
            self.tree.item(name, tags=(name,))

    # -----------------------------------
    def start_sequence(self):
        self.log("[Trigger] Start sequence initiated")
        for k in status:
            status[k] = "Idle"
            durations[k] = None
        self.update_gui()

    # -----------------------------------
    def countdown(self, seconds):
        # for i in range(seconds, 0, -1):
        #     self.countdown_label.config(text=f"Next step countdown: {i} s")
        #     self.root.update()
        #     time.sleep(1)
        # self.countdown_label.config(text="Next step countdown: —")
        self.countdown_label.config(text=f"Next step countdown: {seconds:.1f} s")
        self.root.update()
        time.sleep(seconds)
        self.countdown_label.config(text="Next step countdown: —")

    # -----------------------------------
    def mark_done(self, module):
        status[module] = "Done"
        durations[module] = f"{time.time() - start_times[module]:.2f}"
        self.update_gui()

    # -----------------------------------
    def start_next(self, module, command):
        status[module] = "Working"
        start_times[module] = time.time()
        self.update_gui()
        send_command(module, command)

    # -----------------------------------
    def run(self):
        # listen thread를 여기서 실행 (GUI 완성 후)
        threading.Thread(target=self.listen_feedback, daemon=True).start()
        self.root.mainloop()

# -----------------------------------
if __name__ == "__main__":
    gui = RobotGUI()
    gui.run()
