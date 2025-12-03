import pyrealsense2 as rs
import numpy as np
import cv2
import mediapipe as mp


pipeline = rs.pipeline()
config = rs.config()

config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

profile = pipeline.start(config)
align_to = rs.stream.color
align = rs.align(align_to)

mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

print("카메라 시작... (ESC를 눌러 종료)")

try:
    while True:
        frames = pipeline.wait_for_frames()

        aligned_frames = align.process(frames)
        
        aligned_depth_frame = aligned_frames.get_depth_frame()
        color_frame = aligned_frames.get_color_frame()

        if not aligned_depth_frame or not color_frame:
            continue

        depth_image = np.asanyarray(aligned_depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())

        color_image.flags.writeable = False
        rgb_image = cv2.cvtColor(color_image, cv2.COLOR_BGR2RGB)

        results = face_mesh.process(rgb_image)
        color_image.flags.writeable = True
        
        h, w, _ = color_image.shape

        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                pt1 = face_landmarks.landmark[13] # 윗입술 중앙
                pt2 = face_landmarks.landmark[14] # 아랫입술 중앙

                cx1, cy1 = int(pt1.x * w), int(pt1.y * h)
                cx2, cy2 = int(pt2.x * w), int(pt2.y * h)

                center_x = (cx1 + cx2) // 2
                center_y = (cy1 + cy2) // 2

                if 0 <= center_x < w and 0 <= center_y < h:
                    dist = aligned_depth_frame.get_distance(center_x, center_y)
                
                    cv2.circle(color_image, (center_x, center_y), 5, (0, 255, 0), -1)
                    text = f"Mouth: ({center_x}, {center_y}) | Dist: {dist:.3f}m"
                    cv2.putText(color_image, text, (center_x + 10, center_y), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)                 
                    print(f"X: {center_x}, Y: {center_y}, Z: {dist:.4f} m")

        cv2.imshow('RealSense Mouth Depth', color_image)

        if cv2.waitKey(1) & 0xFF == 27:
            break

finally:
    pipeline.stop()
    cv2.destroyAllWindows()