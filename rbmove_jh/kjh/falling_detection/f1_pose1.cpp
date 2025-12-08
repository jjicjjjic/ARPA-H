#include <iostream>
#include <fstream>
#include <sstream>
#include <array>
#include <thread>
#include <chrono>
#include "rbpodo/rbpodo.hpp"

using namespace rb;

int main() {
  try {
    // (1) 로봇 연결
    podo::Cobot robot("10.0.2.7");
    podo::ResponseCollector rc;

    // (2) 시뮬레이션 모드 (실기일 경우 Real로 변경)
    // robot.set_operation_mode(rc, podo::OperationMode::Simulation);
    robot.set_operation_mode(rc, podo::OperationMode::Real);
    rc.error().throw_if_not_empty();

    // (3) 속도 설정
    robot.set_speed_bar(rc, 0.6);
    robot.flush(rc);

    std::array<double, 6> jnt = {-62, 14, 95, 68, 6, 40};  // 요기에 default pose 정해지면 입력하기!
    robot.move_j(rc, jnt, 60, 80);
    rc.error().throw_if_not_empty();

    std::this_thread::sleep_for(std::chrono::seconds(20));

    std::array<double, 6> jnt2 = {-12.5, 14, 95, 68, -12, 40};  // 요기에 default pose 정해지면 입력하기!
    robot.move_j(rc, jnt2, 60, 80);
    rc.error().throw_if_not_empty();

    

   

  } catch (const std::exception& e) {
    std::cerr << e.what() << std::endl;
    return 1;
  }

  return 0;
}