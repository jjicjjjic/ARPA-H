import socket
import threading
import time
import tkinter as tk
from tkinter import ttk
import subprocess
import os

# UDP_IP = "127.0.0.1"
BIND_IP = "0.0.0.0"
TARGET_IP="127.0.0.1"
MAIN_PORT = 50000
MODULES = {"mobile": 50001, "arm": 50002, "camera": 50003, "hand": 50004, "robotUI": 50005}
chewing_num = 1
mode = 1
task = 0
task_meal = 0

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
        self.root = tk.Tk()
        self.root.title("Robot System Monitor (Unified Command Input)")
        self.root.geometry("650x480")
        self.root.configure(bg="white")
        self.chewing_num = 1
        self.mode = 1 # mode1: meal, mode2: brush, mode3: reposition, mode4: fall prevention
        self.task = 0
        self.task_meal = 0

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

        # ---- Main start condition ----

# Meal start

        if cmd == "button1_on":
            # self.task_meal += 1
            self.start_sequence()
            self.mark_done("mobile")
            self.countdown(1)
            self.start_next("arm", "move_to_bed_start_sound")
            subprocess.run(os.path.expanduser("~/ccmedia/ccmedia_R01"), shell=True, check=True)

        elif cmd == "move_to_bed_finish_mobile":
            self.mark_done("mobile")
            self.countdown(1)
            self.start_next("arm", "move_to_bed_finish_sound")
            self.countdown(1)
            self.start_next("mobile", "dock_on_start_main")
            self.countdown(1)
            self.start_next("arm", "dock_on_start_sound")

        elif cmd == "dock_on_finish_mobile":
            self.mark_done("mobile")
            self.countdown(1)
            self.start_next("arm", "dock_on_finish_sound")

#################### Meal start #############################

        elif cmd == "button2_on" and self.mode == 1 and self.task_meal == 0:
            self.task_meal += 1
            subprocess.run([os.path.expanduser("~/ccmedia/ccmedia_R02")], check=True)
            # self.mark_done("mobile")
            self.countdown(1)
            self.start_next("arm", "meal_start_sound")
            # self.countdown(1)
            # self.start_next("arm", "move_to_spoon_start_main")
            self.task_meal += 1

        elif cmd == "move_to_spoon_finish_arm" and self.task_meal == 2:
            self.task_meal += 1
            self.mark_done("arm")
        #     self.countdown(1)
        #     self.start_next("camera", "find_spoon_position_start_main")

        # elif cmd == "find_spoon_position_finish_camera":
        #     self.mark_done("camera")
        #     self.countdown(1)
        #     self.start_next("arm", "move_next_spoon_start_main")

        # elif cmd == "move_next_spoon_finish_arm":
        #     self.mark_done("arm")
            self.countdown(1)
            self.start_next("hand", "grasp_spoon_start_main")
            self.task_meal += 1


        elif cmd == "grasp_spoon_finish_hand" and self.task_meal == 4:
            self.task_meal += 1
            self.mark_done("hand")
            self.countdown(1)
            self.start_next("arm", "move_to_food1_start_main")
            self.task_meal += 1


        elif cmd == "move_to_food1_finish_arm" and self.task_meal == 6:
            self.task_meal += 1
            self.mark_done("arm")
            self.countdown(1)
            # chewing_num = 1
            self.start_next("arm", "chewing_sound")
            self.task_meal += 1

        elif cmd == "chewing_start_outside":
            print("chewing_start_outside success")
            if self.chewing_num == 1 and self.task_meal == 8:
                self.task_meal += 1
                # self.start_next("arm", "go_to_food_sound")
                # self.mark_done("arm")
                # print("suceess")
                # self.countdown(1)
                # self.start_next("arm", "chewing_sound")
                self.countdown(1)
                self.start_next("arm", "move_to_food2_start_main")
                self.task_meal += 1

        elif cmd == "move_to_food2_finish_arm" and self.task_meal == 10:
            self.task_meal += 1
            # self.task_meal += 1
            self.mark_done("arm")
            self.countdown(1)
            # self.start_next("arm", "chewing_sound")
            self.chewing_num += 1

        elif cmd == "chewing_end_outside":
            print("chewing_end_outside success")
            if self.chewing_num == 2 and self.task_meal == 12:
                self.task_meal += 1
                # self.start_next("arm", "go_to_food_sound")
                # self.mark_done("arm")
                self.chewing_num += 1
                self.countdown(1)
                self.start_next("arm", "move_from_food2_to_mouth_start_main")
                self.task_meal += 1


