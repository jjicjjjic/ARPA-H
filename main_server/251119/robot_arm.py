import socket
import os
import subprocess
import time

UDP_IP = "127.0.0.1"
PORT = 50002
MAIN_PORT = 50000

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, PORT))

print("[Arm] Ready.")

while True:
    data, addr = sock.recvfrom(1024)
    msg = data.decode().strip()
    if msg.startswith("move_to_spoon_start_main"):
        print("[Arm] move_to_spoon_start")
        arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/m0_default_spoon") 
        subprocess.run([arm_path], check=True)
        time.sleep(0.01)
        print("[Arm] move_to_spoon_finish")
        sock.sendto(b"move_to_spoon_finish_arm", (UDP_IP, MAIN_PORT))

    # ---------------------------- repeat 1 --------------------------------------------------------------

    elif msg.startswith("move_to_food1_start_main"):
        print("[Arm] move_to_food1_start")
        arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/m1_spoon_food1")
        subprocess.run([arm_path], check=True)
        time.sleep(1.5)
        arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/m2")
        subprocess.run([arm_path], check=True)
        time.sleep(0.01)
        time.sleep(2)
        print("[Arm] move_to_food1_finish")
        sock.sendto(b"move_to_food1_finish_arm", (UDP_IP, MAIN_PORT))
    
    # ---------------------------- repeat 2 --------------------------------------------------------------

    elif msg.startswith("move_from_food1_to_fix_start_main"):
        print("[Arm] move_from_food1_to_fix_start")
        time.sleep(2)
        arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/m3_mouth_fix")
        subprocess.run([arm_path], check=True)
        time.sleep(6)
        print("success34")
        print("[Arm] move_from_food1_to_fix_finish")
        sock.sendto(b"move_from_food1_to_fix_finish_arm", (UDP_IP, MAIN_PORT))

    elif msg.startswith("move_to_food2_start_main"):
        print("[Arm] move_to_food2_start")
        time.sleep(3)
        arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/m4_fix_food2")
        subprocess.run([arm_path], check=True)
        time.sleep(0.01)
        print("[Arm] move_to_food2_finish")
        sock.sendto(b"move_to_food2_finish_arm", (UDP_IP, MAIN_PORT))

    elif msg.startswith("move_from_food2_to_mouth_start_main"):
        print("[Arm] move_from_food2_to_mouth_start")
        # food2 -> mouth
        time.sleep(2)
        arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/m5_mouthfix")
        subprocess.run([arm_path], check=True)
        time.sleep(1)
        print("[Arm] move_from_food2_to_mouth_finish")
        sock.sendto(b"move_from_food2_to_mouth_finish_arm", (UDP_IP, MAIN_PORT))

    # ---------------------------- repeat 3 --------------------------------------------------------------

    elif msg.startswith("move_from_mouth2_to_fix_start_main"):
        print("[Arm] move_from_mouth2_to_fix_start")
        time.sleep(2)
        arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/m6_mouth_fix")
        subprocess.run([arm_path], check=True)
        time.sleep(5)
        print("[Arm] move_from_mouth2_to_fix_finish")
        sock.sendto(b"move_from_mouth2_to_fix_finish_arm", (UDP_IP, MAIN_PORT))

    elif msg.startswith("move_to_food3_start_main"):
        print("[Arm] move_to_food3_start")
        time.sleep(3)
        arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/m7_fix_food3")
        subprocess.run([arm_path], check=True)
        time.sleep(1)
        print("[Arm] move_to_food3_finish")
        sock.sendto(b"move_to_food3_finish_arm", (UDP_IP, MAIN_PORT))

    elif msg.startswith("move_from_food3_to_mouth_start_main"):
        print("[Arm] move_from_food3_to_mouth_start")
        arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/m8_mouthfix")
        subprocess.run([arm_path], check=True)
        time.sleep(3)
        print("[Arm] move_from_food3_to_mouth_finish")
        sock.sendto(b"move_from_food3_to_mouth_finish_arm", (UDP_IP, MAIN_PORT))

    # ---------------------------- repeat 4 --------------------------------------------------------------

    elif msg.startswith("move_from_mouth3_to_fix_start_main"):
        print("[Arm] move_from_mouth3_to_fix_start")
        time.sleep(2)
        arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/m9_mouth_fix")
        subprocess.run([arm_path], check=True)
        time.sleep(5)
        print("[Arm] move_from_mouth3_to_fix_finish")
        sock.sendto(b"move_from_mouth3_to_fix_finish_arm", (UDP_IP, MAIN_PORT))

    elif msg.startswith("move_to_food4_start_main"):
        print("[Arm] move_to_food4_start")
        arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/m10_fix_food1")
        subprocess.run([arm_path], check=True)
        time.sleep(0.01)
        print("[Arm] move_to_food4_finish")
        sock.sendto(b"move_to_food4_finish_arm", (UDP_IP, MAIN_PORT))

    elif msg.startswith("move_from_food4_to_mouth_start_main"):
        print("[Arm] move_from_food4_to_mouth_start")
        time.sleep(2)
        arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/m2")
        subprocess.run([arm_path], check=True)
        time.sleep(0.01)
        print("[Arm] move_from_food4_to_mouth_finish")
        sock.sendto(b"move_from_food4_to_mouth_finish_arm", (UDP_IP, MAIN_PORT))

    # ---------------------------- repeat 5 --------------------------------------------------------------

    elif msg.startswith("move_from_mouth4_to_fix_start_main"):
        print("[Arm] move_from_mouth4_to_fix_start")
        time.sleep(2)
        arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/m3_mouth_fix")
        subprocess.run([arm_path], check=True)
        time.sleep(5)
        print("[Arm] move_from_mouth4_to_fix_finish")
        sock.sendto(b"move_from_mouth4_to_fix_finish_arm", (UDP_IP, MAIN_PORT))

    elif msg.startswith("move_to_food5_start_main"):
        print("[Arm] move_to_food5_start")
        arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/m4_fix_food2")
        subprocess.run([arm_path], check=True)
        time.sleep(0.01)
        print("[Arm] move_to_food5_finish")
        sock.sendto(b"move_to_food5_finish_arm", (UDP_IP, MAIN_PORT))

    elif msg.startswith("move_from_food5_to_mouth_start_main"):
        print("[Arm] move_from_food5_to_mouth_start")
        arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/m5_mouthfix")
        subprocess.run([arm_path], check=True)
        time.sleep(0.01)
        time.sleep(2)
        print("[Arm] move_from_food5_to_mouth_finish")
        sock.sendto(b"move_from_food5_to_mouth_finish_arm", (UDP_IP, MAIN_PORT))

    # ---------------------------- repeat 6 --------------------------------------------------------------

    elif msg.startswith("move_from_mouth5_to_fix_start_main"):
        print("[Arm] move_from_mouth5_to_fix_start")
        time.sleep(2)
        arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/m6_mouth_fix")
        subprocess.run([arm_path], check=True)
        time.sleep(5)
        print("[Arm] move_from_mouth5_to_fix_finish")
        sock.sendto(b"move_from_mouth5_to_fix_finish_arm", (UDP_IP, MAIN_PORT))

    elif msg.startswith("move_to_food6_start_main"):
        print("[Arm] move_to_food6_start")
        arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/m7_fix_food3")
        subprocess.run([arm_path], check=True)
        time.sleep(0.01)
        print("[Arm] move_to_food6_finish")
        sock.sendto(b"move_to_food6_finish_arm", (UDP_IP, MAIN_PORT))

    elif msg.startswith("move_from_food6_to_mouth_start_main"):
        print("[Arm] move_from_food6_to_mouth_start")
        arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/m8_mouthfix")
        subprocess.run([arm_path], check=True)
        time.sleep(0.01)
        time.sleep(2)
        print("[Arm] move_from_food6_to_mouth_finish")
        sock.sendto(b"move_from_food6_to_mouth_finish_arm", (UDP_IP, MAIN_PORT))

    # ---------------------------- repeat finish --------------------------------------------------------------

    elif msg.startswith("move_from_mouth6_to_fix_start_main"):
        print("[Arm] move_from_mouth6_to_fix_start")
        time.sleep(2)
        arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/m9_mouth_fix")
        subprocess.run([arm_path], check=True)
        time.sleep(5)
        print("[Arm] move_from_mouth6_to_fix_start")
        sock.sendto(b"move_from_mouth6_to_fix_start_arm", (UDP_IP, MAIN_PORT))

    elif msg.startswith("move_from_food_to_default_arm_start_main"):
        print("[Arm] move_from_food_to_default_arm_start")
        arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/m11_fix_spoon")
        subprocess.run([arm_path], check=True)
        time.sleep(0.01)
        time.sleep(2)
        print("[Arm] move_from_food_to_default_arm_finish")
        sock.sendto(b"move_from_food_to_default_arm_finish_arm", (UDP_IP, MAIN_PORT))

