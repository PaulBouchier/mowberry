#!/usr/bin/python

import socket
import serial

def serial_to_udp_relay(serial_port, baud_rate, forward_ip, forward_port):
    # Initialize UDP socket for forwarding
    sock_out = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    print(f"Opening serial port {serial_port} at {baud_rate} baud...")
    
    try:
        # Open the serial port with a short timeout to prevent permanent blocking
        ser = serial.Serial(
            port=serial_port,
            baudrate=baud_rate,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=0.1
        )
        
        print(f"Streaming data to {forward_ip}:{forward_port}...")
        
        while True:
            # Read available bytes from the serial buffer
            # 1024-4096 bytes is typical for high-baud RTCM/GNSS streams
            data = ser.read(2048)
            
            if data:
                # Forward raw binary corrections (RTCM/NMEA) over UDP
                sock_out.sendto(data, (forward_ip, forward_port))
                
    except serial.SerialException as e:
        print(f"Serial error: {e}")
    except KeyboardInterrupt:
        print("\nStreaming stopped by user.")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()
            print("Serial port closed.")
        sock_out.close()

if __name__ == "__main__":
    # Configuration
    SERIAL_PORT = "/dev/ttyUSB0"
    BAUD_RATE = 921600
    FORWARD_IP = "100.102.100.25"   # IP of the receiver script or caster
    FORWARD_PORT = 5000        # Target UDP port
    
    serial_to_udp_relay(SERIAL_PORT, BAUD_RATE, FORWARD_IP, FORWARD_PORT)

