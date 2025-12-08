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

    if msg.startswith("m1_sound"): # move_to_bed_start_sound
        print("[Arm] m1_sound")
        arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/Move_bed") 
        subprocess.run([arm_path], check=True)
        time.sleep(1)
        print("[Arm] m1_sound DONE")

    elif msg.startswith("m2_sound1"): # move_to_bed_finish_sound
        print("[Arm] m2_sound1")
        arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/Move_done") 
        subprocess.run([arm_path], check=True)
        time.sleep(1)
        print("[Arm] m2_sound1 DONE")

    elif msg.startswith("m2_sound2"): # dock_on_start_sound
        print("[Arm] m2_sound2")
        arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/Docking_ongoing") 
        subprocess.run([arm_path], check=True)
        time.sleep(1)
        print("[Arm] m2_sound2 DONE")

    elif msg.startswith("m3_sound"): # dock_on_finish_sound
        print("[Arm] m3_sound")
        arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/Docking_done") 
        subprocess.run([arm_path], check=True)
        time.sleep(1)
        print("[Arm] m3_sound DONE")

    elif msg.startswith("m4_sound"): # meal_start_sound
        print("[Arm] m4_sound")
        arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/Meal_start") 
        subprocess.run([arm_path], check=True)
        time.sleep(1)
        print("[Arm] m4_sound DONE")
    
    elif msg.startswith("m4_arm"): # move_to_spoon_start_main
        print("[Arm] m4_arm")
        arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/m0_default_spoon") 
        subprocess.run([arm_path], check=True)
        time.sleep(1)
        sock.sendto(b"m5", (UDP_IP, MAIN_PORT))

    # ---------------------------- repeat 1 --------------------------------------------------------------

    elif msg.startswith("m6_arm"): # move_to_food1_start_main
        print("[Arm] m6_arm")
        arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/m1_spoon_food1")
        subprocess.run([arm_path], check=True)
        time.sleep(3)
        arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/m5_mouthfix")
        subprocess.run([arm_path], check=True)
        time.sleep(3)
        sock.sendto(b"m7", (UDP_IP, MAIN_PORT))

    elif msg.startswith("m7_sound"): # chewing_sound
        print("[Arm] m7_sound")
        arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/Meal_pleaseeat") 
        subprocess.run([arm_path], check=True)
        time.sleep(1)
        sock.sendto(b"m8", (UDP_IP, MAIN_PORT)) 
    
    # ---------------------------- repeat 2 --------------------------------------------------------------

    elif msg.startswith("m8_arm"): # move_from_food1_to_fix_start_main
        print("[Arm] m8_arm")
        time.sleep(5)
        arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/m6_mouth_fix")
        subprocess.run([arm_path], check=True)
        time.sleep(6)
        sock.sendto(b"m9", (UDP_IP, MAIN_PORT))

    elif msg.startswith("m9_arm"): # move_to_food2_start_main
        print("[Arm] m9_arm")
        time.sleep(1)
        arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/m4_fix_food2")
        subprocess.run([arm_path], check=True)
        time.sleep(3)
        sock.sendto(b"m10", (UDP_IP, MAIN_PORT))

    elif msg.startswith("m10_arm"): # move_from_food2_to_mouth_start_main
        print("[Arm] m10_arm")
        arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/m5_mouthfix")
        subprocess.run([arm_path], check=True)
        time.sleep(3)
        sock.sendto(b"m11", (UDP_IP, MAIN_PORT))

    elif msg.startswith("m11_sound"): # chewing_sound
        print("[Arm] m11_sound")
        arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/Meal_pleaseeat") 
        subprocess.run([arm_path], check=True)
        time.sleep(1)
        sock.sendto(b"m12", (UDP_IP, MAIN_PORT)) 

    # ---------------------------- repeat 3 --------------------------------------------------------------

    elif msg.startswith("m12_arm"): # move_from_mouth2_to_fix_start_main
        print("[Arm] m12_arm")
        time.sleep(5)
        arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/m6_mouth_fix")
        subprocess.run([arm_path], check=True)
        time.sleep(5)
        sock.sendto(b"m13", (UDP_IP, MAIN_PORT))

    elif msg.startswith("m13_arm"): # move_to_food3_start_main
        print("[Arm] m13_arm")
        time.sleep(1)
        arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/m7_fix_food3")
        subprocess.run([arm_path], check=True)
        time.sleep(3)
        sock.sendto(b"m14", (UDP_IP, MAIN_PORT))

    elif msg.startswith("m14_arm"): # move_from_food3_to_mouth_start_main
        print("[Arm] m14_arm")
        arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/m8_mouthfix")
        subprocess.run([arm_path], check=True)
        time.sleep(6)
        sock.sendto(b"m15", (UDP_IP, MAIN_PORT))

    elif msg.startswith("m15_sound"): # chewing_sound
        print("[Arm] m15_sound")
        time.sleep(3)
        arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/Meal_pleaseeat") 
        subprocess.run([arm_path], check=True)
        time.sleep(1)
        sock.sendto(b"m16", (UDP_IP, MAIN_PORT)) 

    # ---------------------------- repeat 4 --------------------------------------------------------------

    elif msg.startswith("m16_arm"): # move_from_mouth3_to_fix_start_main
        print("[Arm] m16_arm")
        arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/m9_mouth_fix")
        subprocess.run([arm_path], check=True)
        time.sleep(5)
        # sock.sendto(b"m17", (UDP_IP, MAIN_PORT))

    elif msg.startswith("m17_arm"): # move_to_food4_start_main
        print("[Arm] move_m17_arm")
        arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/m10_fix_food1")
        subprocess.run([arm_path], check=True)
        time.sleep(6)
        sock.sendto(b"m18", (UDP_IP, MAIN_PORT))

    elif msg.startswith("m18_arm"): # move_from_food4_to_mouth_start_main
        print("[Arm] m18_arm")
        arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/m2")
        subprocess.run([arm_path], check=True)
        time.sleep(6)
        sock.sendto(b"m19", (UDP_IP, MAIN_PORT))

    elif msg.startswith("m19_sound"): # chewing_sound
        print("[Arm] m19_sound")
        time.sleep(5)
        arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/Meal_pleaseeat") 
        subprocess.run([arm_path], check=True)
        time.sleep(1)
        sock.sendto(b"m20", (UDP_IP, MAIN_PORT)) 

    # ---------------------------- repeat 5 --------------------------------------------------------------

    elif msg.startswith("m20_arm"): # move_from_mouth4_to_fix_start_main
        print("[Arm] m20_arm")
        arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/m3_mouth_fix")
        subprocess.run([arm_path], check=True)
        time.sleep(5)
        sock.sendto(b"m21", (UDP_IP, MAIN_PORT))

    elif msg.startswith("m21_arm"): # move_to_food5_start_main
        print("[Arm] m21_arm")
        arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/m4_fix_food2")
        subprocess.run([arm_path], check=True)
        time.sleep(3)
        sock.sendto(b"m22", (UDP_IP, MAIN_PORT))

    elif msg.startswith("m22_arm"): # move_from_food5_to_mouth_start_main
        print("[Arm] m22_arm")
        arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/m5_mouthfix")
        subprocess.run([arm_path], check=True)
        time.sleep(3)
        sock.sendto(b"m23", (UDP_IP, MAIN_PORT))

    elif msg.startswith("m23_sound"): # chewing_sound
        print("[Arm] m23_sound")
        arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/Meal_pleaseeat") 
        subprocess.run([arm_path], check=True)
        time.sleep(1)
        sock.sendto(b"m24", (UDP_IP, MAIN_PORT))

    # ---------------------------- repeat 6 --------------------------------------------------------------

    elif msg.startswith("m24_arm"): # move_from_mouth5_to_fix_start_main
        print("[Arm] m24_arm")
        arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/m6_mouth_fix")
        subprocess.run([arm_path], check=True)
        time.sleep(5)
        sock.sendto(b"m25", (UDP_IP, MAIN_PORT))

    elif msg.startswith("m25_arm"): # move_to_food6_start_main
        print("[Arm] m25_arm")
        arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/m7_fix_food3")
        subprocess.run([arm_path], check=True)
        time.sleep(3)
        sock.sendto(b"m26", (UDP_IP, MAIN_PORT))

    elif msg.startswith("m26_arm"): # move_from_food6_to_mouth_start_main
        print("[Arm] m26_arm")
        arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/m8_mouthfix")
        subprocess.run([arm_path], check=True)
        time.sleep(2)
        sock.sendto(b"m27", (UDP_IP, MAIN_PORT))
    
    elif msg.startswith("m27_sound"): # chewing_sound
        print("[Arm] m27_sound")
        time.sleep(5)
        arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/Meal_pleaseeat") 
        subprocess.run([arm_path], check=True)
        time.sleep(1)
        sock.sendto(b"m28", (UDP_IP, MAIN_PORT))

    # ---------------------------- repeat finish --------------------------------------------------------------

    elif msg.startswith("m28_arm"): # move_from_mouth6_to_fix_start_main
        print("[Arm] m28_arm")
        arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/m9_mouth_fix")
        subprocess.run([arm_path], check=True)
        time.sleep(5)

    elif msg.startswith("m29_arm"): # move_from_food_to_default_arm_start_main
        print("[Arm] m29_arm")
        arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/m11_fix_spoon")
        subprocess.run([arm_path], check=True)
        time.sleep(2)
        sock.sendto(b"m30", (UDP_IP, MAIN_PORT))

    elif msg.startswith("m29_sound"): # meal_finish_sound
        print("[Arm] m29_sound")
        arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/Meal_done") 
        subprocess.run([arm_path], check=True)
        time.sleep(1)

    elif msg.startswith("m31_arm"): # move_from_mouth6_to_fix_start_main
        arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/m12_spoon_default")
        subprocess.run([arm_path], check=True)
        time.sleep(2)

