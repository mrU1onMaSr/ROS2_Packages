#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from my_robot_interfaces.msg import HardwareStatus
    
    
class HardwareStatusPublisherNode(Node): 
    def __init__(self):
        super().__init__("hardware_status_publisher")
        self.hardware_publisher_ = self.create_publisher(HardwareStatus, "hardware_statur", 10)
        self.timer_ = self.create_timer(1.0, self.publish_hardware_status)
        self.get_logger().info("HARDWARE STAUS IS BEING PUBLISHED")
    
    def publish_hardware_status(self):
        msg = HardwareStatus()
        msg.temperature = 33.2
        msg.are_motors_ready = True
        msg.debug_message = "ALL IS WELL"
        self.hardware_publisher_.publish(msg)
    
def main(args=None):
    rclpy.init(args=args)
    node = HardwareStatusPublisherNode()
    rclpy.spin(node)
    rclpy.shutdown()

    
if __name__ == "__main__":
    main()
