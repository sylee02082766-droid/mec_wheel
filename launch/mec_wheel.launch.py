from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='mec_wheel',
            executable='mec_wheel_node',
            name='mec_wheel_node',
            output='screen',
            emulate_tty=True,
            respawn=True,
            respawn_delay=2.0,
            parameters=[{
                'desired_search_distance': 1.5,
                'stop_distance': 0.30,

                'search_lateral_speed': 0.25,
                'max_align_lateral_speed': 0.18,
                'max_approach_speed': 0.12,
                'max_depth_correction': 0.10,
                'max_yaw_rate': 0.35,

                'x_kp_align': 1.0,
                'x_kp_approach': 0.8,
                'z_kp_search': 0.8,
                'z_kp_approach': 0.5,
                'yaw_kp': 0.8,

                'align_x_tol': 0.04,
                'align_z_tol': 0.15,
                'stop_x_tol': 0.02,
                'stop_z_tol': 0.03,

                'align_hold_time': 0.7,
                'stop_hold_time': 0.5,
                'recover_wait_time': 0.8,

                'marker_timeout': 0.35,
                'depth_timeout': 0.35,

                'min_valid_depth': 0.10,
                'max_valid_depth': 3.0,

                'filter_alpha': 0.35,
                'control_period': 0.10,

                # 실제 회전 방향이 반대로 나오면 1.0 -> -1.0
                'search_yaw_sign': 1.0,
                'align_yaw_sign': 1.0
            }]
        )
    ])
