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
        # arm_path = os.path.expanduser("~/rbpodo_kdh/build/practice1_251015")
        # subprocess.run([arm_path], check=True)
        time.sleep(1.5)
        print("[Arm] move_to_spoon_finish")
        sock.sendto(b"move_to_spoon_finish_arm", (UDP_IP, MAIN_PORT))

    elif msg.startswith("move_next_spoon_start_main"):
        print("[Arm] move_next_spoon_start")
        # arm_path = os.path.expanduser("~/rbpodo_kdh/build/practice1_251015")
        # subprocess.run([arm_path], check=True)
        time.sleep(1.5)
        print("[Arm] move_next_spoon_finish")
        sock.sendto(b"move_next_spoon_finish_arm", (UDP_IP, MAIN_PORT))

    elif msg.startswith("move_to_food1_start_main"):
        print("[Arm] move_to_food1_start")
        # arm_path = os.path.expanduser("~/rbpodo_kdh/build/practice1_251015")
        # subprocess.run([arm_path], check=True)
        time.sleep(1.5)
        print("[Arm] move_to_food1_finish")
        sock.sendto(b"move_to_food1_finish_arm", (UDP_IP, MAIN_PORT))

    elif msg.startswith("move_front_mouth_for_meal_start_main"):
        print("[Arm] move_front_mouth_for_meal_start")
        # arm_path = os.path.expanduser("~/rbpodo_kdh/build/practice1_251015")
        # subprocess.run([arm_path], check=True)
        time.sleep(1.5)
        print("[Arm] move_front_mouth_for_meal_finish")
        sock.sendto(b"move_front_mouth_for_meal_finish_arm", (UDP_IP, MAIN_PORT))

    elif msg.startswith("move_to_food2_start_main"):
        print("[Arm] move_to_food2_start")
        # arm_path = os.path.expanduser("~/rbpodo_kdh/build/practice1_251015")
        # subprocess.run([arm_path], check=True)
        time.sleep(1.5)
        print("[Arm] move_to_food2_finish")
        sock.sendto(b"move_to_food2_finish_arm", (UDP_IP, MAIN_PORT))

    elif msg.startswith("move_to_food3_start_main"):
        print("[Arm] move_to_food3_start")
        # arm_path = os.path.expanduser("~/rbpodo_kdh/build/practice1_251015")
        # subprocess.run([arm_path], check=True)
        time.sleep(1.5)
        print("[Arm] move_to_food3_finish")
        sock.sendto(b"move_to_food3_finish_arm", (UDP_IP, MAIN_PORT))

    elif msg.startswith("move_to_food4_start_main"):
        print("[Arm] move_to_food4_start")
        # arm_path = os.path.expanduser("~/rbpodo_kdh/build/practice1_251015")
        # subprocess.run([arm_path], check=True)
        time.sleep(1.5)
        print("[Arm] move_to_food4_finish")
        sock.sendto(b"move_to_food4_finish_arm", (UDP_IP, MAIN_PORT))

    elif msg.startswith("move_from_food_to_default_arm_start_main"):
        print("[Arm] move_from_food_to_default_arm_start")
        # arm_path = os.path.expanduser("~/rbpodo_kdh/build/practice1_251015")
        # subprocess.run([arm_path], check=True)
        time.sleep(1.5)
        print("[Arm] move_from_food_to_default_arm_finish")
        # sock.sendto(b"move_to_default_arm_finish_arm", (UDP_IP, MAIN_PORT))

##################### Meal finish ############################

