import socket
import time
import rclpy
from rclpy.node import Node
from rtcm_msgs.msg import Message
from diagnostic_msgs.msg import DiagnosticArray, DiagnosticStatus, KeyValue

class RtcmUdpReceiver(Node):
    def __init__(self):
        super().__init__('rtcm_udp_receiver')
        
        # Declare parameters
        self.declare_parameter('listen_ip', '0.0.0.0')
        self.declare_parameter('listen_port', 5000)
        self.declare_parameter('expected_hz', 1.0)
        
        listen_ip = self.get_parameter('listen_ip').get_parameter_value().string_value
        listen_port = self.get_parameter('listen_port').get_parameter_value().integer_value
        self.expected_hz = self.get_parameter('expected_hz').get_parameter_value().double_value
        
        # ROS 2 Publishers
        self.rtcm_pub = self.create_publisher(
            Message, 
            '/rtcm', 
            10 
        )
        self.diag_pub = self.create_publisher(
            DiagnosticArray, 
            '/diagnostics', 
            10
        )
        
        # UDP Socket Setup
        self.sock_in = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock_in.bind((listen_ip, listen_port))
        self.sock_in.settimeout(0.1) 
        
        # Diagnostic Tracking Variables
        self.msg_count = 0
        self.last_msg_time = time.time()
        self.start_time = time.time()
        self.current_hz = 0.0
        
        self.get_logger().info(f"Listening for UDP RTCM on {listen_ip}:{listen_port}")
        
        # Timers
        self.socket_timer = self.create_timer(0.001, self.socket_callback)
        self.diag_timer = self.create_timer(2.0, self.diagnostics_callback)

    def socket_callback(self):
        try:
            data, addr = self.sock_in.recvfrom(4096)
            if data:
                now = time.time()
                self.msg_count += 1
                self.last_msg_time = now
                
                # Publish RTCM Message
                msg = Message()
                msg.header.stamp = self.get_clock().now().to_msg()
                msg.header.frame_id = "gps"
                msg.message = list(data)
                self.rtcm_pub.publish(msg)
        except socket.timeout:
            pass
        except Exception as e:
            self.get_logger().error(f"Socket error: {e}")

    def diagnostics_callback(self):
        now = time.time()
        time_elapsed = now - self.start_time
        time_since_last_msg = now - self.last_msg_time
        
        if time_elapsed > 0:
            self.current_hz = self.msg_count / time_elapsed

        # Determine diagnostic severity level
        level = DiagnosticStatus.OK
        message = "Stream healthy"
        
        if time_since_last_msg > 5.0:
            level = DiagnosticStatus.ERROR
            message = "RTCM stream timeout"
        elif self.current_hz < (self.expected_hz * 0.5):
            level = DiagnosticStatus.WARN
            message = "RTCM data frequency low"

        # Construct Diagnostic Status message
        status = DiagnosticStatus()
        status.level = level
        status.name = f"{self.get_name()}: RTCM UDP Receiver Health"
        status.message = message
        status.hardware_id = self.get_parameter('listen_ip').get_parameter_value().string_value
        
        # Append telemetry key-value metadata arrays
        status.values = [
            KeyValue(key="Current Frequency (Hz)", value=f"{self.current_hz:.2f}"),
            KeyValue(key="Expected Frequency (Hz)", value=f"{self.expected_hz:.2f}"),
            KeyValue(key="Seconds Since Last Packet", value=f"{time_since_last_msg:.2f}"),
            KeyValue(key="Window Total Packets", value=str(self.msg_count))
        ]
        
        # Construct and publish the top-level DiagnosticArray wrapper
        diag_array = DiagnosticArray()
        diag_array.header.stamp = self.get_clock().now().to_msg()
        diag_array.status.append(status)
        
        self.diag_pub.publish(diag_array)

        # Reset calculation window parameters
        if time_elapsed > 10.0:
            self.msg_count = 0
            self.start_time = now

    def destroy_node(self):
        self.sock_in.close()
        super().destroy_node()

def main(args=None):
    rclpy.init(args=args)
    node = RtcmUdpReceiver()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()

if __name__ == '__main__':
    main()
