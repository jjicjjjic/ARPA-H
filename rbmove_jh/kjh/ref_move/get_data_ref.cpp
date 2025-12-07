#include <iostream>
#include <fstream>
#include <array>
#include <thread>
#include <chrono>
#include <atomic>
#include <future>
#include <vector>
#include <sstream>
#include <cstring>
#include <sys/socket.h>
#include <netinet/in.h>
#include <unistd.h>
#include "rbpodo/rbpodo.hpp"

#define UDP_PORT 12345
#define BUFFER_SIZE 1024

using namespace rb;

bool check_quit() {
    std::string input;
    std::getline(std::cin, input);
    return (input == "q" || input == "Q");
}

int main() {
    try {
        // ============================================================
        // [STEP 1] UDP로 Reference ArUco 좌표 수신 (티칭 기준점 저장)
        // ============================================================
        int sockfd;
        char buffer[BUFFER_SIZE];
        struct sockaddr_in servaddr, cliaddr;

        if ((sockfd = socket(AF_INET, SOCK_DGRAM, 0)) < 0) {
            perror("socket creation failed");
            return 1;
        }

        memset(&servaddr, 0, sizeof(servaddr));
        servaddr.sin_family = AF_INET;
        servaddr.sin_addr.s_addr = INADDR_ANY;
        servaddr.sin_port = htons(UDP_PORT);

        if (bind(sockfd, (const struct sockaddr *)&servaddr, sizeof(servaddr)) < 0) {
            perror("bind failed");
            return 1;
        }

        std::cout << ">>> [Step 1] Waiting for Global Vision data to set REFERENCE pose..." << std::endl;

        // 한 번만 수신하여 기준점으로 삼음
        socklen_t len = sizeof(cliaddr);
        int n = recvfrom(sockfd, (char *)buffer, BUFFER_SIZE, MSG_WAITALL, (struct sockaddr *)&cliaddr, &len);
        buffer[n] = '\0';
        
        // 데이터 파싱 (UDP 포맷: id, x, y, z, rx, ry, rz)
        std::string data(buffer);
        std::stringstream ss(data);
        std::string item;
        std::vector<double> ref_marker_data;
        while (std::getline(ss, item, ',')) {
            ref_marker_data.push_back(std::stod(item));
        }
        close(sockfd); // 소켓 닫기

        if (ref_marker_data.size() < 7) {
            std::cerr << "Error: Invalid UDP data." << std::endl;
            return 1;
        }

        // [저장] ref_pose.txt에 기준 마커 좌표 저장
        // ref_marker_data[1~3]: X, Y, Z (m)
        // ref_marker_data[4~6]: Rx, Ry, Rz (Rodrigues vector)
        std::ofstream ref_file("/home/nrel/ARPA-H/rbmove_jh/kjh/ref_data/ref_pose.txt");
        if (ref_file.is_open()) {
            ref_file << ref_marker_data[1] << " " << ref_marker_data[2] << " " << ref_marker_data[3] << " "
                     << ref_marker_data[4] << " " << ref_marker_data[5] << " " << ref_marker_data[6];
            ref_file.close();
            std::cout << ">>> Reference Pose Saved to 'ref_pose.txt'!" << std::endl;
        } else {
            std::cerr << "Failed to save reference file." << std::endl;
            return 1;
        }


        // ============================================================
        // [STEP 2] 로봇 팔 궤적 녹화 (기존 get_data 로직)
        // ============================================================
        podo::Cobot robot("10.0.2.7");
        podo::ResponseCollector rc;

        // 저장할 CSV 파일 경로 (필요에 따라 수정)
        std::ofstream file("/home/nrel/ARPA-H/rbmove_jh/kjh/ref_data/test.csv");
        if (!file.is_open()) {
            std::cerr << "CSV 파일을 열 수 없습니다." << std::endl;
            return 1;
        }

        file << "Time(ms),X(mm),Y(mm),Z(mm),Roll(deg),Pitch(deg),Yaw(deg)\n";
        std::cout << ">>> Start Recording Trajectory. Press 'q' to stop.\n";

        std::future<bool> quit_future = std::async(std::launch::async, check_quit);

        while (quit_future.wait_for(std::chrono::milliseconds(1)) == std::future_status::timeout) {
            std::array<double, 6> tcp_pose{};
            robot.get_tcp_info(rc, tcp_pose);
            rc.error().throw_if_not_empty();

            auto now = std::chrono::steady_clock::now().time_since_epoch();
            long long ms = std::chrono::duration_cast<std::chrono::milliseconds>(now).count();

            file << ms << ",";
            for (int j = 0; j < 6; ++j) {
                file << tcp_pose[j];
                if (j < 5) file << ",";
            }
            file << "\n";

            std::this_thread::sleep_for(std::chrono::milliseconds(10)); 
        }

        file.close();
        std::cout << "'q' detected. Recording finished.\n";

    } catch (const std::exception& e) {
        std::cerr << e.what() << std::endl;
        return 1;
    }

    return 0;
}