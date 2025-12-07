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

        if cmd == "m1" or cmd == "button1_on": # cmd == "button1_on" and self.task_mode == "default":
            self.start_sequence()
            subprocess.run(os.path.expanduser("~/ccmedia/ccmedia_R01"), shell=True, check=True)
            self.start_next("arm", "m1_sound") # move_to_bed_start_sound
            self.countdown(0.01)
            self.start_next("mobile", "m1_mobile") # move_to_bed_start_main
            self.countdown(0.01)          

        elif cmd == "m2": # cmd == "move_to_bed_finish_mobile" and self.task_mode == "meal":
            self.start_next("arm", "m2_sound1") # move_to_bed_finish_sound
            self.countdown(3)
            self.start_next("arm", "m2_sound2") # dock_on_start_sound
            self.countdown(1)
            self.start_next("mobile", "m2_mobile") # dock_on_start_main
            self.countdown(0.01)

        elif cmd == "m3": # cmd == "dock_on_finish_mobile" and self.task_mode == "meal":
            self.start_next("arm", "m3_sound") # dock_on_finish_sound
            self.countdown(0.01)

        elif cmd == "m4" or cmd == "button2_on": # cmd == "button2_on" and self.task_mode == "meal":
            subprocess.run([os.path.expanduser("~/ccmedia/ccmedia_R02")], check=True)
            self.countdown(2)
            self.start_next("arm", "m4_sound") # meal_start_sound
            self.countdown(1.5)
            self.start_next("arm", "m4_arm") # move_to_spoon_start_main
            self.countdown(0.01)

        elif cmd == "m5": # cmd == "move_to_spoon_finish_arm" and self.task_mode == "meal":
            self.start_next("hand", "m5_hand") # grasp_spoon_start_main
            self.countdown(1)

        elif cmd == "m6": # cmd == "grasp_spoon_finish_hand" and self.task_mode == "meal":
            self.countdown(2)
            self.start_next("arm", "m6_arm") # move_to_food1_start_main
            self.countdown(6)

        elif cmd == "m7": # cmd == "move_to_food1_finish_arm" and self.task_mode == "meal":
            self.countdown(6)
            self.start_next("arm", "m7_sound") # chewing_sound
            self.countdown(6)

        elif cmd == "m8": # cmd == "chewing_sound_finish_arm" and self.chewing_start_num == 1 and self.food_num == 1:
            self.start_next("arm", "m8_arm") # move_from_food1_to_fix_start_main
            self.countdown(0.01)

        elif cmd == "m9": # cmd == "move_from_food1_to_fix_finish_arm" and self.task_mode == "meal":
            self.start_next("arm", "m9_arm") # move_to_food2_start_main
            self.countdown(6)

        elif cmd == "m10": # cmd == "move_to_food2_finish_arm" and self.chewing_end_num == 1 and self.food_num == 2:
            self.start_next("arm", "m10_arm") # move_from_food2_to_mouth_start_main
            self.countdown(1)

        elif cmd == "m11": # cmd == "move_from_food2_to_mouth_finish_arm" and self.chewing_end_num == 1 and self.food_num == 2:
            self.start_next("arm", "m11_sound") # chewing_sound
            self.countdown(6)

        elif cmd == "m12": # cmd == "chewing_sound_finish_arm" and self.chewing_start_num == 2 and self.food_num == 2:
            self.start_next("arm", "m12_arm") # move_from_mouth2_to_fix_start_main
            self.countdown(0.01)

        elif cmd == "m13": # cmd == "move_from_mouth2_to_fix_finish_arm" and self.task_mode == "meal":
            self.start_next("arm", "m13_arm") # move_to_food3_start_main
            self.countdown(6)

        elif cmd == "m14": # cmd == "move_to_food3_finish_arm" and self.chewing_end_num == 2 and self.food_num == 3:
            self.start_next("arm", "m14_arm") # move_from_food3_to_mouth_start_main
            self.countdown(1)

        elif cmd == "m15": # cmd == "move_from_food3_to_mouth_finish_arm" and self.chewing_end_num == 2 and self.food_num == 3:
            self.start_next("arm", "m15_sound") # chewing_sound
            self.countdown(6)

        elif cmd == "m16": # cmd == "chewing_sound_finish_arm" and self.chewing_start_num == 3 and self.food_num == 3:
            self.countdown(4)
            self.start_next("arm", "m16_arm") # move_from_mouth3_to_fix_start_main
            self.countdown(0.01)

        elif cmd == "m17": # cmd == "move_from_mouth3_to_fix_finish_arm" and self.task_mode == "meal":
            self.start_next("arm", "m17_arm") # move_to_food4_start_main
            self.countdown(6)

        elif cmd == "m18": # cmd == "move_to_food4_finish_arm" and self.chewing_end_num == 3 and self.food_num == 4:
            self.start_next("arm", "m18_arm") # move_from_food4_to_mouth_start_main
            self.countdown(6)

        elif cmd == "m19": # cmd == "move_from_food4_to_mouth_finish_arm" and self.chewing_end_num == 3 and self.food_num == 4:
            self.start_next("arm", "m19_sound") # chewing_sound
            self.countdown(6)

        elif cmd == "m20": # cmd == "chewing_sound_finish_arm" and self.chewing_start_num == 4 and self.food_num == 4:
            self.countdown(5)
            self.start_next("arm", "m20_arm") # move_from_mouth4_to_fix_start_main
            self.countdown(0.01)

        elif cmd == "m21": # cmd == "move_from_mouth4_to_fix_finish_arm" and self.task_mode == "meal":
            self.start_next("arm", "m21_arm") # move_to_food5_start_main
            self.countdown(6)

        elif cmd == "m22": # cmd == "move_to_food5_finish_arm" and self.chewing_end_num == 4 and self.food_num == 5:
            self.start_next("arm", "m22_arm") # move_from_food5_to_mouth_start_main
            self.countdown(6)

        elif cmd == "m23": # cmd == "move_from_food5_to_mouth_finish_arm" and self.chewing_end_num == 4 and self.food_num == 5:
            self.start_next("arm", "m23_sound") # chewing_sound
            self.countdown(6)

        elif cmd == "m24": # cmd == "chewing_sound_finish_arm" and self.chewing_start_num == 5 and self.food_num == 5:
            self.countdown(5)
            self.start_next("arm", "m24_arm") # move_from_mouth5_to_fix_start_main
            self.countdown(6)

        elif cmd == "m25": # cmd == "move_from_mouth5_to_fix_finish_arm" and self.task_mode == "meal":
            self.start_next("arm", "m25_arm") # move_to_food6_start_main
            self.countdown(6)

        elif cmd == "m26": # cmd == "move_to_food6_finish_arm" and self.chewing_end_num == 5 and self.food_num == 6:
            self.start_next("arm", "m26_arm") # move_from_food6_to_mouth_start_main
            self.countdown(6)

        elif cmd == "m27": # cmd == "move_from_food6_to_mouth_finish_arm" and self.chewing_end_num == 5 and self.food_num == 6:
            self.start_next("arm", "m27_sound") # chewing_sound
            self.countdown(6)

        elif cmd == "m28": # cmd == "chewing_sound_finish_arm" and self.chewing_start_num == 6 and self.food_num == 6:
            self.countdown(5)
            self.start_next("arm", "m28_arm") # move_from_mouth6_to_fix_start_main
            self.countdown(0.01)

        elif cmd == "m29" or cmd == "button2_off": # cmd == "button2_off" and self.task_mode == "meal":
            subprocess.run([os.path.expanduser("~/ccmedia/ccmedia_R03")], check=True)
            self.start_next("arm", "m29_sound") # move_from_food_to_default_arm_start_main
            self.countdown(1.5)
            self.start_next("arm", "m29_arm") # meal_finish_sound
            self.countdown(0.01)

