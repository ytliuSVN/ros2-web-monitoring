from os.path import join

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import EnvironmentVariable, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    params_file = join(
        get_package_share_directory('gps_publisher'), 'config', 'params.yaml')

    return LaunchDescription([
        DeclareLaunchArgument(
            'csv_path',
            default_value=EnvironmentVariable(
                'GPS_CSV_PATH', default_value='/data/path_data.csv'),
        ),
        DeclareLaunchArgument(
            'publish_rate_hz',
            default_value=EnvironmentVariable(
                'PUBLISH_RATE_HZ', default_value='5'),
        ),
        DeclareLaunchArgument('frame_id', default_value='gps_link'),
        DeclareLaunchArgument('loop', default_value='true'),
        Node(
            package='gps_publisher',
            executable='gps_publisher_node',
            name='gps_publisher',
            output='screen',
            parameters=[
                params_file,
                {
                    'csv_path': LaunchConfiguration('csv_path'),
                    'publish_rate_hz': ParameterValue(
                        LaunchConfiguration('publish_rate_hz'), value_type=float),
                    'frame_id': LaunchConfiguration('frame_id'),
                    'loop': ParameterValue(
                        LaunchConfiguration('loop'), value_type=bool),
                },
            ],
        ),
    ])