##################### Meal finish ############################

##################### Brush start ############################

    elif msg.startswith("move_from_default_to_comoral_start_main"):
        print("[Arm] move_from_default_to_comoral_start")
        arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/c1_default_comoral")
        subprocess.run([arm_path], check=True)
        time.sleep(0.01)
        print("[Arm] move_from_default_to_comoral_finish")
        sock.sendto(b"move_from_default_to_comoral_finish_arm", (UDP_IP, MAIN_PORT))

    elif msg.startswith("move_cormal_to_mouth_start_main"):
        print("[Arm] move_cormal_to_mouth_start")
        arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/c3")
        subprocess.run([arm_path], check=True)
        time.sleep(0.01)
        print("[Arm] move_cormal_to_mouth_finish")
        sock.sendto(b"move_cormal_to_mouth_finish_arm", (UDP_IP, MAIN_PORT))

    elif msg.startswith("move_from_mouth_to_comoral_start_main"):
        print("[Arm] move_from_mouth_to_comoral_start")
        arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/c4_mouth_fix")
        subprocess.run([arm_path], check=True)
        time.sleep(0.01)
        arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/c5_fix_comoral")
        subprocess.run([arm_path], check=True)
        time.sleep(0.01)
        print("[Arm] move_from_mouth_to_comoral_finish")
        sock.sendto(b"move_from_mouth_to_comoral_finish_arm", (UDP_IP, MAIN_PORT))

    elif msg.startswith("move_from_comoral_to_default_start_main"):
        print("[Arm] move_from_comoral_to_default_start")
        arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/c6_comoral_default")
        subprocess.run([arm_path], check=True)
        time.sleep(0.01)
        arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/default_move")
        subprocess.run([arm_path], check=True)
        time.sleep(0.01)
        print("[Arm] move_from_comoral_to_default_finish")
        sock.sendto(b"move_from_comoral_to_default_finish_arm", (UDP_IP, MAIN_PORT))

