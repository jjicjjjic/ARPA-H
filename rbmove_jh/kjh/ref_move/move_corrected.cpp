#include <iostream>
#include <fstream>
#include <sstream>
#include <array>
#include <thread>
#include <chrono>
#include <vector>
#include <cmath>
#include <iomanip> // std::setprecision 사용을 위해 추가
#include <cstring>
#include <sys/socket.h>
#include <netinet/in.h>
#include <unistd.h>
#include "rbpodo/rbpodo.hpp"

#define UDP_PORT 12345
#define BUFFER_SIZE 1024

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

// --- [수학 라이브러리: 행렬 연산] ---
struct Matrix4d {
    double m[16];

    static Matrix4d identity() {
        Matrix4d res = {0};
        res.m[0] = 1; res.m[5] = 1; res.m[10] = 1; res.m[15] = 1;
        return res;
    }

    Matrix4d operator*(const Matrix4d& other) const {
        Matrix4d res = {0};
        for(int i=0; i<4; i++) {
            for(int j=0; j<4; j++) {
                for(int k=0; k<4; k++) {
                    res.m[i*4+j] += m[i*4+k] * other.m[k*4+j];
                }
            }
        }
        return res;
    }

    Matrix4d inverse() const {
        Matrix4d res = identity();
        // Rotation Transpose
        res.m[0] = m[0]; res.m[1] = m[4]; res.m[2] = m[8];
        res.m[4] = m[1]; res.m[5] = m[5]; res.m[6] = m[9];
        res.m[8] = m[2]; res.m[9] = m[6]; res.m[10] = m[10];
        // Translation: -R^T * t
        double tx = m[3], ty = m[7], tz = m[11];
        res.m[3]  = -(res.m[0]*tx + res.m[1]*ty + res.m[2]*tz);
        res.m[7]  = -(res.m[4]*tx + res.m[5]*ty + res.m[6]*tz);
        res.m[11] = -(res.m[8]*tx + res.m[9]*ty + res.m[10]*tz);
        return res;
    }
    
    // 행렬 출력 헬퍼 함수
    void print(const std::string& name) const {
        std::cout << "   [" << name << "]" << std::endl;
        std::cout << std::fixed << std::setprecision(4);
        for(int i=0; i<4; i++) {
            std::cout << "   | ";
            for(int j=0; j<4; j++) {
                std::cout << std::setw(9) << m[i*4+j] << " ";
            }
            std::cout << "|" << std::endl;
        }
        std::cout << std::endl;
    }
};

Matrix4d rodriguesToMatrix(double rx, double ry, double rz, double tx, double ty, double tz) {
    Matrix4d mat = Matrix4d::identity();
    double theta = sqrt(rx*rx + ry*ry + rz*rz);
    if (theta < 1e-6) {
        mat.m[3]=tx; mat.m[7]=ty; mat.m[11]=tz;
        return mat;
    }
    double kx = rx/theta, ky = ry/theta, kz = rz/theta;
    double c = cos(theta), s = sin(theta), v = 1-c;
    
    mat.m[0] = kx*kx*v + c;    mat.m[1] = kx*ky*v - kz*s; mat.m[2] = kx*kz*v + ky*s;
    mat.m[4] = kx*ky*v + kz*s; mat.m[5] = ky*ky*v + c;    mat.m[6] = ky*kz*v - kx*s;
    mat.m[8] = kx*kz*v - ky*s; mat.m[9] = ky*kz*v + kx*s; mat.m[10]= kz*kz*v + c;
    
    mat.m[3] = tx; mat.m[7] = ty; mat.m[11] = tz;
    return mat;
}

Matrix4d eulerToMatrix(double x, double y, double z, double r, double p, double yw) {
    double rad_r = r * M_PI / 180.0;
    double rad_p = p * M_PI / 180.0;
    double rad_y = yw * M_PI / 180.0;
    double cr = cos(rad_r), sr = sin(rad_r);
    double cp = cos(rad_p), sp = sin(rad_p);
    double cy = cos(rad_y), sy = sin(rad_y);

    Matrix4d mat = Matrix4d::identity();
    mat.m[0] = cy*cp;   mat.m[1] = cy*sp*sr - sy*cr; mat.m[2] = cy*sp*cr + sy*sr;
    mat.m[4] = sy*cp;   mat.m[5] = sy*sp*sr + cy*cr; mat.m[6] = sy*sp*cr - cy*sr;
    mat.m[8] = -sp;     mat.m[9] = cp*sr;            mat.m[10]= cp*cr;
    mat.m[3] = x; mat.m[7] = y; mat.m[11] = z;
    return mat;
}

