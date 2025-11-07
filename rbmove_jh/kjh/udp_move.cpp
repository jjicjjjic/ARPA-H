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

std::array<double, 9> eulerToRotationMatrix(double roll, double pitch, double yaw) {
    double cr = cos(roll), sr = sin(roll), cp = cos(pitch), sp = sin(pitch), cy = cos(yaw), sy = sin(yaw);
    return { cy*cp, cy*sp*sr - sy*cr, cy*sp*cr + sy*sr, sy*cp, sy*sp*sr + cy*cr, sy*sp*cr - cy*sr, -sp, cp*sr, cp*cr };
}

std::array<double, 3> rotationMatrixToEuler(const std::array<double, 9>& R) {
    double roll, pitch, yaw;
    double sy = std::sqrt(R[0]*R[0] + R[3]*R[3]);
    if (sy > 1e-6) {
        roll = std::atan2(R[7], R[8]);
        pitch = std::atan2(-R[6], sy);
        yaw = std::atan2(R[3], R[0]);
    } else {
        roll = std::atan2(-R[5], R[4]);
        pitch = std::atan2(-R[6], sy);
        yaw = 0;
    }
    return {roll * 180.0 / M_PI, pitch * 180.0 / M_PI, yaw * 180.0 / M_PI};
}

std::array<double, 9> rodriguesToRotationMatrix(const std::array<double, 3>& rvec) {
    double angle = std::sqrt(rvec[0]*rvec[0] + rvec[1]*rvec[1] + rvec[2]*rvec[2]);
    if (angle < 1e-9) return {1,0,0, 0,1,0, 0,0,1};
    std::array<double, 3> axis = {rvec[0]/angle, rvec[1]/angle, rvec[2]/angle};
    double c = cos(angle), s = sin(angle), t = 1 - c;
    double x = axis[0], y = axis[1], z = axis[2];
    return { t*x*x + c, t*x*y - s*z, t*x*z + s*y, t*x*y + s*z, t*y*y + c, t*y*z - s*x, t*x*z - s*y, t*y*z + s*x, t*z*z + c };
}

std::array<double, 3> matrix_x_vector(const std::array<double, 9>& R, const std::array<double, 3>& v) {
    return {
        R[0]*v[0] + R[1]*v[1] + R[2]*v[2],
        R[3]*v[0] + R[4]*v[1] + R[5]*v[2],
        R[6]*v[0] + R[7]*v[1] + R[8]*v[2]
    };
}

std::array<double, 9> matrix_x_matrix(const std::array<double, 9>& A, const std::array<double, 9>& B) {
    std::array<double, 9> C{};
    for (int i = 0; i < 3; ++i) for (int j = 0; j < 3; ++j) for (int k = 0; k < 3; ++k) C[i*3 + j] += A[i*3 + k] * B[k*3 + j];
    return C;
}

std::array<double, 9> transposeMatrix3x3(const std::array<double, 9>& M) {
    std::array<double, 9> Mt{};
    for (int i = 0; i < 3; ++i)
        for (int j = 0; j < 3; ++j)
            Mt[i*3 + j] = M[j*3 + i];
    return Mt;
}


