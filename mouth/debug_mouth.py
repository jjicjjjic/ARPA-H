import pyrealsense2 as rs
import numpy as np
import cv2

def create_colorbar(min_val, max_val, height=480, step=0.5):
    """Creates a vertical colorbar with text labels indicating depth values."""
    
    # Create gradient (0 → 255)
    gradient = np.linspace(255, 0, height).astype("uint8").reshape(height, 1)

    # Apply the same COLORMAP_JET used for depth image
    colorbar = cv2.applyColorMap(gradient, cv2.COLORMAP_JET)

    # Add numeric labels (min and max meters)
    bar = colorbar.copy()
    font = cv2.FONT_HERSHEY_SIMPLEX

    # Label for min and max depth values
    cv2.putText(bar, f"{max_val:.2f} m", (5, 20), font, 0.5, (255, 255, 255), 1)
    cv2.putText(bar, f"{min_val:.2f} m", (5, height-10), font, 0.5, (255, 255, 255), 1)

    # Add intermediate labels for depth in meters
    num_labels = int((max_val - min_val) / step)
    for i in range(num_labels):
        label_val = min_val + i * step
        y_position = int(height - (i / num_labels) * height)
        cv2.putText(bar, f"{label_val:.2f} m", (5, y_position), font, 0.5, (255, 255, 255), 1)
    
    return bar


def main():
    # Configure depth and color streams
    pipeline = rs.pipeline()
    config = rs.config()

    config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
    config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

    # Start streaming
    profile = pipeline.start(config)

    # Get depth scale (important!)
    depth_sensor = profile.get_device().first_depth_sensor()
    depth_scale = depth_sensor.get_depth_scale()  # e.g. 0.001 m per unit

    print(f"Depth Scale: {depth_scale} meters per unit")

    # Depth display limits (in meters)
    depth_min = 0.3
    depth_max = 3.0

    try:
        while True:
            frames = pipeline.wait_for_frames()

            depth_frame = frames.get_depth_frame()
            color_frame = frames.get_color_frame()
            if not depth_frame or not color_frame:
                continue

            # Convert to numpy arrays
            depth_raw = np.asanyarray(depth_frame.get_data())
            color_image = np.asanyarray(color_frame.get_data())

            # Convert raw depth values → meters
            depth_meters = depth_raw * depth_scale

            # Clip for visualization
            depth_clipped = np.clip(depth_meters, depth_min, depth_max)

            # Normalize to 0–255 for colormap
            depth_normalized = ((depth_clipped - depth_min) / (depth_max - depth_min) * 255).astype(np.uint8)

            # Apply colormap
            depth_colormap = cv2.applyColorMap(depth_normalized, cv2.COLORMAP_JET)

            # Generate colorbar (same height as the depth image)
            colorbar = create_colorbar(depth_min, depth_max, depth_colormap.shape[0], step=0.5)

            # Combine depth image + colorbar side by side
            depth_with_bar = np.hstack((depth_colormap, colorbar))

            # Show images
            cv2.imshow("RGB Image", color_image)
            cv2.imshow("Depth (meters) + Colorbar", depth_with_bar)

            if cv2.waitKey(1) & 0xFF == 27:  # ESC to exit
                break

    finally:
        pipeline.stop()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
