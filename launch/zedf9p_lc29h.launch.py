""" Launch ZED-F9P and LC29H DA RTK GPS drivers, along with a node to Generate XY offsets from origin"""
import os
from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch.substitutions import LaunchConfiguration, TextSubstitution
from launch_ros.actions import ComposableNodeContainer
from launch_ros.descriptions import ComposableNode


def generate_launch_description():
  """Generate launch description for ublox_dgnss components."""

  namespace = LaunchConfiguration('namespace')
  device_family = LaunchConfiguration("device_family")
  device_serial_string = LaunchConfiguration('device_serial_string')
  frame_id = LaunchConfiguration('frame_id')

  # Declare launch arguments

  # LC29H launch arguments
  port_arg = DeclareLaunchArgument(
      'port',
      default_value='/dev/ttyUSB0',
      description='Serial port for GPS device'
  )

  baudrate_arg = DeclareLaunchArgument(
      'baudrate',
      default_value='115200',
      description='Baudrate for GPS device'
  )

  # ntrip_client launch arguments (forwarded to included launch)
  ntrip_host_arg = DeclareLaunchArgument(
      'host',
      default_value='',
      description='NTRIP host'
  )

  ntrip_port_arg = DeclareLaunchArgument(
      'ntrip_port',
      default_value='2101',
      description='NTRIP port'
  )

  ntrip_mountpoint_arg = DeclareLaunchArgument(
      'mountpoint',
      default_value='',
      description='NTRIP mountpoint'
  )

  ntrip_username_arg = DeclareLaunchArgument(
      'username',
      default_value='',
      description='NTRIP username'
  )

  ntrip_password_arg = DeclareLaunchArgument(
      'password',
      default_value='none',
      description='NTRIP password'
  )

  ntrip_authenticate_arg = DeclareLaunchArgument(
      'authenticate',
      default_value='true',
      description='NTRIP authenticate'
  )

  ntrip_send_nmea_arg = DeclareLaunchArgument(
      'send_nmea',
      default_value='false',
      description='NTRIP send_nmea'
  )

  # ublox launch arguments
  log_level_arg = DeclareLaunchArgument(
    "log_level", default_value=TextSubstitution(text="INFO")
  )
  namespace_arg = DeclareLaunchArgument(
    "namespace", default_value=""
  )
  device_family_arg = DeclareLaunchArgument(
    "device_family", default_value=TextSubstitution(text="F9P")
  )
  device_serial_string_arg = DeclareLaunchArgument(
    "device_serial_string",
    default_value="",
    description="Serial string of the device to use"
  )
  frame_id_arg = DeclareLaunchArgument(
    "frame_id",
    default_value="ubx",
    description="The frame_id to use in header of published messages"
  )

  params = [{"DEVICE_FAMILY": device_family},
            {'DEVICE_SERIAL_STRING': device_serial_string},
            {'FRAME_ID': frame_id},
            {'CFG_USBOUTPROT_NMEA': False},
            {'CFG_RATE_MEAS': 10},
            {'CFG_RATE_NAV': 100},
            {'CFG_MSGOUT_UBX_NAV_HPPOSLLH_USB': 1},
            {'CFG_MSGOUT_UBX_NAV_STATUS_USB': 5},
            {'CFG_MSGOUT_UBX_NAV_COV_USB': 1},
            {'CFG_MSGOUT_UBX_RXM_RTCM_USB': 1}]

  container1 = ComposableNodeContainer(
    name='ublox_dgnss_container',
    namespace='',
    package='rclcpp_components',
    executable='component_container_mt',
    arguments=['--ros-args', '--log-level', LaunchConfiguration('log_level')],
    composable_node_descriptions=[
      ComposableNode(
        package='ublox_dgnss_node',
        plugin='ublox_dgnss::UbloxDGNSSNode',
        name='ublox_dgnss',
        namespace=namespace,
        parameters=params,
        remappings=[("ntrip_client/rtcm", "rtcm")]
      )
    ]
  )

  container2 = ComposableNodeContainer(
    name='ublox_nav_sat_fix_hp_container',
    namespace='',
    package='rclcpp_components',
    executable='component_container_mt',
    arguments=['--ros-args', '--log-level', LaunchConfiguration('log_level')],
    composable_node_descriptions=[
      ComposableNode(
        package='ublox_nav_sat_fix_hp_node',
        plugin='ublox_nav_sat_fix_hp::UbloxNavSatHpFixNode',
        name='ublox_nav_sat_fix_hp',
        namespace=namespace
      )
    ]
  )

  # gps_xy_node for generating XY offsets from origin for LC29H data
  # Command: ros2 run lc29h_da_rtk_gps_driver gps_xy_node --ros-args -p origin_lat:=33.1577935 -p origin_lon:=-96.9373084 -p origin_alt:=143.684
  gps_xy_node = Node(
      package='lc29h_da_rtk_gps_driver',
      executable='gps_xy_node',
      name='gps_xy_node',
      output='screen',
      parameters=[{
          'origin_lat': 33.15777543,
          'origin_lon': -96.93730808,
          'origin_alt': 169.54
      }]
  )

  # gps_xy_node for generating XY offsets from origin for ZED-F9P data
  # Command: ros2 run lc29h_da_rtk_gps_driver gps_xy_node --ros-args -p origin_lat:=33.1577935 -p origin_lon:=-96.9373084 -p origin_alt:=143.684
  zedf9p_gps_xy_node = Node(
      package='lc29h_da_rtk_gps_driver',
      executable='gps_xy_node',
      name='zedf9p_gps_xy_node',
      output='screen',
      parameters=[{
          'origin_lat': 33.15777543,
          'origin_lon': -96.93730808,
          'origin_alt': 169.54
      }],
      remappings=[("gps/fix", "fix"), ("gps/xy", "gps/zedf9p_xy")]
  )

  # Node 2: lc29h_da_rtk_gps_driver
  # Command: ros2 run lc29h_da_rtk_gps_driver lc29h_da_rtk_gps_driver
  lc29h_da_rtk_gps_driver_node = Node(
      package='lc29h_da_rtk_gps_driver',
      executable='lc29h_da_rtk_gps_driver',
      name='lc29h_da_rtk_gps_driver',
      output='screen',
      parameters=[{
          'port': LaunchConfiguration('port'),
          'baudrate': LaunchConfiguration('baudrate')
      }]
  )

  # Launch file: ntrip_client ntrip_client_launch.py
  # Command: ros2 launch ntrip_client ntrip_client_launch.py host:=rtk2go.com port:=2101 mountpoint:=LittleElm_L1L5 username:=paul.bouchier@gmail.com password:=none authenticate:=true send_nmea:=false
  ntrip_client_launch = IncludeLaunchDescription(
      PythonLaunchDescriptionSource(
          os.path.join(
              get_package_share_directory('ntrip_client'),
              'ntrip_client_launch.py'
          )
      ),
      launch_arguments={
          'host': LaunchConfiguration('host'),
          'port': LaunchConfiguration('ntrip_port'),
          'mountpoint': LaunchConfiguration('mountpoint'),
          'username': LaunchConfiguration('username'),
          'password': LaunchConfiguration('password'),
          'authenticate': LaunchConfiguration('authenticate'),
          'send_nmea': LaunchConfiguration('send_nmea')
      }.items()
  )

  return LaunchDescription([
    port_arg,
    baudrate_arg,
    ntrip_host_arg,
    ntrip_port_arg,
    ntrip_mountpoint_arg,
    ntrip_username_arg,
    ntrip_password_arg,
    ntrip_authenticate_arg,
    ntrip_send_nmea_arg,
    gps_xy_node,
    zedf9p_gps_xy_node,
    lc29h_da_rtk_gps_driver_node,
    ntrip_client_launch,
    log_level_arg,
    device_family_arg,
    namespace_arg,
    device_serial_string_arg,
    frame_id_arg,
    container1,
    container2,
    ])