######################################################
        elif cmd == "chewing_problem_outside" and self.task_meal == 12:
            print("chewing_problem_outside success")
            self.countdown(1)
            self.start_next("arm", "chewing_problem_sound")

        # elif cmd == "swallowing_problem_outside":
        #     self.countdown(1)
        #     self.start_next("arm", "chewing_sound")



#########################################################
        elif cmd == "move_to_food3_finish_arm":
            self.mark_done("arm")
            self.countdown(1)
            self.start_next("arm", "move_to_food4_start_main")

        elif cmd == "move_to_food4_finish_arm":
            self.mark_done("arm")
            self.countdown(1)
            self.start_next("arm", "move_to_food5_start_main")

        elif cmd == "move_to_food5_finish_arm":
            self.mark_done("arm")
            self.countdown(1)
            self.start_next("arm", "move_to_food6_start_main")

        elif cmd == "move_to_food6_finish_arm":
            self.mark_done("arm")
            self.countdown(1)
            # self.start_next("arm", "move_to_food3_start_main")

        # elif cmd == "move_to_food1_finish_arm":
        #     self.mark_done("arm")
        #     self.countdown(1)
        #     self.start_next("camera", "find_mouth_position_for_meal_start_main")

        # elif cmd == "find_mouth_position_for_meal_finish_camera":
        #     self.mark_done("camera")
        #     self.countdown(1)
        #     self.start_next("arm", "move_front_mouth_for_meal_start_main")

        # elif cmd == "move_front_mouth_for_meal_finish_arm":
        #     self.mark_done("arm")
        #     self.countdown(1)
            # self.start_next("chew_sensor", "check_chewing_start_main")

        # elif cmd == "check_chewing_finish_chew_sensor":
        #     # self.mark_done("")
        #     self.chewing_num += 1
        #     self.countdown(1)
            # self.start_next("arm", f"move_to_food{self.chewing_num}_start_main")

        # elif cmd == f"move_to_food{self.chewing_num}_finish_arm":
            # self.mark_done("arm")
            # self.countdown(1)
            # self.start_next("chew_sensor", "check_chewing_start_main")

        elif cmd == "button2_off" and self.task_meal == 14:
            subprocess.run([os.path.expanduser("~/ccmedia/ccmedia_R03")], check=True)
            # self.mark_done("arm")
            self.countdown(1)
            self.start_next("arm", "move_from_food_to_default_arm_start_main")
            self.countdown(1)
            self.start_next("arm", "meal_finish_sound")
            subprocess.run([os.path.expanduser("~/ccmedia/ccmedia_R03")], check=True)

########################## Meal finish #############################