##################### Brush start ############################

    elif msg.startswith("move_from_default_to_comoral_start_main"):
        print("[Arm] move_from_default_to_comoral_start")
        # arm_path = os.path.expanduser("~/rbpodo_kdh/build/practice1_251015")
        # subprocess.run([arm_path], check=True)
        time.sleep(1.5)
        print("[Arm] move_from_default_to_comoral_finish")
        sock.sendto(b"move_from_default_to_comoral_finish_arm", (UDP_IP, MAIN_PORT))

    elif msg.startswith("move_next_comoral_start_main"):
        print("[Arm] move_next_comoral_start")
        # arm_path = os.path.expanduser("~/rbpodo_kdh/build/practice1_251015")
        # subprocess.run([arm_path], check=True)
        time.sleep(1.5)
        print("[Arm] move_next_comoral_finish")
        sock.sendto(b"move_next_comoral_finish_arm", (UDP_IP, MAIN_PORT))

    elif msg.startswith("move_cormal_to_mouth_start_main"):
        print("[Arm] move_cormal_to_mouth_start")
        # arm_path = os.path.expanduser("~/rbpodo_kdh/build/practice1_251015")
        # subprocess.run([arm_path], check=True)
        time.sleep(1.5)
        print("[Arm] move_cormal_to_mouth_finish")
        sock.sendto(b"move_cormal_to_mouth_finish_arm", (UDP_IP, MAIN_PORT))

    elif msg.startswith("move_front_mouth_for_brush_start_main"):
        print("[Arm] move_front_mouth_for_brush_start")
        # arm_path = os.path.expanduser("~/rbpodo_kdh/build/practice1_251015")
        # subprocess.run([arm_path], check=True)
        time.sleep(1.5)
        print("[Arm] move_front_mouth_for_brush_finish")
        sock.sendto(b"move_front_mouth_for_brush_finish_arm", (UDP_IP, MAIN_PORT))

    elif msg.startswith("move_from_mouth_to_comoral_start_main"):
        print("[Arm] move_from_mouth_to_comoral_start")
        # arm_path = os.path.expanduser("~/rbpodo_kdh/build/practice1_251015")
        # subprocess.run([arm_path], check=True)
        time.sleep(1.5)
        print("[Arm] move_from_mouth_to_comoral_finish")
        sock.sendto(b"move_from_mouth_to_comoral_finish_arm", (UDP_IP, MAIN_PORT))

    elif msg.startswith("move_from_comoral_to_default_start_main"):
        print("[Arm] move_from_comoral_to_default_start")
        # arm_path = os.path.expanduser("~/rbpodo_kdh/build/practice1_251015")
        # subprocess.run([arm_path], check=True)
        time.sleep(1.5)
        print("[Arm] move_from_comoral_to_default_finish")
        sock.sendto(b"move_from_comoral_to_default_finish_arm", (UDP_IP, MAIN_PORT))

####################### Brush finish #########################

####################### Reposition start #####################

    elif msg.startswith("move_from_default_to_cushion1_start_main"):
        print("[Arm] move_from_default_to_cushion1_start")
        # arm_path = os.path.expanduser("~/rbpodo_kdh/build/practice1_251015")
        # subprocess.run([arm_path], check=True)
        time.sleep(1.5)
        print("[Arm] move_from_default_to_cushion1_finish")
        # sock.sendto(b"move_from_default_to_cushion_finish_arm", (UDP_IP, MAIN_PORT))

    elif msg.startswith("move_from_cushion1_to_back_start_main"):
        print("[Arm] move_from_cushion1_to_back_start")
        # arm_path = os.path.expanduser("~/rbpodo_kdh/build/practice1_251015")
        # subprocess.run([arm_path], check=True)
        time.sleep(1.5)
        print("[Arm] move_from_cushion1_to_back_finish")
        sock.sendto(b"move_from_cushion1_to_back_finish_arm", (UDP_IP, MAIN_PORT))

    elif msg.startswith("move_from_back_to_cushion2_start_main"):
        print("[Arm] move_from_back_to_cushion2_start")
        # arm_path = os.path.expanduser("~/rbpodo_kdh/build/practice1_251015")
        # subprocess.run([arm_path], check=True)
        time.sleep(1.5)
        print("[Arm] move_from_back_to_cushion2_finish")
        sock.sendto(b"move_from_back_to_cushion2_finish_arm", (UDP_IP, MAIN_PORT))

    elif msg.startswith("move_from_cushion2_to_leg_start_main"):
        print("[Arm] move_from_cushion2_to_leg_start")
        # arm_path = os.path.expanduser("~/rbpodo_kdh/build/practice1_251015")
        # subprocess.run([arm_path], check=True)
        time.sleep(1.5)
        print("[Arm] move_from_cushion2_to_leg_finish")
        sock.sendto(b"move_from_cushion2_to_leg_finish_arm", (UDP_IP, MAIN_PORT))

    elif msg.startswith("move_from_back_to_default_start_main"):
        print("[Arm] move_from_back_to_default_start")
        # arm_path = os.path.expanduser("~/rbpodo_kdh/build/practice1_251015")
        # subprocess.run([arm_path], check=True)
        time.sleep(1.5)
        print("[Arm] move_from_back_to_default_finish")
        sock.sendto(b"move_from_back_to_default_finish_arm", (UDP_IP, MAIN_PORT))