####################### Brush finish #########################

####################### Reposition start #####################

    elif msg.startswith("move_from_default_to_cushion1_start_main"):
        print("[Arm] move_from_default_to_cushion1_start")
        arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/p1_default_cushion")
        subprocess.run([arm_path], check=True)
        time.sleep(0.01)
        print("[Arm] move_from_default_to_cushion1_finish")
        sock.sendto(b"move_from_default_to_cushion_finish_arm", (UDP_IP, MAIN_PORT))

    elif msg.startswith("move_from_cushion1_to_back_start_main"):
        print("[Arm] move_from_cushion1_to_back_start")
        arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/p2_cushion_back")
        subprocess.run([arm_path], check=True)
        time.sleep(0.01)
        print("[Arm] move_from_cushion1_to_back_finish")
        sock.sendto(b"move_from_cushion1_to_back_finish_arm", (UDP_IP, MAIN_PORT))

    elif msg.startswith("move_from_back_to_cushion2_start_main"):
        print("[Arm] move_from_back_to_cushion2_start")
        arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/p3_back_cushion2")
        subprocess.run([arm_path], check=True)
        time.sleep(0.01)
        print("[Arm] move_from_back_to_cushion2_finish")
        sock.sendto(b"move_from_back_to_cushion2_finish_arm", (UDP_IP, MAIN_PORT))

    elif msg.startswith("move_from_cushion2_to_leg_start_main"):
        print("[Arm] move_from_cushion2_to_leg_start")
        arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/p4_cushion2_back")
        subprocess.run([arm_path], check=True)
        time.sleep(0.01)
        print("[Arm] move_from_cushion2_to_leg_finish")
        sock.sendto(b"move_from_cushion2_to_leg_finish_arm", (UDP_IP, MAIN_PORT))

    elif msg.startswith("move_from_leg_to_fix_start_main"):
        print("[Arm] move_from_leg_to_fix_start")
        arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/p5_back_fix")
        subprocess.run([arm_path], check=True)
        time.sleep(0.01)
        print("[Arm] move_from_leg_to_fix_finish")

    elif msg.startswith("move_from_back_to_default_start_main"):
        print("[Arm] move_from_back_to_default_start")
        arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/p6_back_default")
        subprocess.run([arm_path], check=True)
        arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/default_move")
        subprocess.run([arm_path], check=True)
        time.sleep(0.01)
        print("[Arm] move_from_back_to_default_finish")

