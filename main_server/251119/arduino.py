import serial
import socket

PORT = '/dev/ttyUSB0' #나중에 컴에 연결해보고 다른 포트에 연결됐으면 수정필요
BAUD = 115200
UDP_IP = "127.0.0.1"
MAIN_PORT = 50000

ser = serial.Serial(PORT, BAUD, timeout=1)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

print("[Relay] Listening Arduino serial...")

while True:
    try:
        if ser.in_waiting > 0:
            msg = ser.readline().decode(errors="ignore").strip()
            if msg:
                print(f"[Arduino→UDP] {msg}")
                sock.sendto(msg.encode(), (UDP_IP, MAIN_PORT))
    except Exception as e:
        print(f"[Relay Error] {e}")