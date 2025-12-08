#include <iostream>
#include <fstream>
#include <sstream>
#include <array>
#include <thread>
#include <chrono>
#include <vector>
#include <cmath>
#include <iomanip>
#include <cstring>
#include "rbpodo/rbpodo.hpp"

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

using namespace rb;

// --- [수학 유틸리티] ---
double normalizeAngle(double angle) {
    while (angle > 180.0) angle -= 360.0;
    while (angle < -180.0) angle += 360.0;
    return angle;
}

int main() {
  try {
    podo::Cobot robot("10.0.2.7");
    podo::ResponseCollector rc;
    
    // 테스트 시에는 Simulation 모드 추천, 실제 구동 시 Real 모드
    robot.set_operation_mode(rc, podo::OperationMode::Simulation); 
    // robot.set_operation_mode(rc, podo::OperationMode::Real); 
    rc.error().throw_if_not_empty();
    robot.set_speed_bar(rc, 1.0);
    robot.flush(rc);

    std::cout << std::string(60, '=') << std::endl;
    std::cout << ">>> Manual Trajectory Correction & Save (Axis Flipped)" << std::endl;
    std::cout << std::string(60, '=') << std::endl;

    // ========================================================
    // (1) 사용자 입력: 현재(Current) ArUco 좌표
    // ========================================================
    double cur_cam_id, cur_cam_x, cur_cam_y, cur_cam_z;
    double cur_cam_rx, cur_cam_ry, cur_cam_rz; // Radian 단위 입력 가정

    std::cout << ">>> Please enter the CURRENT ArUco pose data manually." << std::endl;
    std::cout << "Format: ID  X(m)  Y(m)  Z(m)  RX(rad)  RY(rad)  RZ(rad)" << std::endl;
    std::cout << "Input > ";
    
    std::cin >> cur_cam_id >> cur_cam_x >> cur_cam_y >> cur_cam_z >> cur_cam_rx >> cur_cam_ry >> cur_cam_rz;

    double cur_cam_yaw_rad = cur_cam_rz; 

    std::cout << std::endl;
    std::cout << ">>> 1. Current Camera Pose (User Input)" << std::endl;
    std::cout << "   - Pos: [" << cur_cam_x << ", " << cur_cam_y << ", " << cur_cam_z << "]" << std::endl;
    std::cout << "   - Yaw(rad): " << cur_cam_yaw_rad << std::endl;


    // ========================================================
    // (2) 파일에서 기준(Reference) ArUco 좌표 로드
    // ========================================================
    std::ifstream ref_file("/home/nrel/ARPA-H/rbmove_jh/kjh/ref_data/ref_pose.txt");
    if (!ref_file.is_open()) { std::cerr << "Reference file not found!" << std::endl; return 1; }
    
    std::vector<double> ref_vals;
    double val;
    while (ref_file >> val) ref_vals.push_back(val);
    
    double ref_cam_x = ref_vals[0];
    double ref_cam_y = ref_vals[1];
    double ref_cam_z = ref_vals[2];
    double ref_cam_yaw_rad = ref_vals[5]; 

    std::cout << ">>> 2. Reference Camera Pose (Loaded)" << std::endl;
    std::cout << "   - Pos: [" << ref_cam_x << ", " << ref_cam_y << ", " << ref_cam_z << "]" << std::endl;
    std::cout << "   - Yaw(rad): " << ref_cam_yaw_rad << std::endl;


    // ========================================================
    // (3) 로봇 베이스 기준 오차 계산 (Axis Flip 적용)
    // ========================================================
    double diff_cam_x = cur_cam_x - ref_cam_x;
    double diff_cam_y = cur_cam_y - ref_cam_y;
    double diff_cam_yaw = cur_cam_yaw_rad - ref_cam_yaw_rad;

    double error_robot_x = diff_cam_x;      
    double error_robot_y = -diff_cam_y;     
    double error_robot_yaw = -diff_cam_yaw; 

    double corr_x = -error_robot_x;
    double corr_y = -error_robot_y;
    double corr_yaw = -error_robot_yaw;

    std::cout << ">>> 3. Calculated Correction (Robot Frame)" << std::endl;
    std::cout << "    d_X: " << corr_x * 1000.0 << " mm" << std::endl;
    std::cout << "    d_Y: " << corr_y * 1000.0 << " mm" << std::endl;
    std::cout << "    d_Yaw: " << corr_yaw * 180.0 / M_PI << " deg" << std::endl;
    std::cout << std::string(60, '-') << std::endl;

    double c = cos(corr_yaw);
    double s = sin(corr_yaw);


    // ========================================================
    // (4) CSV 궤적 로드, 보정, 저장 및 이동
    // ========================================================
    std::ifstream file("/home/nrel/ARPA-H/rbmove_jh/kjh/ref_data/test.csv");
    if (!file.is_open()) { std::cerr << "CSV file error" << std::endl; return 1; }

    // [추가] 저장할 파일 열기
    std::ofstream out_file("/home/nrel/ARPA-H/rbmove_jh/kjh/ref_data/corrected_trajectory_y_m5.csv");
    if (!out_file.is_open()) { std::cerr << "Output file creation failed!" << std::endl; return 1; }
    
    // [추가] CSV 헤더 작성 (입력 파일 형식에 맞춤)
    out_file << "time,x,y,z,rx,ry,rz" << std::endl;

    std::string line;
    bool first_line = true;
    
    std::cout << ">>> 4. Trajectory Execution & Saving..." << std::endl;
    std::cout << "   [Time] | [Original X, Y]      -> [Corrected X, Y]" << std::endl;

    while (std::getline(file, line)) {
      if (first_line) { first_line = false; continue; }

      std::stringstream ss_csv(line);
      std::string token;
      std::array<double, 6> saved_pose{}; // mm, deg
      
      std::getline(ss_csv, token, ','); // Time
      double time_ms = std::stod(token);

      int idx = 0;
      while (std::getline(ss_csv, token, ',') && idx < 6) {
        saved_pose[idx++] = std::stod(token);
      }

      if (idx == 6) {
        // [수정된 보정 로직: 평행 이동 우선]
        double org_x = saved_pose[0]; // mm
        double org_y = saved_pose[1]; // mm

        // ---------------------------------------------------------
        // [삭제됨] 원점 기준 회전 행렬 (오차의 주범)
        // double rot_x = org_x * c - org_y * s; 
        // double rot_y = org_x * s + org_y * c;
        // ---------------------------------------------------------

        // [변경됨] 단순 평행 이동 (Translation Only)
        // 원래 좌표에 보정량(corr_x, corr_y)만 그대로 더합니다.
        double final_x = org_x + (corr_x * 1000.0);
        double final_y = org_y + (corr_y * 1000.0);
        
        // [유지] 로봇의 헤딩(Yaw) 각도는 회전 보정을 적용해야 함
        // 위치는 그대로 옮기더라도, 로봇이 바라보는 방향은 틀어줘야 하기 때문
        double final_yaw = saved_pose[5] + (corr_yaw * 180.0 / M_PI);
        final_yaw = normalizeAngle(final_yaw);

        // [결과 생성]
        std::array<double, 6> cmd_pose = saved_pose;
        cmd_pose[0] = final_x;
        cmd_pose[1] = final_y;
        cmd_pose[5] = final_yaw;

        // [파일 저장 및 출력]
        out_file << time_ms << ","
                 << cmd_pose[0] << ","
                 << cmd_pose[1] << ","
                 << cmd_pose[2] << ","
                 << cmd_pose[3] << ","
                 << cmd_pose[4] << ","
                 << cmd_pose[5] << std::endl;

        std::cout << "   [" << std::setw(4) << (int)time_ms << "] | "
                  << "[" << std::setw(7) << saved_pose[0] << ", " << std::setw(7) << saved_pose[1] << "] -> "
                  << "[" << std::setw(7) << cmd_pose[0] << ", " << std::setw(7) << cmd_pose[1] << "]" 
                  << std::endl;

        // 로봇 이동 명령
        robot.move_servo_l(rc, cmd_pose, 0.05, 0.05, 1, 0.05);
        std::this_thread::sleep_for(std::chrono::milliseconds(30));
        rc.error().throw_if_not_empty();
      }
    }
    
    // 파일 닫기
    out_file.close();
    file.close();

    std::cout << std::string(60, '=') << std::endl;
    std::cout << ">>> Corrected trajectory saved to 'corrected_trajectory.csv'" << std::endl;

  } catch (const std::exception& e) {
    std::cerr << e.what() << std::endl;
    return 1;
  }
  return 0;
}