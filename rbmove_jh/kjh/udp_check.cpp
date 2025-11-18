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

const double MIN_VALID_DEPTH = 0.07; // 7cm
const double MAX_VALID_DEPTH = 0.50; // 50cm

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

        std::cout << "Pos[X,Y,Z]: [" << t_cam_to_marker[0] << ", " << t_cam_to_marker[1] << ", " << t_cam_to_marker[2] << "]" << std::endl;
        std::cout << "Ori[R,P,Y]: [" <<rvec_cam_to_marker[0] << ", " << rvec_cam_to_marker[1] << ", " <<rvec_cam_to_marker[2] << "]" << std::endl;
   

    }
    

    close(sockfd);
    return 0;
}