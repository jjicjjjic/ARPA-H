#include <iostream>
#include <fstream>
#include <sstream>
#include <array>
#include <thread>
#include <chrono>
#include <vector>
#include <cmath>
#include "rbpodo/rbpodo.hpp"

using namespace rb;

// [설정] 원하는 이동 속도 (mm/s)
const double DESIRED_VELOCITY = 200.0; 
// [설정] 제어 주기 (s) - 100Hz = 0.01s
const double DT = 0.01;

// 3D 거리 계산 함수
double get_distance(const std::array<double, 6>& p1, const std::array<double, 6>& p2) {
    return std::sqrt(std::pow(p2[0] - p1[0], 2) + 
                     std::pow(p2[1] - p1[1], 2) + 
                     std::pow(p2[2] - p1[2], 2));
}

int main() {
  try {
    // ---------------------------------------------------------
    // 1. CSV 파일 데이터 메모리로 로드 (실시간 루프 밖에서 수행)
    // ---------------------------------------------------------
    std::vector<std::array<double, 6>> path_data;
    std::ifstream file("/home/nrel/ARPA-H/rbmove_jh/kjh/data/tcp_pose_log.csv");
    
    if (!file.is_open()) {
      std::cerr << "CSV 파일을 열 수 없습니다!" << std::endl;
      return 1;
    }

    std::string line;
    bool first_line = true;
    while (std::getline(file, line)) {
      if (first_line) { first_line = false; continue; } // 헤더 스킵
      
      std::stringstream ss(line);
      std::string token;
      std::array<double, 6> tcp_pose{};
      int idx = 0;
      
      // 첫 번째 컬럼(인덱스 등) 스킵하고 좌표만 파싱한다고 가정 (CSV 구조에 맞춰 수정 필요)
      std::getline(ss, token, ','); 
      
      while (std::getline(ss, token, ',') && idx < 6) {
        tcp_pose[idx++] = std::stod(token);
      }
      if (idx == 6) path_data.push_back(tcp_pose);
    }
    file.close();
    std::cout << "데이터 로드 완료: 총 " << path_data.size() << "개 포인트" << std::endl;

    if (path_data.empty()) return 1;

    // ---------------------------------------------------------
    // 2. 로봇 연결 및 설정
    // ---------------------------------------------------------
    podo::Cobot robot("10.0.2.7");
    podo::ResponseCollector rc;
    robot.set_operation_mode(rc, podo::OperationMode::Real); // Real Mode
    std::this_thread::sleep_for(std::chrono::milliseconds(500)); // 모드 변경 대기

    // ---------------------------------------------------------
    // 3. 등속 이동 루프 (Interpolation Logic)
    // ---------------------------------------------------------
    
    // 현재 가상의 로봇 위치를 첫 번째 데이터로 초기화
    std::array<double, 6> current_cmd_pose = path_data[0];
    int next_target_idx = 1;

    // 한 틱당 이동해야 할 거리 (mm) = 속도(mm/s) * 시간(s)
    double step_distance = DESIRED_VELOCITY * DT; 

    std::cout << "이동 시작! 목표 속도: " << DESIRED_VELOCITY << " mm/s" << std::endl;

    while (next_target_idx < path_data.size()) {
        auto start_time = std::chrono::steady_clock::now();

        // (1) 현재 명령 위치에서 다음 타겟 점까지의 거리 계산
        std::array<double, 6> target_pose = path_data[next_target_idx];
        double dist_to_target = get_distance(current_cmd_pose, target_pose);

        // (2) 거리가 너무 가까우면(이미 도달했으면) 다음 타겟으로 인덱스 변경
        if (dist_to_target < step_distance) {
            next_target_idx++;
            continue; // 루프 다시 돌면서 다음 점 확인
        }

        // (3) 선형 보간 (Linear Interpolation) - 방향 벡터 구하기
        double ratio = step_distance / dist_to_target;
        
        // XYZ는 비율대로 이동
        for(int i=0; i<3; ++i) {
            current_cmd_pose[i] += (target_pose[i] - current_cmd_pose[i]) * ratio;
        }
        
        // RX, RY, RZ도 비율대로 이동 (간단한 선형 보간)
        for(int i=3; i<6; ++i) {
            current_cmd_pose[i] += (target_pose[i] - current_cmd_pose[i]) * ratio;
        }

        // (4) 로봇에게 명령 전송 (파라미터 튜닝됨)
        // t1=0.02 (부드러운 연결), Gain=200 (반응성 향상), Alpha=0.9 (필터링 최소화)
        robot.move_servo_l(rc, current_cmd_pose, 0.02, 0.02, 200, 0.9);
        rc.error().throw_if_not_empty();

        // (5) 100Hz 주기 맞추기
        std::this_thread::sleep_until(start_time + std::chrono::milliseconds(10));
    }

    std::cout << "동작 완료!" << std::endl;

  } catch (const std::exception& e) {
    std::cerr << "Error: " << e.what() << std::endl;
    return 1;
  }
  return 0;
}