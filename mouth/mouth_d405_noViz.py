## License: Apache 2.0. See LICENSE file in root directory.
## Copyright(c) 2015-2017 Intel Corporation. All Rights Reserved.

###############################################
##      Open CV and Numpy integration        ##
###############################################
#py3_10/window
#py310/linux
import os
import time    
import socket
import numpy as np
import cv2
import pyrealsense2 as rs
from rtmlib import Wholebody

# Configure depth and color streams
pipeline = rs.pipeline()
config = rs.config()

# Get device product line for setting a supporting resolution
pipeline_wrapper = rs.pipeline_wrapper(pipeline)
pipeline_profile = config.resolve(pipeline_wrapper)
device = pipeline_profile.get_device()
device_product_line = str(device.get_info(rs.camera_info.product_line))

# found_rgb = False
# for s in device.sensors:
#     if s.get_info(rs.camera_info.name) == 'RGB Camera':
#         found_rgb = True
#         break
# if not found_rgb:
#     print("The demo requires Depth camera with Color sensor")
#     exit(0)

config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

# Start streaming
profile = pipeline.start(config)

# Get intrinsics
align = rs.align(rs.stream.color)
color_stream = profile.get_stream(rs.stream.color).as_video_stream_profile()
intr = color_stream.get_intrinsics()
depth_scale = 10000.0  # Depth units to meters: z = raw_depth / depth_scale
    
# Pose estimation setup
backend = 'onnxruntime'
openpose_skeleton = False
# Default to CPU; override by setting RTM_DEVICE to 'cuda' or 'mps' if available.
device = os.environ.get("RTM_DEVICE", "cpu")
wholebody = Wholebody(to_openpose=openpose_skeleton,
                      mode='lightweight',
                      backend=backend,
                      device=device)
print('Model loaded!')


FACE_KEYPOINTS = [71, 77, 85, 89]

def keypoints_2d_to_3d(keypoints_2d, depth_image, intrinsic, depth_scale=10000.0):
    """Convert 2D keypoints into 3D camera coordinates using depth and intrinsics."""
    height, width = depth_image.shape
    fx = intrinsic.fx
    fy = intrinsic.fy
    cx = intrinsic.ppx
    cy = intrinsic.ppy

    points_3d = []
    for (u, v) in keypoints_2d:
        u_int, v_int = int(round(u)), int(round(v))
        if 0 <= v_int < height and 0 <= u_int < width:
            d = depth_image[v_int, u_int]
            if d > 0:
                z = d / depth_scale
                x = (u - cx) * z / fx
                y = (v - cy) * z / fy
                points_3d.append(np.array([x, y, z]))
            else:
                points_3d.append(None)
        else:
            points_3d.append(None)
    return points_3d


def extract_mouth_keypoints(points_3d):
    """Get the subset of 3D points we need for the mouth."""
    return {idx: points_3d[idx] if idx < len(points_3d) else None for idx in FACE_KEYPOINTS}


def main():
    robot_ip = "127.0.0.1"
    robot_port = 12345
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print(f"UDP socket configured to send to {robot_ip}:{robot_port}.")

    cur_time = None
    try:
        while True:
            if cur_time is None:
                cur_time = time.time()
            else:
                new_time = time.time()
                print(f"Frame interval: {new_time - cur_time:.3f} sec")
                cur_time = new_time

            frames = pipeline.wait_for_frames()
            frames = align.process(frames)
            depth_frame = frames.get_depth_frame()
            color_frame = frames.get_color_frame()
            if not depth_frame or not color_frame:
                continue

            depth_image = np.asanyarray(depth_frame.get_data())
            color_image_ = np.asanyarray(color_frame.get_data())
            color_image = cv2.cvtColor(color_image_, cv2.COLOR_BGR2RGB)

            # Run wholebody detector on the color image
            keypoints, scores = wholebody(color_image)

            # Convert 2D keypoints to 3D using depth and intrinsics
            keypoints_3d = keypoints_2d_to_3d(keypoints[0], depth_image, intr, depth_scale=depth_scale)
            mouth_keypoints = extract_mouth_keypoints(keypoints_3d)

            valid_frame = all(mouth_keypoints[idx] is not None for idx in FACE_KEYPOINTS)
            if not valid_frame:
                print("This frame failed to detect a vital lip component.")
                continue

            lip_distance = np.linalg.norm(mouth_keypoints[89] - mouth_keypoints[85])
            mouth_position = np.mean(np.stack(list(mouth_keypoints.values())), axis=0)
            print(f"Distance between lips: {lip_distance:.4f}")
            print(f"Mouth position: {mouth_position}")

            marker_id = 0
            roll = np.pi / 2.0
            pitch = 0.0
            yaw = 0.0

            data_string = (
                f"{marker_id},{mouth_position[0]:.4f},{mouth_position[1]:.4f},{mouth_position[2]:.4f},"
                f"{roll:.4f},{pitch:.4f},{yaw:.4f}"
            )
            sock.sendto(data_string.encode(), (robot_ip, robot_port))

    except KeyboardInterrupt:
        print("Stopping stream...")
    finally:
        pipeline.stop()
        sock.close()


if __name__ == "__main__":
    main()
