import rclpy
from rclpy.node import Node
from sensor_msgs.msg import NavSatFix
from geometry_msgs.msg import PoseStamped
import math
from rclpy.qos import QoSProfile, QoSReliabilityPolicy


class Gps2LocalMapPose(Node):
    def __init__(self):
        super().__init__('gps_to_local_map_pose')

        # 🔥 Declare parameters (so you can change without editing code)
        self.declare_parameter('origin_lat', 0.0)
        self.declare_parameter('origin_lon', 0.0)
        self.declare_parameter('origin_alt', 0.0)

        self.origin_lat = self.get_parameter('origin_lat').value
        self.origin_lon = self.get_parameter('origin_lon').value
        self.origin_alt = self.get_parameter('origin_alt').value

        self.get_logger().info(
            f"gps_to_local_map_pose: Using FIXED origin: lat={self.origin_lat}, lon={self.origin_lon}, alt={self.origin_alt}"
        )

        self.last_pose = PoseStamped()
        self.pose_msg_count = 0
        self.gps_heading = 0.0
        self.q = self.quaternion_from_euler(0.0, 0.0, 0.0)

        # Subscriber
        # Define a BEST_EFFORT QoS profile for subscriptions
        best_effort_qos = QoSProfile(
            reliability=QoSReliabilityPolicy.BEST_EFFORT,
            depth=10
        )

        self.sub = self.create_subscription(
            NavSatFix,
            'gps/fix',
            self.callback,
            qos_profile=best_effort_qos
        )

        # Publisher
        self.pub = self.create_publisher(
            PoseStamped,
            'map_pose',
            10
        )

    def callback(self, msg):
        lat = msg.latitude
        lon = msg.longitude

        # 🔥 More accurate conversion (use origin latitude)
        lat_rad = math.radians(self.origin_lat)

        meters_per_deg_lat = 110540
        meters_per_deg_lon = 111320 * math.cos(lat_rad)

        dx = (lon - self.origin_lon) * meters_per_deg_lon
        dy = (lat - self.origin_lat) * meters_per_deg_lat
        dz = msg.altitude - self.origin_alt

        pose = PoseStamped()
        pose.header.stamp = self.get_clock().now().to_msg()
        pose.header.frame_id = "map"

        pose.pose.position.x = dx
        pose.pose.position.y = dy
        pose.pose.position.z = dz

        self.pose_msg_count += 1

        if self.pose_msg_count > 1:
            delta_x = pose.pose.position.x - self.last_pose.pose.position.x
            delta_y = pose.pose.position.y - self.last_pose.pose.position.y
            dist_moved = math.sqrt(delta_x**2 + delta_y**2)

            if dist_moved > 0.05:  # must have moved at least 5cm to calculate new heading
                self.gps_heading = math.atan2(delta_y, delta_x)  # -pi to +pi from East
                self.q = self.quaternion_from_euler(0.0, 0.0, self.gps_heading)

        pose.pose.orientation.x = self.q[0]
        pose.pose.orientation.y = self.q[1]
        pose.pose.orientation.z = self.q[2]
        pose.pose.orientation.w = self.q[3]
        self.last_pose = pose

        self.pub.publish(pose)


def main():
    rclpy.init()
    node = Gps2LocalMapPose()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
