import socket
import threading
import time
import tkinter as tk
from tkinter import ttk

UDP_IP = "127.0.0.1"
MAIN_PORT = 50000
MODULES = {"mobile": 50001, "arm": 50002, "camera": 50003, "hand": 50004}

status = {name: "Idle" for name in MODULES}
start_times = {name: None for name in MODULES}
durations = {name: None for name in MODULES}

recv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
recv_sock.bind((UDP_IP, MAIN_PORT))
recv_sock.settimeout(0.1)

def send_command(target, message):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(message.encode(), (UDP_IP, MODULES[target]))
    sock.close()
    print(f"[Send] {target}: {message}")

class RobotGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Robot System Monitor (No Keyboard Module)")
        self.root.geometry("580x400")
        self.root.configure(bg="white")

        ttk.Label(self.root, text="Robot System Monitor", font=("Arial", 15, "bold")).pack(pady=10)

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

        ttk.Label(self.root, text="Press '1' key in this window to start sequence", font=("Arial", 11)).pack(pady=5)

        # 키보드 입력 바인딩
        self.root.bind("1", lambda event: self.start_sequence())

        threading.Thread(target=self.listen_feedback, daemon=True).start()

    def update_gui(self):
        color_map = {"Idle": "#D3D3D3", "Working": "#FFD700", "Done": "#90EE90"}
        for name in MODULES.keys():
            st = status[name]
            dur = durations[name] if durations[name] is not None else "—"
            self.tree.item(name, values=[st, dur])
            self.tree.tag_configure(name, background=color_map.get(st, "white"))
            self.tree.item(name, tags=(name,))

    def start_sequence(self):
        print("[Key] 1 pressed — start sequence")
        for k in status:
            status[k] = "Idle"
            durations[k] = None
        self.update_gui()
        status["mobile"] = "Working"
        start_times["mobile"] = time.time()
        self.update_gui()
        send_command("mobile", "MOVE_FOOD")

    def countdown(self, seconds):
        for i in range(seconds, 0, -1):
            self.countdown_label.config(text=f"Next step countdown: {i} s")
            self.root.update()
            time.sleep(1)
        self.countdown_label.config(text="Next step countdown: —")

    def listen_feedback(self):
        while True:
            try:
                data, _ = recv_sock.recvfrom(1024)
                msg = data.decode().strip()
                print(f"[Recv] {msg}")

                if msg == "MOBILE_FOOD_DONE":
                    self.mark_done("mobile")
                    self.countdown(1)
                    self.start_next("arm", "MOVE_ARM_FOOD1")
                elif msg == "ARM_DONE_FOOD1":
                    self.mark_done("arm")
                    self.countdown(1)
                    self.start_next("camera", "CAPTURE_FOOD")
                elif msg == "CAMERA_DONE_FOOD":
                    self.mark_done("camera")
                    self.countdown(1)
                    self.start_next("hand", "GRASP_FOOD1")
                elif msg == "HAND_DONE_FOOD1":
                    self.mark_done("hand")
                    self.countdown(1)
                    self.start_next("arm", "MOVE_ARM_FOOD2")
                elif msg == "ARM_DONE_FOOD2":
                    self.mark_done("arm")
                    self.countdown(1)
                    self.start_next("hand", "GRASP_FOOD2")

            except socket.timeout:
                pass

    def mark_done(self, module):
        status[module] = "Done"
        durations[module] = f"{time.time() - start_times[module]:.2f}"
        self.update_gui()

    def start_next(self, module, command):
        status[module] = "Working"
        start_times[module] = time.time()
        self.update_gui()
        send_command(module, command)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    gui = RobotGUI()
    gui.run()
