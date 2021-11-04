import os

import launch
from ament_index_python.packages import get_package_share_directory
from launch.actions import ExecuteProcess
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def get_robot_spawn_args():
    ROBOT_MODEL = os.environ['ROBOT_MODEL']
    POSE_INIT_X = os.environ['POSE_INIT_X']
    POSE_INIT_Y = os.environ['POSE_INIT_Y']
    POSE_INIT_Z = os.environ['POSE_INIT_Z']

    robot_sdf = os.path.join(get_package_share_directory('tiplu_world'),
                             'models',
                             ROBOT_MODEL,
                             ROBOT_MODEL + '.sdf')
    robot_xml = open(robot_sdf, 'r').read()
    robot_xml = robot_xml.replace('"', '\\"')

    initial_pose = '{position: ' +\
        '{x: ' + POSE_INIT_X + ', ' +\
        'y: ' + POSE_INIT_Y + ', ' +\
        'z: ' + POSE_INIT_Z + '}}'

    spawn_args = '{name: \"' + ROBOT_MODEL + '\",' +\
                 'xml: \"' + robot_xml + '\",' +\
                 'initial_pose: ' + initial_pose + '}'
    return spawn_args


def generate_launch_description():
    launch_file_dir = os.path.join(get_package_share_directory('tiplu_world'), 'launch')
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')

    ld = launch.LaunchDescription([
        launch.actions.IncludeLaunchDescription(
            launch.launch_description_sources.PythonLaunchDescriptionSource(
                [get_package_share_directory(
                    'aws_hospital_world'), '/launch/empty_hospital.launch.py']
            ),
            launch_arguments={
                'gui': 'true'
            }.items()),

        ExecuteProcess(
            cmd=['ros2', 'param', 'set', '/gazebo', 'use_sim_time', use_sim_time],
            output='screen'),

        # Spawn Robot in World
        ExecuteProcess(
            cmd=['ros2', 'service', 'call', '/spawn_entity', 'gazebo_msgs/SpawnEntity', get_robot_spawn_args()],
            output='screen'),

        # Robot state publisher
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource([launch_file_dir, '/robot_state_publisher.launch.py']),
            launch_arguments={'use_sim_time': use_sim_time}.items(),
        ),
    ])
    return ld


if __name__ == '__main__':
    generate_launch_description()
