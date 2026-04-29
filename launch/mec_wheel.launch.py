from launch import LaunchDescription 
from launch.actions import TimerAction 
from launch_ros.actions import Node 

def generate_launch_description(): 
    mec_wheel_node = Node(
        package='mec_wheel',
        executable='mec_wheel_node',
        name='mec_wheel_node',
        output='screen'
    ) 
    
    return LaunchDescription([
        TimerAction(
            period=10.0,
            actions=[mec_wheel_node] 
        ) 
    ])
