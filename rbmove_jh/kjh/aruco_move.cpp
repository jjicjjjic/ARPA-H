#include <iostream>
#include <vector>
#include <string>
#include <sstream>
#include <array>
#include <cmath>
#include <iomanip>
#include <sys/socket.h> 
#include <netinet/in.h> 
#include <unistd.h>    
#include "rbpodo/rbpodo.hpp"


#define PORT 12345
#define BUFFER_SIZE 1024
#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif


using namespace rb;



int main() {

    podo::Cobot robot("10.0.2.7");
    podo::ResponseCollector rc;

    robot.set_operation_mode(rc, podo::OperationMode::Real);
    // robot.set_operation_mode(rc, podo::OperationMode::Simulation);
    rc = rc.error().throw_if_not_empty();

    // 속도 설정
    robot.set_speed_bar(rc, 0.3);
    robot.flush(rc);

    // UDP 서버 소켓 설정
    int sockfd;
    char buffer[BUFFER_SIZE];
    struct sockaddr_in servaddr, cliaddr;

    if ((sockfd = socket(AF_INET, SOCK_DGRAM, 0)) < 0) {
        perror("socket creation failed");
        exit(EXIT_FAILURE);
    }

    memset(&servaddr, 0, sizeof(servaddr));
    servaddr.sin_family = AF_INET;
    servaddr.sin_addr.s_addr = INADDR_ANY;
    servaddr.sin_port = htons(PORT);

    if (bind(sockfd, (const struct sockaddr *)&servaddr, sizeof(servaddr)) < 0) {
        perror("bind failed");
        exit(EXIT_FAILURE);
    }
    
    std::cout << "UDP Server is listening on port " << PORT << std::endl;
   
    const double STEP_FACTOR = 0.05; 
    const double MIN_VALID_DEPTH = 0.07; // 7cm
    const double MAX_VALID_DEPTH = 0.50; // 50cm
    
    bool has_last_valid_pose = false;
    std::array<double, 6> last_valid_aruco_pose;
    const double MAX_JUMP_MM = 50;

    std::cout << "UDP Server is listening on port " << PORT << std::endl;
    std::cout << "Applying D405 depth filter: " << MIN_VALID_DEPTH*100.0 << "cm - " 
              << MAX_VALID_DEPTH*100.0 << "cm" << std::endl;

    while (true) {
        socklen_t len = sizeof(cliaddr);
        int n = recvfrom(sockfd, (char *)buffer, BUFFER_SIZE, 0, (struct sockaddr *) &cliaddr, &len);

        // 2. 버퍼에 쌓인 나머지 데이터가 있다면 싹 다 읽어버림 (Non-Blocking)
        while (true) {
            // MSG_DONTWAIT: 데이터가 없으면 기다리지 않고 즉시 -1 리턴
            int n_next = recvfrom(sockfd, (char *)buffer, BUFFER_SIZE, MSG_DONTWAIT, (struct sockaddr *) &cliaddr, &len);
            
            if (n_next < 0) {
                // 더 이상 읽을 데이터가 없음 -> 방금 전 'n'이 가장 최신 데이터임
                break; 
            }
            
            // 새로운 데이터가 있다면, 그게 더 최신이므로 'n'을 갱신하고 루프 계속
            n = n_next; 
        }
        buffer[n] = '\0';
        std::string data(buffer);

        std::stringstream ss(data);
        std::string item;
        std::vector<double> parsed_data;
        while (std::getline(ss, item, ',')) {
            parsed_data.push_back(stod(item));
        }
        if (parsed_data.size() != 7) continue;


        std::array<double, 6> current_commanded_pose{};
        robot.get_tcp_info(rc, current_commanded_pose);
        
        double target_dist = 0.20; // 목표 20cm

        double err_x = parsed_data[1]; 
        double err_y = parsed_data[2];
        double dist_current = parsed_data[3]; 
        double dist_error   = dist_current - target_dist; 

        // 허용 오차
        double ALIGN_TOL = 0.02; // 2cm
        double STOP_TOL  = 0.01; // 1cm

        // 성공 조건 (20cm 이내 진입 시 정지)
        if (dist_error < STOP_TOL && 
            std::abs(err_x) < ALIGN_TOL && 
            std::abs(err_y) < ALIGN_TOL) 
        {
            std::cout << ">>> [SUCCESS] Target Reached (" << dist_current*1000 << "mm) - STOP <<<" << std::endl;
            continue; // 정지
        }

        // 이동 로직
        double delta_x = 0.0;
        double delta_y = 0.0;
        double delta_z = 0.0;

        bool need_align = (std::abs(err_x) > ALIGN_TOL || std::abs(err_y) > ALIGN_TOL);

        if (need_align) {
            std::cout << "[Step 1: Aligning] ";
            delta_x = 0.0;
            // 사용자님 확인: 방향은 기존 유지 (-err)
            delta_y = -err_x; 
            delta_z = -err_y; 
        } else {
            std::cout << "[Step 2: Forward ] ";
            // 거리 제어
            if (dist_error > 0) {
                delta_x = dist_error; 
            } else {
                delta_x = 0.0; // 너무 가까우면 정지
            }
            delta_y = 0.0; 
            delta_z = 0.0;
        }

        // 명령 적용
        double GAIN = 0.04; 

        // "현재 위치" + "델타" = "다음 목표"
        current_commanded_pose[0] += GAIN * delta_x * 1000.0;
        current_commanded_pose[1] += GAIN * delta_y * 1000.0;
        current_commanded_pose[2] += GAIN * delta_z * 1000.0;

        if (current_commanded_pose[2] < 200.0) current_commanded_pose[2] = 200.0;

        std::cout << "Dist: " << std::fixed << std::setprecision(1) << dist_current*1000 
                  << "mm | ErrX: " << err_x*1000 << " | CmdX: " << delta_x << std::endl;

        robot.move_servo_l(rc, current_commanded_pose, 0.1, 0.05, 1, 0.05);
        std::this_thread::sleep_for(std::chrono::milliseconds(20));
        rc.error().throw_if_not_empty();
    }
    

    close(sockfd);
    return 0;
}