######################################################
        elif cmd == "chewing_start_outside":
            print("chewing_start_outside success")
            
        elif cmd == "chewing_end_outside":
            print("chewing_end_outside success")

        elif cmd == "chewing_problem_outside":
            print("chewing_problem_outside success")
#########################################################

########################## Meal finish #############################

########################## Brush start #############################

        elif cmd == "c1" or cmd == "button3_on": # cmd == "button3_on" and self.task_mode == "default":
            subprocess.run([os.path.expanduser("~/ccmedia/ccmedia_R06")], check=True)
            self.start_next("arm", "c1_sound") # brush_start_sound
            self.countdown(2)
            self.start_next("arm", "c1_arm") # move_from_default_to_comoral_start_main
            self.countdown(2)

        elif cmd == "c2": # cmd == "move_from_default_to_comoral_finish_arm" and self.task_mode == "brush":
            self.start_next("hand", "c2_hand") # grasp_comoral_start_main
            self.countdown(1)

        elif cmd == "c3": # cmd == "grasp_comoral_finish_hand" and self.task_mode == "brush":
            self.start_next("arm", "c3_arm") # move_cormal_to_mouth_start_main
            self.countdown(2)

        elif cmd == "c4": # cmd == "move_cormal_to_mouth_finish_arm" and self.task_mode == "brush":
            self.countdown(5)
            self.start_next("arm", "c4_sound") # bite_cormal_sound
            self.countdown(2)

        elif cmd == "c5" or cmd == "button3_off": # cmd == "button3_off" and self.task_mode == "brush":
            subprocess.run([os.path.expanduser("~/ccmedia/ccmedia_R07")], check=True)
            self.start_next("arm", "c5_sound") # brush_finish_sound           
            self.countdown(2)
            self.start_next("arm", "c5_arm") # move_from_mouth_to_comoral_start_main
            self.countdown(2)

        elif cmd == "c6": # cmd == "move_from_mouth_to_comoral_finish_arm" and self.task_mode == "brush":
            self.start_next("hand", "c6_hand") # release_comoral_start_main
            self.countdown(2)

        elif cmd == "c7": # cmd == "release_comoral_finish_hand" and self.task_mode == "brush":
            self.start_next("arm", "c7_arm") # move_from_comoral_to_default_start_main
            self.countdown(2)

