#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from example_interfaces.srv import SetBool  
    
def main(args=None):
    rclpy.init(args=args)
    node = Node("add_two_ints_client_no_oop")
    
    client = node.create_client(SetBool, "reset_counter")
    while not client.wait_for_service(1.0):
        node.get_logger().warn("Waiting for server Initialization")


    request = SetBool.Request()
    request.data = True

    future = client.call_async(request)
    rclpy.spin_until_future_complete(node, future)

    result = future.result()
    node.get_logger().info(str(result.success) +" "+ result.message)  # type: ignore
    rclpy.shutdown()
    
    
if __name__ == "__main__":
    main()
