#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from my_robot_interfaces.srv import SetLedStates

    
class BatteryNode(Node):
    def __init__(self):
        super().__init__("battery") 
        self.client_ = self.create_client(SetLedStates, "set_led")
        self.timer_ = self.create_timer(0.1, self.battery_level)

        self.battery_delta = self.current_time()
        self.battery_full = True

        self.get_logger().info("BATTERY NODE HAS ACTIVATED")
    
    def current_time(self):
        seconds, nanoseconds = self.get_clock().now().seconds_nanoseconds()
        return seconds + nanoseconds / 1000000000.0
    
    def battery_level(self):
        time_now = self.current_time()
        if self.battery_full == True:
            if time_now - self.battery_delta > 4.0:
                self.battery_full = False
                self.get_logger().warn("CHARGE DEPLETED.... INITIALIZING CHARGE")
                self.call_set_led(2, 1)
                self.battery_delta = time_now
        elif self.battery_full == False:
            if time_now - self.battery_delta > 6.0:
                self.battery_full = True
                self.get_logger().info("CHARGE RESTORED")
                self.call_set_led(2, 0)
                self.battery_delta = time_now
    
    def call_set_led(self, led_number: int, led_state: int):
        while not self.client_.wait_for_service(1.0):
            self.get_logger().warn("WAITING FOR SERVER...... PLEASE INITIALIZE")

        request = SetLedStates.Request()
        request.led_number = led_number
        request.state = led_state

        future = self.client_.call_async(request)
        future.add_done_callback(self.callback_call_set_led)
    
    def callback_call_set_led(self, future):
        response: SetLedStates.Response = future.result()
        if response.success:
            self.get_logger().info(f"CALLBACK WAS SUCCESSFUL")
        else:
            self.get_logger().error(f"CALLBACK FAILIURE HAS OCCURED")
        

    
def main(args=None):
    rclpy.init(args=args)
    node = BatteryNode()
    rclpy.spin(node)
    rclpy.shutdown()
    
    
if __name__ == "__main__":
    main()
