## License: Apache 2.0. See LICENSE file in root directory.
## Copyright(c) 2015-2017 Intel Corporation. All Rights Reserved.

###############################################
##      Open CV and Numpy integration        ##
###############################################
#py3_10/window
import time    
import open3d as o3d
import open3d.visualization.gui as gui
import open3d.visualization.rendering as rendering
import threading
import pyrealsense2 as rs
import numpy as np
import cv2
from tqdm import tqdm
from _viz_utils import *
from rtmlib import Wholebody
import socket

COCO_INDEX = np.load('coco.npy', allow_pickle=True)

# Configure depth and color streams
pipeline = rs.pipeline()
config = rs.config()

# Get device product line for setting a supporting resolution
pipeline_wrapper = rs.pipeline_wrapper(pipeline)
pipeline_profile = config.resolve(pipeline_wrapper)
device = pipeline_profile.get_device()
device_product_line = str(device.get_info(rs.camera_info.product_line))

found_rgb = False
for s in device.sensors:
    if s.get_info(rs.camera_info.name) == 'RGB Camera':
        found_rgb = True
        break
if not found_rgb:
    print("The demo requires Depth camera with Color sensor")
    exit(0)

config.enable_stream(rs.stream.depth, 1280, 720, rs.format.z16, 30)
config.enable_stream(rs.stream.color, 1280, 720, rs.format.bgr8, 30)

# Start streaming
profile = pipeline.start(config)

# Get intrinsics
align = rs.align(rs.stream.color)
color_stream = profile.get_stream(rs.stream.color).as_video_stream_profile()
intr = color_stream.get_intrinsics()
o3d_intr = o3d.camera.PinholeCameraIntrinsic(
    width=intr.width,
    height=intr.height,
    fx=intr.fx,
    fy=intr.fy,
    cx=intr.ppx,
    cy=intr.ppy
)
    
# Pose estimation setup
device = 'cuda'  # 'cuda' or 'mps' if available
# device = 'cuda'  # 'cuda' or 'mps' if available
backend = 'onnxruntime'
openpose_skeleton = False
wholebody = Wholebody(to_openpose=openpose_skeleton,
                      mode='performance',
                      backend=backend,
                      device=device)


material_pc = rendering.MaterialRecord()
# material_pc.point_size = 3
# material_pc.base_color = [1.0, 1.0, 1.0, 1]
# material_pc.shader = "defaultLitTransparency"
# material_pc.has_alpha = True

material_sphere = rendering.MaterialRecord()
material_sphere.shader = "defaultLit"

material_line = rendering.MaterialRecord()
material_line.shader = "unlitLine"
material_line.line_width = 7.0  # Set the desired thickness here
material_line.base_color = np.array([1,0,0,1])
# material_line.depth_test = False  # Disable depth test → lines always visible on top