##################### Meal finish ############################

##################### Brush start ############################

    elif msg.startswith("c1_sound"): # brush_start_sound
        print("[Arm] c1_sound")
        arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/Brushing_start") 
        subprocess.run([arm_path], check=True)
        time.sleep(1)
        print("[Arm] c1_sound DONE")

    elif msg.startswith("c1_arm"): # move_from_default_to_comoral_start_main
        print("[Arm] c1_arm")
        arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/c1_default_comoral")
        subprocess.run([arm_path], check=True)
        time.sleep(5)
        sock.sendto(b"c2", (UDP_IP, MAIN_PORT))

    elif msg.startswith("c3_arm"): # move_cormal_to_mouth_start_main
        print("[Arm] c3_arm")
        arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/c2_comoral_mouth")
        subprocess.run([arm_path], check=True)
        # time.sleep(3)
        sock.sendto(b"c4", (UDP_IP, MAIN_PORT))

    elif msg.startswith("c4_sound"): # bite_cormal_sound
        print("[Arm] c4_sound")
        # time.sleep(2)
        arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/Brushing_bitewaterlet") 
        subprocess.run([arm_path], check=True)
        time.sleep(1)

    elif msg.startswith("c5_sound"): # brush_finish_sound
        print("[Arm] c5_sound")
        arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/Brushing_done") 
        subprocess.run([arm_path], check=True)
        time.sleep(1)

    elif msg.startswith("c5_arm"): # move_from_mouth_to_comoral_start_main
        print("[Arm] c5_arm")
        arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/c4_mouth_fix")
        subprocess.run([arm_path], check=True)
        time.sleep(7)
        arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/c5_fix_comoral")
        subprocess.run([arm_path], check=True)
        time.sleep(2)
        sock.sendto(b"c6", (UDP_IP, MAIN_PORT))

    elif msg.startswith("c7_arm"): # move_from_comoral_to_default_start_main
        print("[Arm] c7_arm")
        arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/c6_comoral_default")
        subprocess.run([arm_path], check=True)
        time.sleep(5)
        # arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/default_move")
        # subprocess.run([arm_path], check=True)
        # time.sleep(1)

