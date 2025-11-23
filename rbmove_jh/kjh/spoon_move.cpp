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

    int approach_state = 0;          
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

        // --- (현재 로봇 위치 갱신) ---
        std::array<double, 6> current_tcp_pose_mm_deg{};
        robot.get_tcp_info(rc, current_tcp_pose_mm_deg);
        
        // current_commanded_pose를 현재 위치로 동기화 (매우 중요)
        std::array<double, 6> next_cmd = current_tcp_pose_mm_deg;

        // ===================================================================
        // [시퀀스 제어] 1. 접근(20cm) -> 2. 상승(15cm)
        // ===================================================================

        if (approach_state == 0) { 
            // [STEP 1] 마커 20cm 앞까지 접근 (Visual Servoing)
            
            double target_dist = 0.27; // 목표 거리 27cm
            double err_x = parsed_data[1]; 
            double err_y = parsed_data[2];
            double dist_current = parsed_data[3]; 
            double dist_error   = dist_current - target_dist; 

            double ALIGN_TOL = 0.02; // 2cm
            double STOP_TOL  = 0.01; // 1cm

            // 도착 확인
            if (dist_error < STOP_TOL && 
                std::abs(err_x) < ALIGN_TOL && 
                std::abs(err_y) < ALIGN_TOL) 
            {
                std::cout << ">>> [STEP 1 COMPLETE] Target Reached! Preparing to Move Up. <<<" << std::endl;
                approach_state = 1; // 다음 단계로 넘어감
                continue; 
            }

            // 이동 로직 (Align -> Forward)
            double delta_x = 0.0;
            double delta_y = 0.0;
            double delta_z = 0.0;

            bool need_align = (std::abs(err_x) > ALIGN_TOL || std::abs(err_y) > ALIGN_TOL);

            if (need_align) {
                std::cout << "[Step 1: Aligning] ";
                delta_x = 0.0;    
                delta_y = -err_x; 
                delta_z = -err_y; 
            } else {
                std::cout << "[Step 1: Forward ] ";
                if (dist_error > 0.005) delta_x = dist_error; 
                else delta_x = 0.0;
                delta_y = 0.0;
                delta_z = 0.0;
            }

            double GAIN = 0.04; 
            next_cmd[0] += GAIN * delta_x * 1000.0;
            next_cmd[1] += GAIN * delta_y * 1000.0;
            next_cmd[2] += GAIN * delta_z * 1000.0;
            
            // 로그
            std::cout << "Dist: " << std::fixed << std::setprecision(1) << dist_current*1000 
                      << "mm | ErrX: " << err_x*1000 << " | CmdX: " << delta_x << std::endl;

        } 
        else if (approach_state == 1) {
            // [STEP 2] 15cm 수직 상승 (Open Loop)
            // 마커를 안 보고 로봇 좌표계 기준으로 그냥 위로 올립니다.
            
            std::cout << ">>> [STEP 2] Moving Up 15cm... <<<" << std::endl;
            
            // 현재 위치에서 Z축(베이스 기준 상방)으로 150mm 더한 목표 설정
            // 주의: move_servo_l은 보간 이동이므로, 여기서는 while루프를 돌며 조금씩 올리는 게 아니라
            // 한 번에 명령을 주고 state를 변경하거나, 조금씩 올리는 방식을 선택해야 합니다.
            // 안전하게 조금씩 올리는 방식을 유지합니다.
            
            // 목표 높이 설정 (현재 높이 + 150mm)
            static double target_z_height = 0.0;
            if (target_z_height == 0.0) {
                target_z_height = current_tcp_pose_mm_deg[2] + 150.0; // 15cm 상승 목표
            }

            double z_diff = target_z_height - current_tcp_pose_mm_deg[2];

            if (std::abs(z_diff) < 5.0) { // 5mm 이내 도달 시 완료
                std::cout << ">>> [STEP 2 COMPLETE] Holding Position. <<<" << std::endl;
                approach_state = 2; // 완료 상태
                continue;
            }

            // 천천히 상승
            double LIFT_SPEED = 2.0; // 루프당 2mm씩 상승
            if (z_diff > 0) next_cmd[2] += LIFT_SPEED;
            else next_cmd[2] -= LIFT_SPEED;
            
            std::cout << "Lifting... CurZ: " << current_tcp_pose_mm_deg[2] 
                      << " | TargetZ: " << target_z_height << std::endl;
        }
        else if (approach_state == 2) {
            // [완료 상태] 제자리 유지
            // 아무 명령도 안 보내거나, 현 위치 유지 명령 전송
            std::cout << ">>> [HOLDING] Mission Complete <<<" << std::endl;
            // 굳이 명령 안 보내도 되지만, 안전을 위해 현 위치 유지
        }

        // 안전장치 (최소 높이 제한)
        if (next_cmd[2] < 200.0) next_cmd[2] = 200.0;

        robot.move_servo_l(rc, next_cmd, 0.1, 0.05, 1, 0.05);
        std::this_thread::sleep_for(std::chrono::milliseconds(20));
        rc.error().throw_if_not_empty();
    }
    

    close(sockfd);
    return 0;
}