################### Reposition finish ########################

################### Fall prevention start ####################

    elif msg.startswith("prevent_fall_posture_main"):
            print("[Arm] prevent_fall_posture_start")
            # arm_path = os.path.expanduser("~/rbpodo_kdh/build/practice1_251015")
            # subprocess.run([arm_path], check=True)
            time.sleep(1.5)
            print("[Arm] prevent_fall_posture_finish")
            sock.sendto(b"prevent_fall_posture_finish_arm", (UDP_IP, MAIN_PORT))




# sound
    elif msg.startswith("move_to_bed_start_sound"):
        print("[Arm] move_to_bed_start_sound")
        # arm_path = os.path.expanduser("~/rbpodo_kdh/build/practice2_251015") 
        # subprocess.run([arm_path], check=True)
        time.sleep(1.5)
        print("[Arm] move_to_bed_start_sound DONE")
        # sock.sendto(b"ARM_DONE_FOOD2", (UDP_IP, MAIN_PORT))

    elif msg.startswith("dock_on_start_sound"):
        print("[Arm] dock_on_start_sound")
        # arm_path = os.path.expanduser("~/rbpodo_kdh/build/practice2_251015") 
        # subprocess.run([arm_path], check=True)
        time.sleep(1.5)
        print("[Arm] dock_on_start_sound DONE")
        # sock.sendto(b"ARM_DONE_FOOD2", (UDP_IP, MAIN_PORT))

    elif msg.startswith("dock_on_finish_sound"):
        print("[Arm] dock_on_finish_sound")
        # arm_path = os.path.expanduser("~/rbpodo_kdh/build/practice2_251015") 
        # subprocess.run([arm_path], check=True)
        time.sleep(1.5)
        print("[Arm] dock_on_finish_sound DONE")
        # sock.sendto(b"ARM_DONE_FOOD2", (UDP_IP, MAIN_PORT))

    elif msg.startswith("meal_start_sound"):
        print("[Arm] meal_start_sound")
        # arm_path = os.path.expanduser("~/rbpodo_kdh/build/practice2_251015") 
        # subprocess.run([arm_path], check=True)
        time.sleep(1.5)
        print("[Arm] meal_start_sound DONE")
        # sock.sendto(b"ARM_DONE_FOOD2", (UDP_IP, MAIN_PORT))

    elif msg.startswith("meal_finish_sound"):
        print("[Arm] meal_finish_sound")
        # arm_path = os.path.expanduser("~/rbpodo_kdh/build/practice2_251015") 
        # subprocess.run([arm_path], check=True)
        time.sleep(1.5)
        print("[Arm] meal_finish_sound DONE")
        # sock.sendto(b"ARM_DONE_FOOD2", (UDP_IP, MAIN_PORT))
    
############### Meal finish #######################

