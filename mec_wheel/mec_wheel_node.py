import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist, PoseArray
from std_msgs.msg import Float32, String
import math

class MecWheel(Node):
    def __init__(self):
        super().__init__('mec_wheel_node')
        
        # Publisher
        self.cmd_vel_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.status_pub = self.create_publisher(String, '/wheel_status', 10) 
        
        # Subscriber
        self.pose_sub = self.create_subscription(PoseArray, '/aruco_tf', self.aruco_callback, 10)
        self.depth_sub = self.create_subscription(Float32, '/target_depth', self.depth_callback, 10)
        
        self.state = "blind_orbit"
        self.marker_x = 0.0  
        self.marker_z = 0.0  
        self.has_marker = False
        
        self.depth_distance = 0.0
        self.has_depth = False

        self.MAX_V = 0.3  # 기본 궤도 게걸음 속도 (+X 방향)
        self.HALF_FOV_RAD = math.radians(43.5) # FOV 절반
        
        self.timer = self.create_timer(0.1, self.control_loop)

    def aruco_callback(self, msg):
        """Aruco 마커 x, z 좌표 수신"""
        if len(msg.poses) > 0:
            self.has_marker = True
            self.marker_x = msg.poses[0].position.x 
            self.marker_z = msg.poses[0].position.z 
        else:
            self.has_marker = False

    def depth_callback(self, msg):
        """Depth 수신"""
        if 0.1 < msg.data < 3.0: 
            self.depth_distance = msg.data
            self.has_depth = True
        else:
            self.has_depth = False

    def control_loop(self):
        msg = Twist()
        status_msg = String()
        status_msg.data = "moving"

        if self.state == "blind_orbit":
            msg.linear.x = self.MAX_V
            msg.angular.y = abs(self.MAX_V) / 1.5
            
            if self.has_depth:
                # 1.5m 거리 유지하게 하기
                msg.linear.z = 1.0 * (self.depth_distance - 1.5)
            
            self.get_logger().info('blind_orbit')
            
            if self.has_marker:
                self.state = "align_orbit"

        elif self.state == "align_orbit":
            if self.has_marker:
                theta = math.atan2(abs(self.marker_x), self.marker_z)
                
                w = min(theta / self.HALF_FOV_RAD, 1.0)
                
                msg.linear.x = self.MAX_V * w
                
                msg.linear.z = 1.0 * (self.marker_z - 1.5)
                msg.angular.y = 0.5 * self.marker_x 
                
                self.get_logger().info(f'align_orbit | w: {w:.2f}')
                
                if abs(self.marker_x) < 0.05:
                    self.state = "approach"
            else:
                self.state = "blind_orbit"

        elif self.state == "approach":
            if self.has_marker:
                if self.marker_z > 0.3:
                    msg.linear.z = 0.15
                    self.get_logger().info('approach')
                else:
                    self.state = "stop"
            else:
                self.state = "blind_orbit"

        elif self.state == "stop":
            msg.linear.x = 0.0
            msg.linear.y = 0.0
            msg.linear.z = 0.0
            msg.angular.x = 0.0
            msg.angular.y = 0.0
            msg.angular.z = 0.0
            
            status_msg.data = "stopped"
            self.get_logger().info('stop')

        self.cmd_vel_pub.publish(msg)
        self.status_pub.publish(status_msg)

def main(args=None):
    rclpy.init(args=args)
    node = MecWheel()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.cmd_vel_pub.publish(Twist())
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
