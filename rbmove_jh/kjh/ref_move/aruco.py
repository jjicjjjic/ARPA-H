import pyrealsense2 as rs
import numpy as np
import cv2
import socket
import time

# ==========================================
# [설정] 환경에 맞게 수정하세요
# ==========================================
UDP_IP = "127.0.0.1"   # C++ 프로그램이 같은 PC에 있다면 "127.0.0.1"
                       # 다른 PC라면 해당 PC의 IP 주소 (예: "192.168.0.10")
UDP_PORT = 12345       # C++ 코드와 동일한 포트 번호

# 마커 실제 크기 (단위: Meter) -> *매우 중요*
# 자로 마커의 검은색 테두리 한 변의 길이를 정확히 재서 넣어야 거리가 맞습니다.
MARKER_SIZE = 0.05     # 예: 5cm -> 0.05

# 사용할 마커 딕셔너리 (사용 중인 마커 종류에 맞춰 변경)
# 보통 DICT_4X4_50, DICT_5X5_100, DICT_6X6_250 등을 많이 씁니다.
ARUCO_DICT_TYPE = cv2.aruco.DICT_5X5_100
# ==========================================

def main():
    # 1. UDP 소켓 생성
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print(f">>> UDP Target: {UDP_IP}:{UDP_PORT}")

    # 2. RealSense 파이프라인 설정
    pipeline = rs.pipeline()
    config = rs.config()
    
    # RGB 스트림 활성화 (640x480, 30fps)
    config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

    # 파이프라인 시작
    print(">>> Starting RealSense Pipeline...")
    profile = pipeline.start(config)

    # 3. 카메라 내부 파라미터(Intrinsics) 가져오기
    # RealSense는 캘리브레이션 데이터가 내장되어 있어 바로 가져오면 됩니다.
    color_stream = profile.get_stream(rs.stream.color)
    intrinsics = color_stream.as_video_stream_profile().get_intrinsics()

    # OpenCV용 카메라 매트릭스 구성
    camera_matrix = np.array([
        [intrinsics.fx, 0, intrinsics.ppx],
        [0, intrinsics.fy, intrinsics.ppy],
        [0, 0, 1]
    ], dtype=np.float32)
    
    dist_coeffs = np.array(intrinsics.coeffs) # 왜곡 계수

    # 4. ArUco 탐지기 설정
    aruco_dict = cv2.aruco.getPredefinedDictionary(ARUCO_DICT_TYPE)
    parameters = cv2.aruco.DetectorParameters()

    try:
        while True:
            # 프레임 받기
            frames = pipeline.wait_for_frames()
            color_frame = frames.get_color_frame()
            if not color_frame:
                continue

            # numpy 배열로 변환
            frame = np.asanyarray(color_frame.get_data())

            # 마커 탐지
            # corners: 마커 코너 좌표, ids: 마커 ID
            corners, ids, rejected = cv2.aruco.detectMarkers(frame, aruco_dict, parameters=parameters)

            if ids is not None:
                # 6D Pose 추정 (rvec: 회전 벡터, tvec: 이동 벡터)
                # tvec 단위는 MARKER_SIZE와 동일하게 Meter로 나옵니다.
                rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(corners, MARKER_SIZE, camera_matrix, dist_coeffs)

                # 탐지된 모든 마커에 대해 전송 (여기선 첫 번째 마커만 전송하거나 특정 ID만 전송 가능)
                for i in range(len(ids)):
                    # 시각화 (축 그리기)
                    cv2.drawFrameAxes(frame, camera_matrix, dist_coeffs, rvecs[i], tvecs[i], 0.03)
                    cv2.aruco.drawDetectedMarkers(frame, corners)

                    # 데이터 추출
                    marker_id = int(ids[i][0])
                    
                    # tvec = [x, y, z] (Meter)
                    tx, ty, tz = tvecs[i][0]
                    
                    # rvec = [rx, ry, rz] (Rodrigues Vector, Radian)
                    rx, ry, rz = rvecs[i][0]

                    # UDP 패킷 포맷: "id,x,y,z,rx,ry,rz"
                    # 소수점 5자리까지 전송
                    message = f"{marker_id},{tx:.5f},{ty:.5f},{tz:.5f},{rx:.5f},{ry:.5f},{rz:.5f}"
                    
                    # 전송!
                    sock.sendto(message.encode(), (UDP_IP, UDP_PORT))
                    
                    # 터미널 출력 (디버깅용)
                    print(f"Sent: ID={marker_id} | Pos=[{tx:.3f} {ty:.3f} {tz:.3f}]")

            # 화면 출력
            cv2.imshow('RealSense ArUco Sender', frame)

            # 'q' 키 누르면 종료
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    finally:
        pipeline.stop()
        cv2.destroyAllWindows()
        print(">>> Pipeline Stopped.")

if __name__ == "__main__":
    main()