############### Brush start #######################

    elif msg.startswith("brush_start_sound"):
        print("[Arm] brush_start_sound")
        # arm_path = os.path.expanduser("~/rbpodo_kdh/build/practice2_251015") 
        # subprocess.run([arm_path], check=True)
        time.sleep(1.5)
        print("[Arm] brush_start_sound DONE")
        # sock.sendto(b"ARM_DONE_FOOD2", (UDP_IP, MAIN_PORT))

    elif msg.startswith("bite_cormal_sound"):
        print("[Arm] bite_cormal_sound")
        # arm_path = os.path.expanduser("~/rbpodo_kdh/build/practice2_251015") 
        # subprocess.run([arm_path], check=True)
        time.sleep(1.5)
        print("[Arm] bite_cormal_sound DONE")
        # sock.sendto(b"ARM_DONE_FOOD2", (UDP_IP, MAIN_PORT))

    elif msg.startswith("brush_finish_sound"):
        print("[Arm] brush_finish_sound")
        # arm_path = os.path.expanduser("~/rbpodo_kdh/build/practice2_251015") 
        # subprocess.run([arm_path], check=True)
        time.sleep(1.5)
        print("[Arm] brush_finish_sound DONE")
        # sock.sendto(b"ARM_DONE_FOOD2", (UDP_IP, MAIN_PORT))

############### Brush start #######################

############### Reposition start ##################

    elif msg.startswith("reposition_start_sound"):
        print("[Arm] reposition_start_sound")
        # arm_path = os.path.expanduser("~/rbpodo_kdh/build/practice2_251015") 
        # subprocess.run([arm_path], check=True)
        time.sleep(1.5)
        print("[Arm] reposition_start_sound DONE")
        # sock.sendto(b"ARM_DONE_FOOD2", (UDP_IP, MAIN_PORT))

    elif msg.startswith("reposition_finish_sound"):
        print("[Arm] reposition_finish_sound")
        # arm_path = os.path.expanduser("~/rbpodo_kdh/build/practice2_251015") 
        # subprocess.run([arm_path], check=True)
        time.sleep(1.5)
        print("[Arm] reposition_finish_sound DONE")
        # sock.sendto(b"ARM_DONE_FOOD2", (UDP_IP, MAIN_PORT))

################## Reposition finish ##########################

################## Fall prevention start ######################

    elif msg.startswith("move_to_gap1_sound"):
        print("[Arm] move_to_gap1_sound")
        # arm_path = os.path.expanduser("~/rbpodo_kdh/build/practice2_251015") 
        # subprocess.run([arm_path], check=True)
        time.sleep(1.5)
        print("[Arm] move_to_gap1_sound DONE")
        # sock.sendto(b"ARM_DONE_FOOD2", (UDP_IP, MAIN_PORT))

    #########################

    elif msg.startswith("dock_off_start_sound"):
        print("[Arm] dock_off_start_sound")
        # arm_path = os.path.expanduser("~/rbpodo_kdh/build/practice2_251015") 
        # subprocess.run([arm_path], check=True)
        time.sleep(1.5)
        print("[Arm] dock_off_start_sound DONE")
        # sock.sendto(b"ARM_DONE_FOOD2", (UDP_IP, MAIN_PORT))

    elif msg.startswith("dock_off_finish_sound"):
        print("[Arm] dock_off_finish_sound")
        # arm_path = os.path.expanduser("~/rbpodo_kdh/build/practice2_251015") 
        # subprocess.run([arm_path], check=True)
        time.sleep(1.5)
        print("[Arm] dock_off_finish_sound DONE")
        # sock.sendto(b"ARM_DONE_FOOD2", (UDP_IP, MAIN_PORT))

    elif msg.startswith("move_to_charger_start_sound"):
        print("[Arm] move_to_charger_start_sound")
        # arm_path = os.path.expanduser("~/rbpodo_kdh/build/practice2_251015") 
        # subprocess.run([arm_path], check=True)
        time.sleep(1.5)
        print("[Arm] move_to_charger_start_sound DONE")
        # sock.sendto(b"ARM_DONE_FOOD2", (UDP_IP, MAIN_PORT))

    elif msg.startswith("move_to_charger_finish_sound"):
        print("[Arm] move_to_charger_finish_sound")
        # arm_path = os.path.expanduser("~/rbpodo_kdh/build/practice2_251015") 
        # subprocess.run([arm_path], check=True)
        time.sleep(1.5)
        print("[Arm] move_to_charger_finish_sound DONE")
        # sock.sendto(b"ARM_DONE_FOOD2", (UDP_IP, MAIN_PORT))