########################## Brush start #############################

        elif cmd == "button3_on":
            subprocess.run([os.path.expanduser("~/ccmedia/ccmedia_R06")], check=True)
            # self.mark_done("mobile")
            self.countdown(1)
            self.start_next("arm", "brush_start_sound")
            self.countdown(1)
            self.start_next("arm", "move_from_default_to_comoral_start_main")

        elif cmd == "move_from_default_to_comoral_finish_arm":
            self.mark_done("arm")
            self.countdown(1)
            # self.start_next("camera", "find_comoral_position_start_main")

        # elif cmd == "find_comoral_position_finish_camera":
        #     self.mark_done("camera")
            # # self.countdown(1)
            # self.start_next("arm", "move_next_comoral_start_main")

        # elif cmd == "move_next_comoral_finish_arm":
        #     self.mark_done("arm")
        #     self.countdown(1)
            self.start_next("hand", "grasp_comoral_start_main")

        elif cmd == "grasp_comoral_finish_hand":
            self.mark_done("hand")
            self.countdown(1)
            self.start_next("arm", "move_cormal_to_mouth_start_main")

        elif cmd == "move_cormal_to_mouth_finish_arm":
            self.mark_done("arm")
            self.countdown(1)
            self.start_next("camera", "find_mouth_position_for_brush_start_main")
            self.countdown(1)
            self.start_next("arm", "move_front_mouth_for_brush_start_main")

        # elif cmd == "find_mouth_position_for_brush_finish_camera":
        #     self.mark_done("camera")
        #     self.countdown(1)
        #     self.start_next("arm", "move_front_mouth_for_brush_start_main")

        elif cmd == "move_front_mouth_for_brush_finish_arm":
            self.mark_done("arm")
            self.countdown(1)
            # self.countdown(1)
            self.start_next("arm", "bite_cormal_sound")
            # self.start_next("chew_sensor", "check_chewing_start_main")

        elif cmd == "button3_off":
            subprocess.run([os.path.expanduser("~/ccmedia/ccmedia_R07")], check=True)
            # self.mark_done("mobile")
            self.countdown(1)
            self.start_next("arm", "brush_finish_sound")
            self.countdown(1)
            self.start_next("arm", "move_from_mouth_to_comoral_start_main")

        elif cmd == "move_from_mouth_to_comoral_finish_arm":
            self.mark_done("arm")
            self.countdown(1)
            self.start_next("hand", "release_comoral_start_main")

        elif cmd == "release_comoral_finish_hand":    
            self.mark_done("hand")
            self.countdown(1)
            self.start_next("arm", "move_from_comoral_to_default_start_main")
            self.countdown(1)
            self.start_next("arm", "brush_finish_sound")

##################### Brush finish #############################

##################### Reposition start #########################

        elif cmd == "change_pressure_outside":
            print("pressure_outside success")
            self.mode = 3
            self.task = 1

        # elif cmd == "button1_on" and self.mode == 3 and self.task == 1:
        #     self.task += 1
        #     print("mode 3")
        #     subprocess.run([os.path.expanduser("~/ccmedia/ccmedia_R09")], check=True)
        #     # self.mark_done("mobile")
        #     # self.countdown(1)
        #     # self.start_next("arm", "move_from_gap1_to_default_main")

        elif cmd == "button4_on" and self.task == 2:
            subprocess.run([os.path.expanduser("~/ccmedia/ccmedia_R10")], check=True)
            # self.mark_done("pressure")
            self.task += 1
            self.countdown(1)
            self.start_next("arm", "move_from_default_to_cushion1_start_main")
            self.countdown(1)
            self.start_next("arm", "reposition_start_sound")
            
        elif cmd == "change_vision_outside" and self.task == 3:
            print("change vision outside success")
            self.task += 1
            # self.mark_done("arm")
            # print("[Hand] release_comoral_finish")
            self.countdown(1)
            self.start_next("hand", "grasp_cushion1_start_main")

        elif cmd == "grasp_cushion1_finish_hand" and self.task == 4:
            self.mark_done("hand")
            self.task += 1
            self.countdown(1)
            self.start_next("arm", "move_from_cushion1_to_back_start_main")

        elif cmd == "move_from_cushion1_to_back_finish_arm" and self.task == 5:
            self.mark_done("arm")
            self.task += 1
            self.countdown(1)
            self.start_next("hand", "release_cushion1_start_main")

        elif cmd == "release_cushion1_finish_hand" and self.task == 6:
            self.mark_done("hand")
            self.task += 1
            self.countdown(1)
            self.start_next("arm", "move_from_back_to_cushion2_start_main")

        elif cmd == "move_from_back_to_cushion2_finish_arm" and self.task == 7:
            self.mark_done("arm")
            self.task += 1
            self.countdown(1)
            self.start_next("hand", "grasp_cushion2_start_main")

        elif cmd == "grasp_cushion2_finish_hand" and self.task == 8:
            self.mark_done("hand")
            self.task += 1
            self.countdown(1)
            self.start_next("arm", "move_from_cushion2_to_leg_start_main")

        elif cmd == "move_from_cushion2_to_leg_finish_arm" and self.task == 9:
            self.mark_done("arm")
            self.task += 1
            self.countdown(1)
            self.start_next("hand", "release_cushion2_start_main")

        elif cmd == "release_cushion2_finish_hand" and self.task == 10:
            subprocess.run([os.path.expanduser("~/ccmedia/ccmedia_R11")], check=True)
            self.mark_done("hand")
            self.task += 1
            self.countdown(1)
            self.start_next("arm", "move_from_back_to_default_start_main")
            self.countdown(1)
            self.start_next("arm", "reposition_finish_sound")

        elif cmd == "move_from_back_to_default_finish_arm" and self.task == 11:
            self.task += 1
            subprocess.run([os.path.expanduser("~/ccmedia/ccmedia_R12")], check=True)
            if cmd == "button1_off":
                self.countdown(1)
                self.start_next("mobile", "dock_off_start_main")
                self.countdown(1)
                self.start_next("arm", "dock_off_start_sound")

            

