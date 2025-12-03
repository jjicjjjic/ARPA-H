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
    podo::Cobot robot("10.0.2.7");
    podo::ResponseCollector rc;

    // robot.set_operation_mode(rc, podo::OperationMode::Simulation);
    robot.set_operation_mode(rc, podo::OperationMode::Real);
    rc.error().throw_if_not_empty();

    robot.set_speed_bar(rc, 0.7);
    robot.flush(rc);

    std::array<double, 6> tcp_pose = {321, -390, 770, -13, -23, 20};  // 요기에 Fix pose 정해지면 입력하기!
    robot.move_l(rc, tcp_pose, 100, 100);
    rc.error().throw_if_not_empty();

    std::cout << "default 자세 완료" << std::endl;

  } catch (const std::exception& e) {
    std::cerr << e.what() << std::endl;
    return 1;
  }

  return 0;
}