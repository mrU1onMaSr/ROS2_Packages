#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from my_robot_interfaces.msg import LedPanelState
from my_robot_interfaces.srv import SetLedStates
    
    
class LedPanelNode(Node): 
    def __init__(self):
        super().__init__("led_panel")

        self.declare_parameter("initial_led_state", [0,0,0])

        self.led_state_publisher_ = self.create_publisher(LedPanelState, "led_panel_state", 10)
        self.timer_ = self.create_timer(5.0, self.callback_publish)

        self.server_ = self.create_service(SetLedStates, "set_led", self.callback_set_led) # type: ignore

        self.led_panel_state_: list = self.get_parameter("initial_led_state").value # type: ignore

        self.get_logger().info("LED STATES ARES BEING PUBLISHED")
    
    def callback_publish(self):
        msg = LedPanelState()
        msg.led_states = self.led_panel_state_
        self.led_state_publisher_.publish(msg)
    
    def callback_set_led(self, request: SetLedStates.Request, response: SetLedStates.Response): 
        
        try:
            self.led_panel_state_[request.led_number] = request.state
            response.success = True
            self.get_logger().info(f"LED {str(request.led_number)} HAS BEEN SET TO STATE {str(request.state)}")
            return response
        except Exception as e:
            self.get_logger().error("ERROR HAS OCCURED " + str(e))
            response.success = False
            return response
    
def main(args=None):
    rclpy.init(args=args)
    node = LedPanelNode()
    rclpy.spin(node)
    rclpy.shutdown()
    
    
if __name__ == "__main__":
    main()