#################### Reposition finish #########################

################### Fall prevention start ######################

        # elif cmd == "fall_first_outside":
        #     # self.mark_done("arm")
        #     subprocess.run([os.path.expanduser("~/ccmedia/ccmedia_R14")], check=True)
        #     self.countdown(1)
        #     self.start_next("mobile", "move_to_gap1_start_main")
        #     self.countdown(1)
        #     self.start_next("arm", "move_to_gap1_sound")
        #     self.countdown(1)
        #     self.start_next("arm", "prevent_fall_posture_start_main")

        # elif cmd == "button1_off_for_fall":
        #     subprocess.run([os.path.expanduser("~/ccmedia/ccmedia_R15")], check=True)
        #     self.mark_done("arm")
        #     self.countdown(1)
        #     self.start_next("arm", "move_from_gap1_to_default_main")

        elif cmd == "ccmedia_R16":
            subprocess.run([os.path.expanduser("~/ccmedia/ccmedia_R16")], check=True)
            # self.mark_done("arm")
            # self.countdown(1)
            # self.start_next("arm", "move_from_gap1_to_default_main")

################################################################

        elif cmd == "button1_off":
            # self.mark_done("arm")
            self.countdown(1)
            self.start_next("mobile", "dock_off_start_main")
            self.countdown(1)
            self.start_next("arm", "dock_off_start_sound")

        elif cmd == "dock_off_finish_mobile":
            self.mark_done("mobile")
            self.countdown(1)
            self.start_next("arm", "dock_off_finish_sound")
            self.countdown(1)
            self.start_next("mobile", "move_to_charger_start_main")
            self.countdown(1)
            self.start_next("arm", "move_to_charger_start_sound")

        elif cmd == "move_to_charger_finish_mobile":
            self.mark_done("mobile")
            self.countdown(1)
            self.start_next("arm", "move_to_charger_finish_sound")


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
        status["mobile"] = "Working"
        start_times["mobile"] = time.time()
        self.update_gui()
        send_command("mobile", "move_to_bed_start_main")

    # -----------------------------------
    def countdown(self, seconds):
        for i in range(seconds, 0, -1):
            self.countdown_label.config(text=f"Next step countdown: {i} s")
            self.root.update()
            time.sleep(1)
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