##################### Brush finish #############################

##################### Reposition start #########################

        elif cmd == "r1" or cmd == "button4_on": # cmd == "button4_on" and self.task_mode == "reposition":
            subprocess.run([os.path.expanduser("~/ccmedia/ccmedia_R10")], check=True)
            self.countdown(1)
            self.start_next("arm", "r1_sound") # reposition_start_sound
            self.countdown(1.5)
            self.start_next("hand", "r1_hand") # cushion_before_main
            self.countdown(1)
            self.start_next("arm", "r1_arm") # move_from_default_to_cushion1_start_main
            self.countdown(1)                

        elif cmd == "r2": # cmd == "move_from_default_to_cushion1_finish_arm" and self.vision_reposition == 1 and self.task_mode == "reposition":
            self.start_next("hand", "r2_hand") # grasp_cushion1_start_main
            self.countdown(1)

        elif cmd == "r3": # cmd == "grasp_cushion1_finish_hand" and self.task_mode == "reposition":
            self.start_next("arm", "r3_arm") # move_from_cushion1_to_back_start_main
            self.countdown(1)

        elif cmd == "r4": # cmd == "move_from_cushion1_to_back_finish_arm" and self.task_mode == "reposition":
            self.start_next("hand", "r4_hand") # release_cushion1_start_main
            self.countdown(1)

        elif cmd == "r5": # cmd == "release_cushion1_finish_hand" and self.task_mode == "reposition":
            self.start_next("arm", "r5_arm") # move_from_back_to_cushion2_start_main
            self.countdown(1)

        elif cmd == "r6": # cmd == "move_from_back_to_cushion2_finish_arm" and self.task_mode == "reposition": 
            self.start_next("hand", "r6_hand") # grasp_cushion2_start_main
            self.countdown(1)

        elif cmd == "r7": # cmd == "grasp_cushion2_finish_hand" and self.task_mode == "reposition":
            self.start_next("arm", "r7_arm") # move_from_cushion2_to_leg_start_main
            self.countdown(1)

        elif cmd == "r8": # cmd == "move_from_cushion2_to_leg_finish_arm" and self.task_mode == "reposition":
            self.start_next("hand", "r8_hand") # release_cushion2_start_main
            self.countdown(1)

        elif cmd == "r9": # cmd == "release_cushion2_finish_hand" and self.task_mode == "reposition":
            self.start_next("arm", "r9_arm") # move_from_leg_to_fix_start_main
            self.countdown(1)

        elif cmd == "r10" or cmd == "button4_off": # cmd == "button4_off" and self.task_mode == "reposition":
            subprocess.run([os.path.expanduser("~/ccmedia/ccmedia_R11")], check=True)
            self.start_next("arm", "r10_sound") # reposition_finish_sound
            self.countdown(1.5)
            self.start_next("arm", "r10_arm") # move_from_back_to_default_start_main
            subprocess.run([os.path.expanduser("~/ccmedia/ccmedia_R12")], check=True)

        elif cmd == "r11" or  cmd == "button1_off": # cmd == "button1_off":
            self.start_next("arm", "r11_sound") # dock_off_start_sound
            self.countdown(0.01)
            self.start_next("mobile", "r11_mobile") # dock_off_start_main
            self.countdown(0.01)

        elif cmd == "r12": # cmd == "dock_off_finish_mobile":
            self.start_next("arm", "r12_sound1") # dock_off_finish_sound
            self.countdown(3)
            self.start_next("arm", "r12_sound2") # move_to_charger_start_sound
            self.countdown(3)
            self.start_next("mobile", "r12_mobile") # move_to_charger_start_main
            self.countdown(1)

        elif cmd == "r13": # cmd == "move_to_charger_finish_mobile":
            self.start_next("arm", "r13_sound") # move_to_charger_finish_sound
            self.countdown(1)

