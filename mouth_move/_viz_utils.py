import open3d as o3d
import open3d.visualization.gui as gui
import open3d.visualization.rendering as rendering
import numpy as np

material_pc = rendering.MaterialRecord()
material_pc.point_size = 3
material_pc.base_color = [1.0, 1.0, 1.0, 0.993]
material_pc.shader = "defaultLitTransparency"
material_pc.has_alpha = True

material_sphere = rendering.MaterialRecord()
material_sphere.shader = "defaultLit"

material_line = rendering.MaterialRecord()
material_line.shader = "unlitLine"
material_line.line_width = 7.0  # Set the desired thickness here
material_line.base_color = np.array([1,0,0,1])

def keypoints_2d_to_3d_open3d(keypoints_2d, depth_image, intrinsic, depth_scale=1000.0):
    """
    Converts 2D keypoints into 3D using Open3D-style intrinsics and scaling.

    Args:
        keypoints_2d: (N, 2) array of [u, v] pixel coordinates.
        depth_image: Open3D depth image (uint16) used to construct RGBDImage.
        intrinsic: open3d.camera.PinholeCameraIntrinsic.
        depth_scale: Scale factor used when creating the RGBD image. Default: 1000.0 (mm to m).

    Returns:
        List of 3D points (np.array of shape (3,)), or None if invalid depth.
    """
    height, width = np.asarray(depth_image).shape
    depth_np = np.asarray(depth_image).astype(np.float32)
    
    fx = intrinsic.intrinsic_matrix[0, 0]
    fy = intrinsic.intrinsic_matrix[1, 1]
    cx = intrinsic.intrinsic_matrix[0, 2]
    cy = intrinsic.intrinsic_matrix[1, 2]

    points_3d = []
    for (u, v) in keypoints_2d:
        u_int, v_int = int(round(u)), int(round(v))
        if 0 <= v_int < height and 0 <= u_int < width:
            d = depth_np[v_int, u_int]
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

def draw_skeleton_3d(scene, points_3d, scores, keypoint_info, skeleton_info, kpt_thr=0.5, color_default=(1, 0, 0)):
    """
    Draws 3D skeleton lines on Open3D visualizer.
    
    Args:
        vis: Open3D Visualizer
        points_3d: numpy array (N, 3) of 3D points for each keypoint
        scores: numpy array (N,) confidence scores for each keypoint
        keypoint_info: dict with keypoint meta info including 'id', 'color', 'name'
        skeleton_info: dict with skeleton links info including 'link' and 'color'
        kpt_thr: score threshold to consider keypoint visible
        color_default: fallback RGB color for lines (if skeleton_info color not provided)
    
    Returns:
        list of added geometries (LineSet) to the visualizer
    """
    # Determine visible keypoints by score threshold
    vis_kpt = [s >= kpt_thr for s in scores]

    # Create a map from keypoint name to index/id
    name_to_id = {}
    for info in keypoint_info.values():
        name_to_id[info['name']] = info['id']

    line_point_names = []
    for i, point in keypoint_info.items():
        if not vis_kpt[i] or point is None:
            continue
        idx = name_to_id.get(point['name'], None)
        
        # Create a small sphere at the 3D keypoint
        sphere = o3d.geometry.TriangleMesh.create_sphere(radius=0.005)
        if points_3d[idx] is not None:
            sphere.translate(points_3d[idx])
            sphere.compute_vertex_normals()
            
            # Optional: color each keypoint differently
            color = [1.0, 0.0, 0.0]  # red
            sphere.paint_uniform_color(color)

            # Add to scene
            scene.scene.add_geometry(f"kp_{i}", sphere, material_sphere)
            line_point_names.append(f"kp_{i}")
    
    for i, ske_info in skeleton_info.items():
        link = ske_info['link']  # ['left_shoulder', 'left_elbow'], for example
        kp0_name, kp1_name = link[0], link[1]

        # Get indices of keypoints from their names
        idx0 = name_to_id.get(kp0_name, None)
        idx1 = name_to_id.get(kp1_name, None)
        if idx0 is None or idx1 is None:
            continue

        # Check if both keypoints are visible and have valid 3D points
        if not (vis_kpt[idx0] and vis_kpt[idx1]):
            continue
        pt0 = points_3d[idx0]
        pt1 = points_3d[idx1]

        if pt0 is None or pt1 is None or (pt0 == pt1).sum()==pt0.shape[-1]:
            continue

        # Use color from skeleton_info or fallback
        # line_color = ske_info.get('color', color_default)
        line_color = [255,0,0]
        line = o3d.geometry.LineSet(
            points=o3d.utility.Vector3dVector([pt0, pt1]),
            lines=o3d.utility.Vector2iVector([[0, 1]])
        )
        line.colors = o3d.utility.Vector3dVector([line_color])

        scene.scene.add_geometry(f"line_{i}", line, material_line)
        line_point_names.append(f"line_{i}")
    return line_point_names

FACE_KEYPOINTS = [71, 77, 85, 89]

# 71: 입 오른쪽 끝 지점
# 74: 윗 입술 중간, 위
# 77: 입 왼쪽 끝 지점
# 80: 아랫 입술 중간, 밑
# 85: 윗 입술 중간, 밑
# 89: 아랫 입술 중간, 위

def draw_face_3d(scene, points_3d, scores, keypoint_info, kpt_thr=0.5, color_default=(1, 0, 0)):
    """
    Draws 3D skeleton lines on Open3D visualizer.
    
    Args:
        vis: Open3D Visualizer
        points_3d: numpy array (N, 3) of 3D points for each keypoint
        scores: numpy array (N,) confidence scores for each keypoint
        keypoint_info: dict with keypoint meta info including 'id', 'color', 'name'
        skeleton_info: dict with skeleton links info including 'link' and 'color'
        kpt_thr: score threshold to consider keypoint visible
        color_default: fallback RGB color for lines (if skeleton_info color not provided)
    
    Returns:
        list of added geometries (LineSet) to the visualizer
    """
    keypoint_3d_positions = {}
    
    # Create a map from keypoint name to index/id
    name_to_id = {}
    for info in keypoint_info.values():
        name_to_id[info['name']] = info['id']

    line_point_names = []
    for i, point in keypoint_info.items():
        if i not in FACE_KEYPOINTS:
            continue
        # print('---------------------')
        # print(f'입 오른쪽 끝 지점: {scores[71]}')
        # print(f'입 왼쪽 끝 지점: {scores[77]}')
        # print(f'윗 입술 중간, 밑: {scores[85]}')
        # print(f'아랫 입술 중간, 위: {scores[89]}')
        idx = name_to_id.get(point['name'], None)
        keypoint_3d_positions[i] = points_3d[idx]
        
        # Create a small sphere at the 3D keypoint
        sphere = o3d.geometry.TriangleMesh.create_sphere(radius=0.005)
        if points_3d[idx] is not None:
            sphere.translate(points_3d[idx])
            sphere.compute_vertex_normals()
            
            # Optional: color each keypoint differently
            color = [1.0, 0.0, 0.0]  # red
            sphere.paint_uniform_color(color)

            # Add to scene
            scene.scene.add_geometry(f"kp_{i}", sphere, material_sphere)
            line_point_names.append(f"kp_{i}")
    
    return line_point_names, keypoint_3d_positions