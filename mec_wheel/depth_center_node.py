import math
import numpy as np

import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data

from sensor_msgs.msg import Image
from std_msgs.msg import Float32


class DepthCenterNode(Node):
    def __init__(self):
        super().__init__('depth_center_node')

        self.declare_parameter('depth_image_topic', '/camera/camera/depth/image_rect_raw')
        self.declare_parameter('target_depth_topic', '/target_depth')

        self.declare_parameter('roi_width', 80)
        self.declare_parameter('roi_height', 60)

        # RealSense 16UC1 depth는 보통 mm 단위이므로 m로 바꾸기 위해 0.001 사용
        self.declare_parameter('depth_scale', 0.001)

        self.declare_parameter('min_depth', 0.10)
        self.declare_parameter('max_depth', 3.00)

        self.declare_parameter('filter_alpha', 0.35)
        self.declare_parameter('min_valid_pixels', 30)

        self.depth_image_topic = str(self.get_parameter('depth_image_topic').value)
        self.target_depth_topic = str(self.get_parameter('target_depth_topic').value)

        self.roi_width = int(self.get_parameter('roi_width').value)
        self.roi_height = int(self.get_parameter('roi_height').value)

        self.depth_scale = float(self.get_parameter('depth_scale').value)
        self.min_depth = float(self.get_parameter('min_depth').value)
        self.max_depth = float(self.get_parameter('max_depth').value)
        self.filter_alpha = float(self.get_parameter('filter_alpha').value)
        self.min_valid_pixels = int(self.get_parameter('min_valid_pixels').value)

        self.filtered_depth = None
        self.last_log_time = 0.0

        self.depth_pub = self.create_publisher(Float32, self.target_depth_topic, 10)

        self.depth_sub = self.create_subscription(
            Image,
            self.depth_image_topic,
            self.depth_callback,
            qos_profile_sensor_data
        )

        self.get_logger().info(f'DepthCenterNode started')
        self.get_logger().info(f'Subscribe depth image: {self.depth_image_topic}')
        self.get_logger().info(f'Publish target depth: {self.target_depth_topic}')

    def now_sec(self):
        return self.get_clock().now().nanoseconds * 1e-9

    def low_pass(self, prev, new):
        if prev is None:
            return new
        a = self.filter_alpha
        return a * new + (1.0 - a) * prev

    def depth_callback(self, msg: Image):
        if msg.encoding != '16UC1':
            now = self.now_sec()
            if now - self.last_log_time > 2.0:
                self.get_logger().warn(
                    f'Unsupported depth encoding: {msg.encoding}. Expected 16UC1.'
                )
                self.last_log_time = now
            return

        # 16UC1이므로 픽셀 1개 = uint16 1개 = 2 bytes
        dtype = '>u2' if msg.is_bigendian else '<u2'

        try:
            depth_raw = np.frombuffer(msg.data, dtype=dtype)

            # step은 한 행의 byte 수입니다.
            # 16UC1이므로 한 행의 uint16 개수 = step / 2
            row_pixels = msg.step // 2
            depth_img = depth_raw.reshape((msg.height, row_pixels))

            # padding이 있을 수 있으므로 실제 width까지만 사용
            depth_img = depth_img[:, :msg.width]

        except Exception as e:
            self.get_logger().warn(f'Failed to decode depth image: {e}')
            return

        h, w = depth_img.shape

        cx = w // 2
        cy = h // 2

        half_w = self.roi_width // 2
        half_h = self.roi_height // 2

        x1 = max(0, cx - half_w)
        x2 = min(w, cx + half_w)
        y1 = max(0, cy - half_h)
        y2 = min(h, cy + half_h)

        roi = depth_img[y1:y2, x1:x2].astype(np.float32)

        # 0은 보통 depth invalid 값으로 처리
        valid = roi[roi > 0.0] * self.depth_scale

        valid = valid[
            (valid >= self.min_depth) &
            (valid <= self.max_depth) &
            np.isfinite(valid)
        ]

        if valid.size < self.min_valid_pixels:
            now = self.now_sec()
            if now - self.last_log_time > 1.0:
                self.get_logger().warn(
                    f'Not enough valid depth pixels: {valid.size}'
                )
                self.last_log_time = now
            return

        # 평균보다 median이 튀는 값에 강함
        depth_m = float(np.median(valid))

        self.filtered_depth = self.low_pass(self.filtered_depth, depth_m)

        out = Float32()
        out.data = float(self.filtered_depth)
        self.depth_pub.publish(out)

        now = self.now_sec()
        if now - self.last_log_time > 1.0:
            self.get_logger().info(f'target_depth: {out.data:.3f} m')
            self.last_log_time = now


def main(args=None):
    rclpy.init(args=args)
    node = DepthCenterNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