class RealSenseSceneApp:
    def __init__(self, pipeline, align, o3d_intr):
        self.pipeline = pipeline
        self.align = align
        self.o3d_intr = o3d_intr
        self.cur_time = None

        self.pcd = o3d.geometry.PointCloud()
        self.old_pose_geometries = []

        # Open3D GUI setup
        gui.Application.instance.initialize()
        self.window = gui.Application.instance.create_window("RealSense 3D Viewer", 1280, 720)
        
        self.scene = gui.SceneWidget()
        self.scene.scene = rendering.Open3DScene(self.window.renderer)
        self.window.add_child(self.scene)

        # Add initial empty geometry to the scene
        mat = rendering.MaterialRecord()
        mat.shader = "defaultUnlit"
        self.scene.scene.add_geometry("pcd", self.pcd, mat)
        # Add origin coordinate frame (XYZ axes)
        coord_frame = o3d.geometry.TriangleMesh.create_coordinate_frame(size=0.1, origin=[0, 0, 0])
        self.scene.scene.add_geometry("origin", coord_frame, rendering.MaterialRecord())

        self.skeleton_mat = rendering.MaterialRecord()
        self.skeleton_mat.shader = "unlitLine"

        # For thread-safe communication
        self.new_pcd_points = None
        self.new_pcd_colors = None
        self.new_keypoints_3d = None
        self.new_scores = None

        # Get skeleton info once
        self.skeleton_info, self.keypoint_info = COCO_INDEX
        
        self.robot_ip = "127.0.0.1"  
        self.robot_port = 12345
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        print(f"UDP 소켓이 {self.robot_ip}:{self.robot_port} 로 데이터를 전송하도록 설정되었습니다.")

        self.running = True
        threading.Thread(target=self.update_loop, daemon=True).start()

    def update_loop(self):
            try:
                while self.running:
                    if self.cur_time is None:
                        self.cur_time = time.time()
                    else:
                        new_time = time.time()
                        # print(new_time-self.cur_time)
                        self.cur_time = new_time
                    frames = pipeline.wait_for_frames()
                    frames = self.align.process(frames)
                    depth_frame = frames.get_depth_frame()
                    color_frame = frames.get_color_frame()
                    if not depth_frame or not color_frame:
                        continue

                    # Convert images to numpy arrays
                    depth_image = np.asanyarray(depth_frame.get_data())
                    color_image_ = np.asanyarray(color_frame.get_data())
                    color_image = cv2.cvtColor(color_image_, cv2.COLOR_BGR2RGB)  # ✅ Fix color order

                    # print(f"color img shape: {color_image.shape}")
                    # print(f"depth img shape: {depth_image.shape}")
                    rgbd_image = o3d.geometry.RGBDImage.create_from_color_and_depth(
                        o3d.geometry.Image(color_image),
                        o3d.geometry.Image(depth_image),
                        depth_scale=1000.0,
                        depth_trunc=3.0,
                        convert_rgb_to_intensity=False
                    )

                    new_pcd = o3d.geometry.PointCloud.create_from_rgbd_image(rgbd_image, self.o3d_intr)

                    # Run wholebody detector on the color image (your function)
                    keypoints, scores = wholebody(color_image)

                    # Convert 2D keypoints to 3D using depth and intrinsics
                    keypoints_3d = keypoints_2d_to_3d_open3d(keypoints[0], depth_image, self.o3d_intr)

                    # Store new data for main thread to update visualization
                    self.new_pcd_points = np.asarray(new_pcd.points)
                    self.new_pcd_colors = np.asarray(new_pcd.colors)
                    self.new_keypoints_3d = keypoints_3d
                    self.new_scores = scores[0]

                    # Post update to main GUI thread
                    gui.Application.instance.post_to_main_thread(self.window, self.update_scene)
                    

            except RuntimeError:
                print("Playback finished or interrupted.")

            finally:
                self.pipeline.stop()
                self.sock.close()
                self.running = False

    def update_scene(self):
        # time.sleep(0.75)  # wait 0.5 sec between frames
        # Update point cloud points and colors
        if self.new_pcd_points is not None and self.new_pcd_colors is not None:
            self.pcd.points = o3d.utility.Vector3dVector(self.new_pcd_points)
            self.pcd.colors = o3d.utility.Vector3dVector(self.new_pcd_colors)

            self.scene.scene.remove_geometry("pcd")
            self.scene.scene.add_geometry("pcd", self.pcd, material_pc)


        # Remove old skeleton geometries
        for geo_name in self.old_pose_geometries:
            self.scene.scene.remove_geometry(geo_name)
        self.old_pose_geometries.clear()

        # Draw new skeleton lines and points if available
        if self.new_keypoints_3d is not None and self.new_scores is not None:
            new_geos, keypoint_3d_positions = draw_face_3d(self.scene, self.new_keypoints_3d, self.new_scores, 
                                        self.keypoint_info)
            # keypoint_3d_positions 의 index:            
                # 71: 입 오른쪽 끝 지점
                # 74: 윗 입술 중간, 위
                # 77: 입 왼쪽 끝 지점
                # 80: 아랫 입술 중간, 밑
                # 85: 윗 입술 중간, 밑
                # 89: 아랫 입술 중간, 위

            self.old_pose_geometries.extend(new_geos)
        
        # Mouth 3D position stuff
        valid_frame = True
        for lip_idx in keypoint_3d_positions.keys():
            if keypoint_3d_positions[lip_idx] is None:
                valid_frame = False
                print('This frame failed to detect a vital lip component.')
                break
        if valid_frame:
            lip_distance = np.linalg.norm(keypoint_3d_positions[89]-keypoint_3d_positions[85])
            mouth_position = np.mean(np.stack([keypoint_3d_positions[71], keypoint_3d_positions[77], keypoint_3d_positions[85], keypoint_3d_positions[89]]), axis=0)
            print(f'Distance between lips: {lip_distance}')
            print(f'Mouth position: {mouth_position}')
            
            marker_id = 0
            roll = np.pi / 2.0
            pitch = 0.0
            yaw = 0.0
            
            data_string = f"{marker_id},{mouth_position[0]:.4f},{mouth_position[1]:.4f},{mouth_position[2]:.4f}," \
                          f"{roll:.4f},{pitch:.4f},{yaw:.4f}"
                          
            self.sock.sendto(data_string.encode(), (self.robot_ip, self.robot_port))

        self.scene.force_redraw()

    def run(self):
        gui.Application.instance.run()
        
app = RealSenseSceneApp(pipeline, align, o3d_intr)
app.run()