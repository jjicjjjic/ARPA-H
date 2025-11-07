import socket

# --- 설정 ---
# '0.0.0.0'은 이 PC의 모든 네트워크 인터페이스(랜카드)에서
# 들어오는 데이터를 수신하겠다는 의미입니다.
SERVER_IP = '0.0.0.0' 
SERVER_PORT = 12345    # 사용할 포트 번호 (임의로 지정 가능)
BUFFER_SIZE = 1024     # 한 번에 수신할 최대 데이터 크기
# ------------

try:
    # 1. 소켓 생성 (AF_INET: IPv4, SOCK_DGRAM: UDP)
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # 2. 소켓을 지정된 IP와 포트에 바인딩(연결)
    server_socket.bind((SERVER_IP, SERVER_PORT))

    print(f"UDP 서버가 {SERVER_IP}:{SERVER_PORT}에서 수신 대기 중입니다...")

    while True:
        # 3. 클라이언트로부터 데이터 수신
        # data: 수신된 데이터 (bytes)
        # addr: 데이터를 보낸 클라이언트의 주소 (IP, port)
        data, addr = server_socket.recvfrom(BUFFER_SIZE)
        
        # 수신된 데이터를 utf-8로 디코딩 (문자열로 변환)
        message = data.decode('utf-8')
        
        print(f"수신된 메시지 (from {addr}): {message}")

        # 4. (선택 사항) 클라이언트에게 응답 보내기
        response_message = "메시지를 성공적으로 수신했습니다."
        server_socket.sendto(response_message.encode('utf-8'), addr)

except KeyboardInterrupt:
    print("\n서버를 종료합니다.")
finally:
    # 5. 소켓 닫기
    server_socket.close()
    print("소켓이 닫혔습니다.")