################### Reposition finish ########################

################### Fall prevention start ####################

    elif msg.startswith("prevent_fall1_posture_start_main"):
        print("[Arm] prevent_fall1_posture_start")
        arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/f1_pose1")
        subprocess.run([arm_path], check=True)
        time.sleep(1.5)
        print("[Arm] prevent_fall1_posture_finish")
        sock.sendto(b"prevent_fall1_posture_finish_arm", (UDP_IP, MAIN_PORT))

    elif msg.startswith("prevent_fall2_posture_start_main"):
        print("[Arm] prevent_fall2_posture_start")
        arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/f3_pose2")
        subprocess.run([arm_path], check=True)
        time.sleep(1.5)
        print("[Arm] prevent_fall2_posture_finish")
        sock.sendto(b"prevent_fall2_posture_finish_arm", (UDP_IP, MAIN_PORT))

    elif msg.startswith("prevent_fall3_posture_start_main"):
        print("[Arm] prevent_fall3_posture_start")
        arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/f5_pose3")
        subprocess.run([arm_path], check=True)
        time.sleep(1.5)
        print("[Arm] prevent_fall3_posture_finish")
        sock.sendto(b"prevent_fall3_posture_finish_arm", (UDP_IP, MAIN_PORT))

    elif msg.startswith("move_from_gap1_to_default_main"):
        print("[Arm] move_from_gap1_to_default_start")
        arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/f2_pose1_default")
        subprocess.run([arm_path], check=True)
        time.sleep(1.5)
        arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/default_move")
        subprocess.run([arm_path], check=True)
        time.sleep(1.5)
        print("[Arm] move_from_gap1_to_default_finish")
        sock.sendto(b"move_from_gap1_to_default_finish_arm", (UDP_IP, MAIN_PORT))   

    elif msg.startswith("move_from_gap2_to_default_main"):
        print("[Arm] move_from_gap2_to_default_start")
        arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/f4_pose2_default")
        subprocess.run([arm_path], check=True)
        time.sleep(1.5)
        arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/default_move")
        subprocess.run([arm_path], check=True)
        time.sleep(1.5)
        print("[Arm] move_from_gap2_to_default_finish")
        sock.sendto(b"move_from_gap2_to_default_finish_arm", (UDP_IP, MAIN_PORT))   

    elif msg.startswith("move_from_gap3_to_default_main"):
        print("[Arm] move_from_gap3_to_default_start")
        arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/f6_pose3_default")
        subprocess.run([arm_path], check=True)
        time.sleep(1.5)
        arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/default_move")
        subprocess.run([arm_path], check=True)
        time.sleep(1.5)
        print("[Arm] move_from_gap3_to_default_finish")
        sock.sendto(b"move_from_gap3_to_default_finish_arm", (UDP_IP, MAIN_PORT))   