####################### Brush finish #########################

####################### Reposition start #####################

    elif msg.startswith("r1_sound"): # reposition_start_sound
        print("[Arm] r1_sound")
        arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/Position_start") 
        subprocess.run([arm_path], check=True)
        time.sleep(1)

    elif msg.startswith("r1_arm"): # move_from_default_to_cushion1_start_main
        print("[Arm] r1_arm")
        arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/p1_default_cushion")
        subprocess.run([arm_path], check=True)
        time.sleep(3)

    elif msg.startswith("r3_arm"): # move_from_cushion1_to_back_start_main
        print("[Arm] r3_arm")
        time.sleep(2)
        arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/p2_cushion_back")
        subprocess.run([arm_path], check=True)
        time.sleep(1)
        sock.sendto(b"r4", (UDP_IP, MAIN_PORT))

    elif msg.startswith("r5_arm"): # move_from_back_to_cushion2_start_main
        print("[Arm] r5_arm")
        arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/p3_back_cushion2")
        subprocess.run([arm_path], check=True)
        time.sleep(1)
        sock.sendto(b"r6", (UDP_IP, MAIN_PORT))

    elif msg.startswith("r7_arm"): # move_from_cushion2_to_leg_start_main
        print("[Arm] r7_arm")
        arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/p4_cushion2_back")
        subprocess.run([arm_path], check=True)
        time.sleep(1)
        sock.sendto(b"r8", (UDP_IP, MAIN_PORT))

    elif msg.startswith("r9_arm"): # move_from_leg_to_fix_start_main
        print("[Arm] r9_arm")
        arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/p5_back_fix")
        subprocess.run([arm_path], check=True)
        time.sleep(1)

    elif msg.startswith("r10_sound"): # reposition_finish_sound
        print("[Arm] r10_sound")
        arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/Position_end") 
        subprocess.run([arm_path], check=True)
        time.sleep(1)

    elif msg.startswith("r10_arm"): # move_from_back_to_default_start_main
        print("[Arm] r10_arm")
        arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/p6_back_default")
        subprocess.run([arm_path], check=True)
        time.sleep(3)
        arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/default_move")
        subprocess.run([arm_path], check=True)
        time.sleep(1)

    elif msg.startswith("r11_sound"): # dock_off_start_sound
        print("[Arm] r11_sound")
        arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/Docking_unlockongoing") 
        subprocess.run([arm_path], check=True)
        time.sleep(1)

    elif msg.startswith("r12_sound1"): # dock_off_finish_sound
        print("[Arm] r12_sound1")
        arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/Docking_unlockdone") 
        subprocess.run([arm_path], check=True)
        time.sleep(1)

    elif msg.startswith("r12_sound2"): # move_to_charger_start_sound
        print("[Arm] r12_sound2")
        arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/Move_charger") 
        subprocess.run([arm_path], check=True)
        time.sleep(1)

    elif msg.startswith("r13_sound"): # move_to_charger_finish_sound
        print("[Arm] r13_sound")
        arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/Move_done") 
        subprocess.run([arm_path], check=True)
        time.sleep(1)

