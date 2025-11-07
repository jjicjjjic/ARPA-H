import socket
import time

# --- 설정 ---
# 중요: 여기에 '서버(수신측) PC'의 실제 IP 주소를 입력해야 합니다.
SERVER_IP = '143.248.67.67'  # 예시 IP. 서버 PC의 IP로 반드시 변경하세요!
SERVER_PORT = 12345         # 서버와 동일한 포트 번호
# ------------

try:
    # 1. 소켓 생성 (AF_INET: IPv4, SOCK_DGRAM: UDP)
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # (선택 사항) 서버로부터 응답을 기다릴 타임아웃 설정 (5초)
    client_socket.settimeout(5.0)

    message_count = 0
    while True:
        message_count += 1
        message = f"테스트 메시지입니다. (번호: {message_count})"
        
        # 2. 메시지를 utf-8로 인코딩하여 서버로 전송
        client_socket.sendto(message.encode('utf-8'), (SERVER_IP, SERVER_PORT))
        print(f"[{message_count}] 서버({SERVER_IP}:{SERVER_PORT})로 메시지 전송: {message}")

        # 3. (선택 사항) 서버로부터 응답 수신
        try:
            data, addr = client_socket.recvfrom(1024)
            print(f"서버로부터 응답: {data.decode('utf-8')}")
        except socket.timeout:
            print("서버로부터 응답 시간 초과")

        # 1초 대기 후 다음 메시지 전송
        time.sleep(1)

except KeyboardInterrupt:
    print("\n클라이언트를 종료합니다.")
finally:
    # 4. 소켓 닫기
    client_socket.close()
    print("소켓이 닫혔습니다.")