# sound
    elif msg.startswith("move_to_bed_start_sound"):
        print("[Arm] move_to_bed_start_sound")
        arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/Move_bed") 
        subprocess.run([arm_path], check=True)
        time.sleep(0.01)
        print("[Arm] move_to_bed_start_sound DONE")

    elif msg.startswith("move_to_bed_finish_sound"):
        print("[Arm] move_to_bed_finish_sound")
        arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/Move_done") 
        subprocess.run([arm_path], check=True)
        time.sleep(0.01)
        print("[Arm] move_to_bed_finish_sound DONE")

    elif msg.startswith("dock_on_start_sound"):
        print("[Arm] dock_on_start_sound")
        arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/Docking_ongoing") 
        subprocess.run([arm_path], check=True)
        time.sleep(0.01)
        print("[Arm] dock_on_start_sound DONE")

    elif msg.startswith("dock_on_finish_sound"):
        print("[Arm] dock_on_finish_sound")
        arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/Docking_done") 
        subprocess.run([arm_path], check=True)
        time.sleep(0.01)
        print("[Arm] dock_on_finish_sound DONE")

    elif msg.startswith("meal_start_sound"):
        print("[Arm] meal_start_sound")
        arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/Meal_start") 
        subprocess.run([arm_path], check=True)
        time.sleep(0.01)
        print("[Arm] meal_start_sound DONE")

    elif msg.startswith("chewing_sound"):
        print("[Arm] chewing_sound")
        time.sleep(3)
        arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/Meal_pleaseeat") 
        subprocess.run([arm_path], check=True)
        time.sleep(0.01)
        print("[Arm] chewing_sound DONE")
        sock.sendto(b"chewing_sound_finish_arm", (UDP_IP, MAIN_PORT))  
        
    elif msg.startswith("chewing_problem_sound"):
        print("[Arm] chewing_problem_sound")
        arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/Meal_pleasechew") 
        subprocess.run([arm_path], check=True)
        time.sleep(0.01)
        print("[Arm] chewing_problem_sound DONE")

    elif msg.startswith("meal_finish_sound"):
        print("[Arm] meal_finish_sound")
        arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/Meal_done") 
        subprocess.run([arm_path], check=True)
        time.sleep(0.01)
        print("[Arm] meal_finish_sound DONE")
    
############### Meal finish #######################

############### Brush start #######################

    elif msg.startswith("brush_start_sound"):
        print("[Arm] brush_start_sound")
        arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/Brushing_start") 
        subprocess.run([arm_path], check=True)
        time.sleep(0.01)
        print("[Arm] brush_start_sound DONE")

    elif msg.startswith("bite_cormal_sound"):
        print("[Arm] bite_cormal_sound")
        arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/Brushing_bitewaterlet") 
        subprocess.run([arm_path], check=True)
        time.sleep(0.01)
        print("[Arm] bite_cormal_sound DONE")

    elif msg.startswith("brush_finish_sound"):
        print("[Arm] brush_finish_sound")
        arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/Brushing_done") 
        subprocess.run([arm_path], check=True)
        time.sleep(0.01)
        print("[Arm] brush_finish_sound DONE")

############### Brush start #######################

############### Reposition start ##################

    elif msg.startswith("reposition_start_sound"):
        print("[Arm] reposition_start_sound")
        arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/Position_start") 
        subprocess.run([arm_path], check=True)
        time.sleep(0.01)
        print("[Arm] reposition_start_sound DONE")

    elif msg.startswith("reposition_finish_sound"):
        print("[Arm] reposition_finish_sound")
        arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/Position_end") 
        subprocess.run([arm_path], check=True)
        time.sleep(0.01)
        print("[Arm] reposition_finish_sound DONE")

################## Reposition finish ##########################

################## Fall prevention start ######################

    elif msg.startswith("move_to_gap1_sound"):
        print("[Arm] move_to_gap1_sound")
        arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/Fall_danger") 
        subprocess.run([arm_path], check=True)
        time.sleep(0.01)
        print("[Arm] move_to_gap1_sound DONE")

    #########################

    elif msg.startswith("dock_off_start_sound"):
        print("[Arm] dock_off_start_sound")
        arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/Docking_unlockongoing") 
        subprocess.run([arm_path], check=True)
        time.sleep(0.01)
        print("[Arm] dock_off_start_sound DONE")

    elif msg.startswith("dock_off_finish_sound"):
        print("[Arm] dock_off_finish_sound")
        arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/Docking_unlockondone") 
        subprocess.run([arm_path], check=True)
        time.sleep(0.01)
        print("[Arm] dock_off_finish_sound DONE")

    elif msg.startswith("move_to_charger_start_sound"):
        print("[Arm] move_to_charger_start_sound")
        arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/Move_charger") 
        subprocess.run([arm_path], check=True)
        time.sleep(0.01)
        print("[Arm] move_to_charger_start_sound DONE")

    elif msg.startswith("move_to_charger_finish_sound"):
        print("[Arm] move_to_charger_finish_sound")
        arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/Move_done") 
        subprocess.run([arm_path], check=True)
        time.sleep(0.01)
        print("[Arm] move_to_charger_finish_sound DONE")
