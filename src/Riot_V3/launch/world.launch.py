import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import ExecuteProcess, DeclareLaunchArgument, IncludeLaunchDescription
from launch_ros.actions import Node
from launch.substitutions import LaunchConfiguration
from launch.launch_description_sources import PythonLaunchDescriptionSource


# this is the function launch  system will look for

def generate_launch_description():

    robot_name = 'Riot_V3'
    world_file_name = 'riot_level5.world'
    rviz_config_file_name = 'urdf_config.rviz'

    use_sim_time = LaunchConfiguration('use_sim_time', default='false')

    # full  path to urdf and world file
    
    world = os.path.join(get_package_share_directory(robot_name), 'worlds', world_file_name)

    urdf = os.path.join(get_package_share_directory(robot_name), 'urdf', 'riot.urdf')

    # read urdf contents because to spawn an entity in 
    # gazebo we need to provide entire urdf as string on command line

    xml = open(urdf, 'r').read()

    # double quotes need to be with escape sequence
    xml = xml.replace('"', '\\"')

    # this is argument format for spwan_entity service 
    spwan_args = '{name: \"riot\", xml: \"'  +  xml + '\" }'


    # starts the robot_state_publisher node
    robot_state_publisher_node = Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            parameters=[{'use_sim_time': use_sim_time}],
            arguments=[urdf]
    )

    
    # starts the joint_state_publisher node
    joint_state_publisher_node = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
    )

    # starts the rviz node
    rviz_node = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
         get_package_share_directory('Riot_V3'), 'launch'),
         '/riotsim_rviz.launch.py'])
    )

    # create and return launch description object
    return LaunchDescription([

        robot_state_publisher_node,
        joint_state_publisher_node,
        
        # start gazebo, notice we are using libgazebo_ros_factory.so instead of libgazebo_ros_init.so
        # That is because only libgazebo_ros_factory.so contains the service call to /spawn_entity
        ExecuteProcess(
            cmd=['gazebo', '--verbose', world, '-s', 'libgazebo_ros_factory.so'],
            output='screen'),

        # tell gazebo to spwan your robot in the world by calling service
        ExecuteProcess(
            cmd=['ros2', 'service', 'call', '/spawn_entity', 'gazebo_msgs/SpawnEntity', spwan_args],
            output='screen'),

        rviz_node    
    ])