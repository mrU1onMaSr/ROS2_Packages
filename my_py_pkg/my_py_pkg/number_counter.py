#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from example_interfaces.msg import Int64
from example_interfaces.srv import SetBool
    
class NumberCounterNode(Node):
    def __init__(self):
        super().__init__("number_counter")
        self.count_ = 0

        self.subscriber_ = self.create_subscription(Int64, "number", self.counter, 10)
        self.publisher_ = self.create_publisher(Int64, "number_count", 10)

        self.server_ = self.create_service(SetBool, "reset_counter", self.callback_reset_counter) # type: ignore

        self.get_logger().info("COUNTER HAS COME ONLINE")
    
    def counter(self, msg: Int64):
        num = msg.data
        self.count_ += num
        self.publish_number()
    
    def publish_number(self):
        msg = Int64()
        msg.data = self.count_
        self.publisher_.publish(msg)
    
    def callback_reset_counter(self, request: SetBool.Request, response: SetBool.Response):
        if request.data == True:
            self.count_ = 0
            response.message = "SUCCESS"
            response.success = True
            self.get_logger().warn("COUNTER RESET")
            return response
        else:
            self.get_logger().error("PLEASE PROVIDE ACCURATE REQUEST")
            response.message = "ERROR"
            response.success = False
            return response
        

def main(args=None):
    rclpy.init(args=args)
    node = NumberCounterNode()
    rclpy.spin(node)
    rclpy.shutdown()
    
    
if __name__ == "__main__":
    main()