std::array<double, 6> matrixToPose(const Matrix4d& m) {
    double x = m.m[3];
    double y = m.m[7];
    double z = m.m[11];
    double r, p, yw;
    if (abs(m.m[8]) < 0.99999) {
        p = atan2(-m.m[8], sqrt(m.m[0]*m.m[0] + m.m[4]*m.m[4]));
        r = atan2(m.m[9], m.m[10]);
        yw = atan2(m.m[4], m.m[0]);
    } else {
        p = atan2(-m.m[8], sqrt(m.m[0]*m.m[0] + m.m[4]*m.m[4]));
        r = atan2(-m.m[6], m.m[5]);
        yw = 0;
    }
    return {x, y, z, r * 180.0 / M_PI, p * 180.0 / M_PI, yw * 180.0 / M_PI};
}
// ------------------------------------------

using namespace rb;

int main() {
  try {
    podo::Cobot robot("10.0.2.7");
    podo::ResponseCollector rc;
    // robot.set_operation_mode(rc, podo::OperationMode::Real); 
    robot.set_operation_mode(rc, podo::OperationMode::Simulation); // 테스트용 시뮬레이션 모드
    rc.error().throw_if_not_empty();
    robot.set_speed_bar(rc, 1.0);
    robot.flush(rc);

    std::cout << std::string(60, '=') << std::endl;
    std::cout << ">>> Trajectory Correction System Started" << std::endl;
    std::cout << std::string(60, '=') << std::endl;

    // ========================================================
    // (1) UDP로 현재(Current) ArUco 좌표 수신
    // ========================================================
    int sockfd;
    char buffer[BUFFER_SIZE];
    struct sockaddr_in servaddr, cliaddr;

    if ((sockfd = socket(AF_INET, SOCK_DGRAM, 0)) < 0) { perror("socket creation failed"); return 1; }
    memset(&servaddr, 0, sizeof(servaddr));
    servaddr.sin_family = AF_INET;
    servaddr.sin_addr.s_addr = INADDR_ANY;
    servaddr.sin_port = htons(UDP_PORT);
    if (bind(sockfd, (const struct sockaddr *)&servaddr, sizeof(servaddr)) < 0) { perror("bind failed"); return 1; }

    std::cout << ">>> Waiting for CURRENT ArUco Pose via UDP..." << std::endl;
    socklen_t len = sizeof(cliaddr);
    int n = recvfrom(sockfd, (char *)buffer, BUFFER_SIZE, MSG_WAITALL, (struct sockaddr *)&cliaddr, &len);
    buffer[n] = '\0';
    close(sockfd);

    std::string data(buffer);
    std::stringstream ss(data);
    std::string item;
    std::vector<double> cur_marker_data;
    while (std::getline(ss, item, ',')) { cur_marker_data.push_back(std::stod(item)); }

    // T_curr (천장 -> 현재 로봇)
    Matrix4d T_curr = rodriguesToMatrix(
        cur_marker_data[4], cur_marker_data[5], cur_marker_data[6], // rvec
        cur_marker_data[1], cur_marker_data[2], cur_marker_data[3]  // tvec (m)
    );

    // [출력] 현재 ArUco 좌표
    std::cout << std::fixed << std::setprecision(4);
    std::cout << ">>> 1. Current ArUco Pose (Received)" << std::endl;
    std::cout << "   - ID: " << cur_marker_data[0] << std::endl;
    std::cout << "   - Pos(m): [" << cur_marker_data[1] << ", " << cur_marker_data[2] << ", " << cur_marker_data[3] << "]" << std::endl;
    std::cout << "   - Rot(rad): [" << cur_marker_data[4] << ", " << cur_marker_data[5] << ", " << cur_marker_data[6] << "]" << std::endl;
    std::cout << std::endl;


    // ========================================================
    // (2) 파일에서 기준(Reference) ArUco 좌표 로드
    // ========================================================
    std::ifstream ref_file("/home/nrel/ARPA-H/rbmove_jh/kjh/ref_data/ref_pose.txt");
    if (!ref_file.is_open()) { std::cerr << "Reference file not found!" << std::endl; return 1; }
    
    std::vector<double> ref_vals;
    double val;
    while (ref_file >> val) ref_vals.push_back(val);
    
    // T_ref (천장 -> 티칭 때 로봇)
    Matrix4d T_ref = rodriguesToMatrix(
        ref_vals[3], ref_vals[4], ref_vals[5], // rvec
        ref_vals[0], ref_vals[1], ref_vals[2]  // tvec (m)
    );

    // [출력] 기준 ArUco 좌표
    std::cout << ">>> 2. Reference ArUco Pose (Loaded)" << std::endl;
    std::cout << "   - Pos(m): [" << ref_vals[0] << ", " << ref_vals[1] << ", " << ref_vals[2] << "]" << std::endl;
    std::cout << "   - Rot(rad): [" << ref_vals[3] << ", " << ref_vals[4] << ", " << ref_vals[5] << "]" << std::endl;
    std::cout << std::endl;


    // ========================================================
    // (3) 보정 행렬(Correction Matrix) 계산
    // ========================================================
    Matrix4d T_curr_inv = T_curr.inverse();
    Matrix4d T_diff = T_curr_inv * T_ref; 

    // [출력] 보정 행렬
    std::cout << ">>> 3. Correction Matrix (T_diff)" << std::endl;
    T_diff.print("T_diff");
    
    // 오차량 간략 표시
    std::array<double, 6> diff_pose = matrixToPose(T_diff);
    std::cout << "   => Estimated Error (Correction Amount):" << std::endl;
    std::cout << "      d_X: " << diff_pose[0]*1000 << " mm, d_Y: " << diff_pose[1]*1000 << " mm" << std::endl; 
    std::cout << "      d_Yaw: " << diff_pose[5] << " deg" << std::endl;
    std::cout << std::string(60, '-') << std::endl;


    // ========================================================
    // (4) CSV 궤적 로드 및 보정 후 이동
    // ========================================================
    std::ifstream file("/home/nrel/ARPA-H/rbmove_jh/kjh/ref_data/test.csv");
    if (!file.is_open()) { std::cerr << "CSV file error" << std::endl; return 1; }

    std::string line;
    bool first_line = true;
    
    std::cout << ">>> 4. Trajectory Execution (Real-time Correction)" << std::endl;
    std::cout << "   [Time] | [Original X, Y, Z]       -> [Corrected X, Y, Z]" << std::endl;

    while (std::getline(file, line)) {
      if (first_line) { first_line = false; continue; }

      std::stringstream ss_csv(line);
      std::string token;
      std::array<double, 6> saved_pose{}; // mm, deg
      
      std::getline(ss_csv, token, ','); // Time string
      double time_ms = std::stod(token);

      int idx = 0;
      while (std::getline(ss_csv, token, ',') && idx < 6) {
        saved_pose[idx++] = std::stod(token);
      }

      if (idx == 6) {
        // 1. CSV 포즈 -> Matrix
        Matrix4d T_traj = eulerToMatrix(
            saved_pose[0]/1000.0, saved_pose[1]/1000.0, saved_pose[2]/1000.0,
            saved_pose[3], saved_pose[4], saved_pose[5]
        );

        // 2. 보정 적용
        Matrix4d T_target = T_diff * T_traj;

        // 3. 다시 Robot Command 포맷
        std::array<double, 6> cmd_pose = matrixToPose(T_target);
        cmd_pose[0] *= 1000.0;
        cmd_pose[1] *= 1000.0;
        cmd_pose[2] *= 1000.0;

        // [출력] 실시간 비교 (너무 빠르면 스크롤되니 100ms마다 한 번씩만 출력하거나, 다 출력하거나)
        // 여기서는 매 포인트 출력
        std::cout << "   [" << std::setw(4) << (int)time_ms << "] | "
                  << "[" << std::setw(7) << saved_pose[0] << ", " << std::setw(7) << saved_pose[1] << ", " << std::setw(7) << saved_pose[2] << "] -> "
                  << "[" << std::setw(7) << cmd_pose[0] << ", " << std::setw(7) << cmd_pose[1] << ", " << std::setw(7) << cmd_pose[2] << "]" 
                  << std::endl;

        // 4. 이동 명령
        robot.move_servo_l(rc, cmd_pose, 0.1, 0.05, 1, 0.05);
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
        rc.error().throw_if_not_empty();
      }
    }
    std::cout << std::string(60, '=') << std::endl;
    std::cout << ">>> Corrected Motion Complete!" << std::endl;

  } catch (const std::exception& e) {
    std::cerr << e.what() << std::endl;
    return 1;
  }
  return 0;
}