################### Reposition finish ########################

################### Fall prevention start ####################

    elif msg.startswith("f1_sound"): # move_to_bed_start_sound
        print("[Arm] f1_sound")
        arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/Move_bed") 
        subprocess.run([arm_path], check=True)
        time.sleep(1)
        print("[Arm] f1_sound DONE")

    elif msg.startswith("f2_arm"): # prevent_fall1_posture_start_main
        print("[Arm] f2_arm")
        arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/f1_pose1")
        subprocess.run([arm_path], check=True)
        time.sleep(1.5)
        sock.sendto(b"f3", (UDP_IP, MAIN_PORT))

    elif msg.startswith("f3_sound"): # move_to_gap1_sound
        print("[Arm] f3_sound")
        arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/Fall_danger") 
        subprocess.run([arm_path], check=True)
        time.sleep(1)
        print("[Arm] f3_sound DONE")

    elif msg.startswith("f4_arm"): # move_from_gap1_to_default_main
        print("[Arm] f4_arm")
        arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/f2_pose1_default")
        subprocess.run([arm_path], check=True)
        time.sleep(1.5)
        arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/default_move")
        subprocess.run([arm_path], check=True)
        time.sleep(1.5)
        sock.sendto(b"f5", (UDP_IP, MAIN_PORT))    

    elif msg.startswith("f5_sound"): # move_to_charger_start_sound
        print("[Arm] f5_sound")
        arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/Move_charger") 
        subprocess.run([arm_path], check=True)
        time.sleep(1)

    elif msg.startswith("f6_sound"): # move_to_charger_finish_sound
        print("[Arm] f6_sound")
        arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/Move_done") 
        subprocess.run([arm_path], check=True)
        time.sleep(1)

# sound
       
    # elif msg.startswith("chewing_problem_sound"):
    #     print("[Arm] chewing_problem_sound")
    #     arm_path = os.path.expanduser("/home/nrel/ARPA-H/rbmove_jh/build/Meal_pleasechew") 
    #     subprocess.run([arm_path], check=True)
    #     time.sleep(0.01)
    #     print("[Arm] chewing_problem_sound DONE")


    
############### Meal finish #######################

############### Brush start #######################

############### Brush start #######################

############### Reposition start ##################

    

    

################## Reposition finish ##########################

################## Fall prevention start ######################

    

    #########################

    

    

    