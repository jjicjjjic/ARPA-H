#include <iostream>
#include <string>
#include <cstring>
#include <arpa/inet.h>
#include <unistd.h>

int main() {
    const char* ROBOT_IP = "10.0.2.7";   // ⚠️ 실제 로봇 제어반 IP로 변경
    const int ROBOT_PORT = 5000;         // 명령 포트
    const std::string CMD = "interface_music_on \"도킹_해제_완료했습니다\", 0,1,100,0,0\n"; // 반드시 \n 포함

    // 1. 소켓 생성
    int sock = socket(AF_INET, SOCK_STREAM, 0);
    if (sock < 0) {
        std::cerr << "[Error] Socket creation failed\n";
        return 1;
    }

    // 2. 서버 주소 설정
    sockaddr_in serv_addr{};
    serv_addr.sin_family = AF_INET;
    serv_addr.sin_port = htons(ROBOT_PORT);
    if (inet_pton(AF_INET, ROBOT_IP, &serv_addr.sin_addr) <= 0) {
        std::cerr << "[Error] Invalid IP address format\n";
        close(sock);
        return 1;
    }

    // 3. 제어반 연결
    if (connect(sock, (sockaddr*)&serv_addr, sizeof(serv_addr)) < 0) {
        std::cerr << "[Error] Connection to robot controller failed\n";
        close(sock);
        return 1;
    }

    std::cout << "[RB] Connected to robot controller at " << ROBOT_IP << ":" << ROBOT_PORT << std::endl;

    // 4. 명령 전송
    ssize_t sent = send(sock, CMD.c_str(), CMD.size(), 0);
    if (sent < 0) {
        std::cerr << "[Error] Failed to send command\n";
        close(sock);
        return 1;
    }

    std::cout << "[RB] Sent command: " << CMD;

    // 5. 응답 수신
    char buffer[1024] = {0};
    ssize_t received = read(sock, buffer, sizeof(buffer)-1);
    if (received > 0) {
        std::cout << "[RB] Response: " << buffer << std::endl;
    } else {
        std::cerr << "[Warning] No response received from robot.\n";
    }

    // 6. 연결 종료
    close(sock);
    std::cout << "[RB] Disconnected.\n";

    return 0;
}
