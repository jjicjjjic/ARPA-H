#include <iostream>
#include <string>
#include <cstring>
#include <arpa/inet.h>
#include <unistd.h>

void send_command_to_robot(const std::string& robot_ip, int robot_port, const std::string& cmd) {
    int sock = socket(AF_INET, SOCK_STREAM, 0);
    if (sock < 0) {
        std::cerr << "[Error] Socket creation failed\n";
        return;
    }

    sockaddr_in serv_addr{};
    serv_addr.sin_family = AF_INET;
    serv_addr.sin_port = htons(robot_port);
    if (inet_pton(AF_INET, robot_ip.c_str(), &serv_addr.sin_addr) <= 0) {
        std::cerr << "[Error] Invalid IP address format\n";
        close(sock);
        return;
    }

    if (connect(sock, (sockaddr*)&serv_addr, sizeof(serv_addr)) < 0) {
        std::cerr << "[Error] Connection to robot controller failed\n";
        close(sock);
        return;
    }

    std::cout << "[RB] Connected to robot controller (" << robot_ip << ":" << robot_port << ")\n";

    std::string cmd_with_newline = cmd + "\n"; // 반드시 '\n' 포함
    send(sock, cmd_with_newline.c_str(), cmd_with_newline.size(), 0);
    std::cout << "[RB] Sent command: " << cmd << std::endl;

    char buffer[1024] = {0};
    ssize_t received = read(sock, buffer, sizeof(buffer)-1);
    if (received > 0) {
        std::cout << "[RB] Response: " << buffer << std::endl;
    } else {
        std::cout << "[Warning] No response received.\n";
    }

    close(sock);
    std::cout << "[RB] Disconnected.\n\n";
}

int main() {
    const std::string ROBOT_IP = "10.0.2.7"; // ⚠️ 실제 로봇 IP로 변경
    const int ROBOT_PORT = 5000;

    std::cout << "=============================\n";
    std::cout << " RB Sound Control Interface\n";
    std::cout << "=============================\n";
    std::cout << "Commands:\n";
    std::cout << "  1 : Play music  (interface_music_on)\n";
    std::cout << "  2 : Stop music  (interface_music_off)\n";
    std::cout << "  q : Quit\n";
    std::cout << "=============================\n";

    while (true) {
        std::cout << "\nSelect command (1/2/q): ";
        char choice;
        std::cin >> choice;

        if (choice == '1') {
            // 음악 ON
            std::string cmd = "interface_music_on \"Over_the_Horizon\", 0,1,10,0,0";
            send_command_to_robot(ROBOT_IP, ROBOT_PORT, cmd);
        } 
        else if (choice == '2') {
            // 음악 OFF
            std::string cmd = "interface_music_off";
            send_command_to_robot(ROBOT_IP, ROBOT_PORT, cmd);
        } 
        else if (choice == 'q' || choice == 'Q') {
            std::cout << "Exiting program...\n";
            break;
        } 
        else {
            std::cout << "Invalid input. Try again.\n";
        }
    }

    return 0;
}