int main() {

    podo::Cobot robot("10.0.2.7");
    podo::ResponseCollector rc;

    // robot.set_operation_mode(rc, podo::OperationMode::Real);
    robot.set_operation_mode(rc, podo::OperationMode::Simulation);
    rc = rc.error().throw_if_not_empty();

    // 속도 설정
    robot.set_speed_bar(rc, 0.3);
    robot.flush(rc);

    const std::array<double, 3> t_tcp_to_camera = {0.010, -0.029, 0.048}; 
    const std::array<double, 9> R_tcp_to_camera = {
        -1, 0, 0,
        0, -1, 0,
        0, 0, 1  
    };

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
    //---
    std::array<double, 6> current_commanded_pose;

    // --- [새로운 로직 STEP 2] ---
    // 이 변수를 로봇의 현재 실제 포즈로 초기화합니다.
    { // 임시 스코프
        std::array<double, 6> initial_tcp_pose_mm_deg;
        robot.get_tcp_info(rc, initial_tcp_pose_mm_deg);
        rc.error().throw_if_not_empty();

        current_commanded_pose = {
            initial_tcp_pose_mm_deg[0], // X (mm)
            initial_tcp_pose_mm_deg[1], // Y (mm)
            initial_tcp_pose_mm_deg[2], // Z (mm)
            initial_tcp_pose_mm_deg[3],          // R (deg)
            initial_tcp_pose_mm_deg[4],          // P (deg)
            initial_tcp_pose_mm_deg[5]           // Y (deg)
        };
        std::cout << "Initial robot pose set." << std::endl;
    }
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
        int n = recvfrom(sockfd, (char *)buffer, BUFFER_SIZE, MSG_WAITALL, (struct sockaddr *) &cliaddr, &len);
        buffer[n] = '\0';
        std::string data(buffer);

        std::stringstream ss(data);
        std::string item;
        std::vector<double> parsed_data;
        while (std::getline(ss, item, ',')) {
            parsed_data.push_back(stod(item));
        }
        if (parsed_data.size() != 7) continue;

        double marker_depth_from_camera = parsed_data[3]; 

        if (marker_depth_from_camera < MIN_VALID_DEPTH || 
            marker_depth_from_camera > MAX_VALID_DEPTH) 
        {
            // 유효 범위를 벗어남
            std::cout << std::fixed << std::setprecision(3);
            std::cout << "--- Depth (" << marker_depth_from_camera * 100.0 
                      << " cm) is outside valid range. Ignoring frame. ---" << std::endl;
            
            // 이 프레임에 대한 모든 계산을 건너뛰고 다음 UDP 패킷을 기다립니다.
            continue; 
        }

        // ===================================================================
        // ===== [누락된 부분 1] UDP 데이터 -> 변수 할당 =====
        // ===================================================================
        std::array<double, 3> t_cam_to_marker = {parsed_data[1], parsed_data[2], parsed_data[3]};
        std::array<double, 3> rvec_cam_to_marker = {parsed_data[4], parsed_data[5], parsed_data[6]};
        std::array<double, 9> R_cam_to_marker = rodriguesToRotationMatrix(rvec_cam_to_marker);

        // ===================================================================
        // ===== [누락된 부분 2] 로봇 TCP 정보 -> 변수 할당 =====
        // ===================================================================
        std::array<double, 6> current_tcp_pose_mm_deg{};
        robot.get_tcp_info(rc, current_tcp_pose_mm_deg);
        std::array<double, 3> t_base_to_tcp = {
            current_tcp_pose_mm_deg[0] / 1000.0,
            current_tcp_pose_mm_deg[1] / 1000.0,
            current_tcp_pose_mm_deg[2] / 1000.0
        };
        std::array<double, 9> R_base_to_tcp = eulerToRotationMatrix(
            current_tcp_pose_mm_deg[3] * M_PI / 180.0,
            current_tcp_pose_mm_deg[4] * M_PI / 180.0,
            current_tcp_pose_mm_deg[5] * M_PI / 180.0
        );
        
        // --- [계산 과정] ---
        // 1. 베이스 -> 카메라 계산 (T_base_to_cam = T_base_to_tcp * T_tcp_to_camera)
        std::array<double, 9> RT_base_to_tcp = transposeMatrix3x3(R_base_to_tcp);
        std::array<double, 9> R_base_to_cam = matrix_x_matrix(R_tcp_to_camera, RT_base_to_tcp);
        std::array<double, 3> t_tcp_to_cam_in_base = matrix_x_vector(R_base_to_tcp, t_tcp_to_camera);
        std::array<double, 3> t_base_to_cam = {
            t_base_to_tcp[0] + t_tcp_to_cam_in_base[0],
            t_base_to_tcp[1] + t_tcp_to_cam_in_base[1],
            t_base_to_tcp[2] + t_tcp_to_cam_in_base[2]
        };
        
        // 2. 최종: 베이스 -> 마커 계산 (T_base_to_marker = T_base_to_cam * T_cam_to_marker)
        std::array<double, 9> RT_base_to_cam = transposeMatrix3x3(R_base_to_cam);
        std::array<double, 9> R_base_to_marker = matrix_x_matrix(RT_base_to_cam, R_cam_to_marker);
        std::array<double, 3> t_cam_to_marker_in_base = matrix_x_vector(R_base_to_cam, t_cam_to_marker);
        std::array<double, 3> t_base_to_marker = {
            t_base_to_cam[0] + t_cam_to_marker_in_base[0],
            t_base_to_cam[1] + t_cam_to_marker_in_base[1],
            t_base_to_cam[2] + t_cam_to_marker_in_base[2]
        };
        
        // --- [최종 결과 출력] ---
        std::array<double, 3> euler_base_to_marker_deg = rotationMatrixToEuler(R_base_to_marker);
        
        std::cout << "================================================================" << std::endl;
        std::cout << ">>> ArUco Pose in Base Frame <<<" << std::endl;
        std::cout << "================================================================" << std::endl;
        std::cout << std::fixed << std::setprecision(3);
        std::cout << "Position (mm) [X, Y, Z] : ["
                  << t_base_to_marker[0] * 1000.0 << ", "
                  << t_base_to_marker[1] * 1000.0 << ", "
                  << t_base_to_marker[2] * 1000.0 << "]" << std::endl;

        std::cout << "Orientation (deg) [R, P, Y] : ["
                  << euler_base_to_marker_deg[0] << ", "
                  << euler_base_to_marker_deg[1] << ", "
                  << euler_base_to_marker_deg[2] << "]" << std::endl;

        
        std::array<double, 6> aruco_target_pose = {
            t_base_to_marker[0]* 1000.0,       // Position X
            t_base_to_marker[1]* 1000.0,       // Position Y
            t_base_to_marker[2]* 1000.0,       // Position Z
            euler_base_to_marker_deg[0], // Orientation R (Roll)
            euler_base_to_marker_deg[1], // Orientation P (Pitch)
            euler_base_to_marker_deg[2]  // Orientation Y (Yaw)
        };

        if (has_last_valid_pose) {
            double dx = aruco_target_pose[0] - last_valid_aruco_pose[0]; // (mm - mm)
            double dy = aruco_target_pose[1] - last_valid_aruco_pose[1]; // (mm - mm)
            double dz = aruco_target_pose[2] - last_valid_aruco_pose[2]; // (mm - mm)
            double distance_jump = std::sqrt(dx*dx + dy*dy + dz*dz);

            if (distance_jump > MAX_JUMP_MM) { // MAX_JUMP_MM 으로 변경
                std::cout << std::fixed << std::setprecision(1); // mm 단위이므로 소수점 변경
                std::cout << "--- Spike detected! (" << distance_jump
                          << " mm). Ignoring frame. ---" << std::endl;
                continue; 
            }
        }
        
        last_valid_aruco_pose = aruco_target_pose;
        has_last_valid_pose = true;

        for (int i = 0; i < 6; ++i) {
            current_commanded_pose[i] = current_commanded_pose[i] + 
                                        STEP_FACTOR * (aruco_target_pose[i] - current_commanded_pose[i]);
        }

        std::cout << std::fixed << std::setprecision(4);
        std::cout << ">>> Commanding Waypoint (mm/deg) <<<" << std::endl;
        std::cout << "Pos[X,Y,Z]: [" << current_commanded_pose[0] << ", " << current_commanded_pose[1] << ", " << current_commanded_pose[2] << "]" << std::endl;
        std::cout << "Ori[R,P,Y]: [" << current_commanded_pose[3] << ", " << current_commanded_pose[4] << ", " << current_commanded_pose[5] << "]" << std::endl;

        robot.move_servo_l(rc, current_commanded_pose, 0.01, 0.05, 1, 0.05);
        rc.error().throw_if_not_empty();
    }
    

    close(sockfd);
    return 0;
}