######################################################
        elif cmd == "change_pressure_outside":
            print("pressure_outside success")

        elif cmd == "change_vision_outside":
            print("change vision outside success")
######################################################

#################### Reposition finish #########################

################### Fall prevention start ######################

        elif cmd == "f1": # self.vision_fall_start == 1 and self.task_mode == "fall":
            subprocess.run([os.path.expanduser("~/ccmedia/ccmedia_R16")], check=True)
            self.start_next("arm", "f1_sound") # move_to_bed_start_sound
            # self.arduino_UI.write(b"button1_on_pc\n")         
            self.countdown(0.01)
            self.start_next("mobile", "f1_mobile") # move_to_gap1_start_main
            self.countdown(0.01)

        elif cmd == "f2": # cmd == "move_to_gap1_finish_mobile" and self.vision_fall_start == 1 and self.task_mode == "fall":
            self.start_next("arm", "f2_arm") # prevent_fall1_posture_start_main
            self.countdown(1)

        elif cmd == "f3": # cmd == "prevent_fall1_posture_finish_arm" and self.task_mode == "fall":
            self.start_next("arm", "f3_sound") # warning_sound
            self.countdown(0.01)

        elif cmd == "f4": # self.vision_fall_start == 1 and self.vision_fall_finish == 1 and self.task_mode == "fall":
            self.start_next("arm", "f4_arm") # move_from_gap1_to_default_main
            self.countdown(1)

        elif cmd == "f5": # cmd == "button1_off":
            self.start_next("arm", "f5_sound") # move_to_charger_start_sound
            self.countdown(1)
            self.start_next("mobile", "f5_mobile") # move_to_charger_start_main
            self.countdown(0.01)            

        elif cmd == "f6": # cmd == "move_to_charger_finish_mobile":
            self.start_next("arm", "f6_sound") # move_to_charger_finish_sound
            self.countdown(0.01)

######################################################
        elif cmd == "Body_extruded":
            print("Body_extruded success")
######################################################

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
