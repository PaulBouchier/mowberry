import math

from geometry_msgs.msg import PointStamped
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import NavSatFix
# from ublox_ubx_msgs.msg import UBXNavHPPosLLH
from rclpy.qos import QoSProfile, QoSReliabilityPolicy


class PrintZedf9pPos(Node):
    """ROS2 node that subscribes to GPS data and prints it periodically."""

    def __init__(self):
        """Initialize the PrintPos node."""
        super().__init__('print_pos')

        # Initialize fields
        self.h_acc = None
        self.latitude = None
        self.x = None
        self.y = None
        self.z = None
        self.last_xy_time = None
        self.last_timer_xy_time = None
        self.longitude = None
        self.altitude = None

        # Declare parameters
        self.declare_parameter('verbose', False)

        # Define a BEST_EFFORT QoS profile for subscriptions
        best_effort_qos = QoSProfile(
            reliability=QoSReliabilityPolicy.BEST_EFFORT,
            depth=10
        )

        # Subscribers
        self.fix_sub = self.create_subscription(
            NavSatFix,
            'fix',
            self.fix_callback,
            best_effort_qos
        )

        self.xy_sub = self.create_subscription(
            PointStamped,
            'gps/zedf9p_xy',
            self.xy_callback,
            10
        )

        # self.hp_pos_llh_sub = self.create_subscription(
        #     UBXNavHPPosLLH,
        #     'gps/zedf9p_xy',
        #     self.pos_llh_cb,
        #     best_effort_qos

       # Periodic timer (4 seconds)
        self.timer = self.create_timer(4.0, self.timer_callback)

        self.get_logger().info('PrintZedf9pPos node initialized and listening.')

    def fix_callback(self, msg):
        """Update the latest fix type status."""
        self.latitude = msg.latitude
        self.longitude = msg.longitude
        self.altitude = msg.altitude

    def xy_callback(self, msg):
        """Update the latest local x, y, z coordinates."""
        self.x = msg.point.x
        self.y = msg.point.y
        self.z = msg.point.z
        self.last_xy_time = msg.header.stamp.sec

    def pos_llh_cb(self, msg):
        """Update the latest h_acc from UBXNavHPPosLLH message."""
        self.h_acc = msg.h_acc

    def timer_callback(self):
        """Print the latest coordinates and fix type status."""
        if self.last_timer_xy_time is not None and self.last_xy_time <= self.last_timer_xy_time:
            return
        self.last_timer_xy_time = self.last_xy_time

        # Format values to 3 decimal places if available, otherwise 'None'
        x_str = f'{self.x:.3f}' if self.x is not None else 'None'
        y_str = f'{self.y:.3f}' if self.y is not None else 'None'
        z_str = f'{self.z:.3f}' if self.z is not None else 'None'
        h_acc_str = f'{self.h_acc:.3f}' if self.h_acc is not None else 'None'

        # Print to stdout/logger
        output_str = (
            f'X: {x_str}, Y: {y_str}, Z: {z_str}, '
            f'h_acc: {h_acc_str}'
        )

        verbose = self.get_parameter('verbose').value
        if verbose:
            lat_str = f'{self.latitude:.7f}' if self.latitude is not None else 'None'
            lon_str = f'{self.longitude:.7f}' if self.longitude is not None else 'None'
            alt_str = f'{self.altitude:.2f}' if self.altitude is not None else 'None'

            if self.latitude is not None and self.longitude is not None:
                easting, northing, zone_number = self.compute_utm(self.latitude, self.longitude)
                easting_str = f'{easting:.2f}'
                northing_str = f'{northing:.2f}'
            else:
                easting_str = 'None'
                northing_str = 'None'
                zone_number = 'None'

            output_str += (
                f', Lat: {lat_str}, Lon: {lon_str}, Alt: {alt_str}, '
                f'Easting: {easting_str}, Northing: {northing_str}, Zone: {zone_number}'
            )

        # self.get_logger().info(output_str)
        # Also print to stdout directly to ensure it appears in raw output
        print(output_str, flush=True)

    def compute_utm(self, latitude, longitude):
        """Compute UTM Easting and Northing for the given latitude and longitude."""
        # WGS84 ellipsoid constants
        K0 = 0.9996
        E = 0.00669438
        E2 = E * E
        E3 = E2 * E
        E_P2 = E / (1 - E)



        M1 = (1 - E / 4 - 3 * E2 / 64 - 5 * E3 / 256)
        M2 = (3 * E / 8 + 3 * E2 / 32 + 45 * E3 / 1024)
        M3 = (15 * E2 / 256 + 45 * E3 / 1024)
        M4 = (35 * E3 / 3072)

        R = 6378137

        # Normalize longitude to be in range [-180, 180)
        lon_normalized = (longitude % 360 + 540) % 360 - 180

        # Calculate UTM Zone
        # Special zone for Norway
        if 56 <= latitude < 64 and 3 <= lon_normalized < 12:
            zone_number = 32
        # Special zones for Svalbard
        elif 72 <= latitude <= 84 and lon_normalized >= 0:
            if lon_normalized < 9:
                zone_number = 31
            elif lon_normalized < 21:
                zone_number = 33
            elif lon_normalized < 33:
                zone_number = 35
            elif lon_normalized < 42:
                zone_number = 37
            else:
                zone_number = int((lon_normalized + 180) / 6) + 1
        else:
            zone_number = int((lon_normalized + 180) / 6) + 1

        central_lon = (zone_number - 1) * 6 - 180 + 3

        lat_rad = math.radians(latitude)
        lat_sin = math.sin(lat_rad)
        lat_cos = math.cos(lat_rad)

        lat_tan = lat_sin / lat_cos
        lat_tan2 = lat_tan * lat_tan
        lat_tan4 = lat_tan2 * lat_tan2

        lon_rad = math.radians(lon_normalized)
        central_lon_rad = math.radians(central_lon)

        n = R / math.sqrt(1 - E * lat_sin**2)
        c = E_P2 * lat_cos**2

        # Diff angle normalized to -pi..pi
        diff_lon = lon_rad - central_lon_rad
        diff_lon = (diff_lon + math.pi) % (2 * math.pi) - math.pi

        a = lat_cos * diff_lon
        a2 = a * a
        a3 = a2 * a
        a4 = a3 * a
        a5 = a4 * a
        a6 = a5 * a

        m = R * (M1 * lat_rad -
                 M2 * math.sin(2 * lat_rad) +
                 M3 * math.sin(4 * lat_rad) -
                 M4 * math.sin(6 * lat_rad))

        easting = (
            K0 * n * (
                a +
                a3 / 6 * (1 - lat_tan2 + c) +
                a5 / 120 * (5 - 18 * lat_tan2 + lat_tan4 + 72 * c - 58 * E_P2)
            ) + 500000
        )

        northing = K0 * (
            m + n * lat_tan * (
                a2 / 2 +
                a4 / 24 * (5 - lat_tan2 + 9 * c + 4 * c**2) +
                a6 / 720 * (61 - 58 * lat_tan2 + lat_tan4 + 600 * c - 330 * E_P2)
            )
        )

        if latitude < 0:
            northing += 10000000

        return easting, northing, zone_number


def main(args=None):
    """Run the printzedf9ppos node."""
    rclpy.init(args=args)
    node = PrintZedf9pPos()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        try:
            node.destroy_node()
            rclpy.shutdown()
        except Exception:
            pass


if __name__ == '__main__':
    main()
