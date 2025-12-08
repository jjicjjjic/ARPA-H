#include <iostream>
#include <fstream>
#include <array>
#include <thread>
#include <chrono>
#include <atomic>
#include <future>
#include "rbpodo/rbpodo.hpp"

using namespace rb;

bool check_quit() {
  std::string input;
  std::getline(std::cin, input);
  return (input == "q" || input == "Q");
}

int main() {
  try {
    podo::Cobot robot("10.0.2.7");
    podo::ResponseCollector rc;

    // std::ofstream file("/home/nrel/ARPA-H/rbmove_jh/kjh/data/tcp_pose_log.csv");
    //meal
    // std::ofstream file("/home/nrel/ARPA-H/rbmove_jh/kjh/data/meal/d_w.csv");
    // std::ofstream file("/home/nrel/ARPA-H/rbmove_jh/kjh/data/meal/w_s.csv");
    // std::ofstream file("/home/nrel/ARPA-H/rbmove_jh/kjh/data/meal/s_o.csv");
    // std::ofstream file("/home/nrel/ARPA-H/rbmove_jh/kjh/data/meal/s_f.csv");
    // std::ofstream file("/home/nrel/ARPA-H/rbmove_jh/kjh/data/meal/f.csv");
    // std::ofstream file("/home/nrel/ARPA-H/rbmove_jh/kjh/data/meal/f_m.csv");
    // std::ofstream file("/home/nrel/ARPA-H/rbmove_jh/kjh/data/meal/fix_f2.csv");
    // std::ofstream file("/home/nrel/ARPA-H/rbmove_jh/kjh/data/meal/f2.csv");
    // std::ofstream file("/home/nrel/ARPA-H/rbmove_jh/kjh/data/meal/f2_m.csv");
    // std::ofstream file("/home/nrel/ARPA-H/rbmove_jh/kjh/data/meal/fix_f3.csv");
    // std::ofstream file("/home/nrel/ARPA-H/rbmove_jh/kjh/data/meal/f3.csv");
    // std::ofstream file("/home/nrel/ARPA-H/rbmove_jh/kjh/data/meal/f3_m.csv");
    // std::ofstream file("/home/nrel/ARPA-H/rbmove_jh/kjh/data/meal/fix_f4.csv");
    // std::ofstream file("/home/nrel/ARPA-H/rbmove_jh/kjh/data/meal/f4.csv");
    // std::ofstream file("/home/nrel/ARPA-H/rbmove_jh/kjh/data/meal/f4_m.csv");
    // std::ofstream file("/home/nrel/ARPA-H/rbmove_jh/kjh/data/meal/fix_f5.csv");
    // std::ofstream file("/home/nrel/ARPA-H/rbmove_jh/kjh/data/meal/f5.csv");
    // std::ofstream file("/home/nrel/ARPA-H/rbmove_jh/kjh/data/meal/f5_m.csv");
    // std::ofstream file("/home/nrel/ARPA-H/rbmove_jh/kjh/data/meal/fix_f6.csv");
    // std::ofstream file("/home/nrel/ARPA-H/rbmove_jh/kjh/data/meal/f6.csv");
    // std::ofstream file("/home/nrel/ARPA-H/rbmove_jh/kjh/data/meal/f6_m.csv");
    // std::ofstream file("/home/nrel/ARPA-H/rbmove_jh/kjh/data/meal/fix_s.csv");
    // std::ofstream file("/home/nrel/ARPA-H/rbmove_jh/kjh/data/meal/s_d.csv");
    // // meal onetake
    // std::ofstream file("/home/nrel/ARPA-H/rbmove_jh/kjh/data/meal_onetake/d_s.csv");
    // std::ofstream file("/home/nrel/ARPA-H/rbmove_jh/kjh/data/meal_onetake/s_f1_side.csv");
    // std::ofstream file("/home/nrel/ARPA-H/rbmove_jh/kjh/data/meal_onetake/f1_mf.csv");
    std::ofstream file("/home/nrel/ARPA-H/rbmove_jh/kjh/data/meal_onetake/fix_f2.csv");
    // std::ofstream file("/home/nrel/ARPA-H/rbmove_jh/kjh/data/meal_onetake/fix_f3.csv");
    // std::ofstream file("/home/nrel/ARPA-H/rbmove_jh/kjh/data/meal_onetake/fix_f1.csv");
    // std::ofstream file("/home/nrel/ARPA-H/rbmove_jh/kjh/data/meal_onetake/fix_s.csv");
    // std::ofstream file("/home/nrel/ARPA-H/rbmove_jh/kjh/data/meal_onetake/fix_s.csv");
    // //comoral
    // std::ofstream file("/home/nrel/ARPA-H/rbmove_jh/kjh/data/comoral/d_c.csv");
    // std::ofstream file("/home/nrel/ARPA-H/rbmove_jh/kjh/data/comoral/c_m.csv");
    // std::ofstream file("/home/nrel/ARPA-H/rbmove_jh/kjh/data/comoral/f_c.csv");
    // std::ofstream file("/home/nrel/ARPA-H/rbmove_jh/kjh/data/comoral/c_d.csv");
    // //position change
    // std::ofstream file("/home/nrel/ARPA-H/rbmove_jh/kjh/data/position/default_cushion.csv");
    // std::ofstream file("/home/nrel/ARPA-H/rbmove_jh/kjh/data/position/cushion_back.csv");
    // std::ofstream file("/home/nrel/ARPA-H/rbmove_jh/kjh/data/position/back_cushion2.csv");
    // std::ofstream file("/home/nrel/ARPA-H/rbmove_jh/kjh/data/position/cushion2_back.csv");
    // std::ofstream file("/home/nrel/ARPA-H/rbmove_jh/kjh/data/position/back_default.csv");
    // //falling_detection
    // std::ofstream file("/home/nrel/ARPA-H/rbmove_jh/kjh/data/fall/fp1.csv");
    // std::ofstream file("/home/nrel/ARPA-H/rbmove_jh/kjh/data/fall/fp1_d.csv");
    // std::ofstream file("/home/nrel/ARPA-H/rbmove_jh/kjh/data/fall/fp2.csv");
    // std::ofstream file("/home/nrel/ARPA-H/rbmove_jh/kjh/data/fall/fp2_d.csv");
    // std::ofstream file("/home/nrel/ARPA-H/rbmove_jh/kjh/data/fall/fp3.csv");
    // std::ofstream file("/home/nrel/ARPA-H/rbmove_jh/kjh/data/fall/fp3_d.csv");


    if (!file.is_open()) {
      std::cerr << "파일을 열 수 없습니다." << std::endl;
      return 1;
    }

    file << "Time(ms),X(mm),Y(mm),Z(mm),Roll(deg),Pitch(deg),Yaw(deg)\n";

    std::cout << "TCP 자세 기록을 시작합니다. 종료하려면 'q'를 입력 후 Enter를 누르세요.\n";

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

      std::this_thread::sleep_for(std::chrono::milliseconds(10));  // 10Hz 기록
    }

    file.close();
    std::cout << "'q' 입력 감지됨. TCP 자세값 기록을 종료합니다.\n";

  } catch (const std::exception& e) {
    std::cerr << e.what() << std::endl;
    return 1;
  }

  return 0;
}