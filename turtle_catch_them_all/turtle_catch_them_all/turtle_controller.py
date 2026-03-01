#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from turtlesim.msg import Pose
from geometry_msgs.msg import Twist
from math import sqrt, atan2, sin ,cos
from my_robot_interfaces.msg import TurtleArray, Turtle
from my_robot_interfaces.srv import TurtleCatch
from functools import partial
    
class TurtleControllerNode(Node): 
    def __init__(self):
        super().__init__("turtle_controller")

        #initializing parameters
        self.declare_parameter("catch_closest", True)
        self.catch_closest_ = self.get_parameter("catch_closest").get_parameter_value().bool_value
        #initializing timer
        self.timer_ = self.create_timer(0.01, self.main_loop)
        #initializing subscribers and publishers
        self.pose_subscriber_ = self.create_subscription(Pose, "/turtle1/pose", self.update_position, 10)
        self.turtle_list_subscriber_ = self.create_subscription(TurtleArray, "alive_turtles", self.update_target, 10)
        self.cmd_vel_publisher_ = self.create_publisher(Twist, "/turtle1/cmd_vel", 10)
        self.catch_client_ = self.create_client(TurtleCatch, "catch_turtle")

        #initializing global variables
        self.pose = Pose()
        self.target_turtle: Turtle = None  # type: ignore

        self.get_logger().info("CATCH 'EM ALL IS RUNNING")
    
    def update_target(self, msg: TurtleArray):
        if len(msg.turtle_array) > 0:
            if self.catch_closest_:
                closest_turtle = None
                closest_turtle_distance = float('inf')
                for turtle in msg.turtle_array:
                    distance = sqrt((self.pose.x - turtle.x)**2 + (self.pose.y - turtle.y)**2)
                    if distance < closest_turtle_distance:
                        closest_turtle_distance = distance
                        closest_turtle = turtle
                self.target_turtle = closest_turtle # type: ignore
            else:
                self.target_turtle = msg.turtle_array[0] # type: ignore
    
    def update_position(self, msg: Pose):
        self.pose.x = msg.x
        self.pose.y = msg.y
        self.pose.theta = msg.theta

    def main_loop(self):
        if self.pose == None or self.target_turtle == None:
            return

        # Distance is calculated by using dist = root[(x1 - x2)^2 + (y1 - y2)^2] 
        distance = sqrt((self.pose.x - self.target_turtle.x)**2 + (self.pose.y - self.target_turtle.y)**2)
        # calculating turn amount
        turn_amount = atan2((self.target_turtle.y - self.pose.y), (self.target_turtle.x - self.pose.x))
        # diffrence of out theta and turn_amount
        turn_amount = turn_amount - self.pose.theta 
        # normalizing turn amount
        turn_amount = atan2(sin(turn_amount), cos(turn_amount))

        # publishing values
        cmd_vel = Twist()
        if distance > 0.5 :
            cmd_vel.angular.z = turn_amount*6
            cmd_vel.linear.x = distance*2
        elif distance <= 0.5:
            cmd_vel.angular.z = 0.0
            cmd_vel.linear.x = 0.0
            self.call_catch_turtle(self.target_turtle.name)
            self.target_turtle = None                                                    # type: ignore

        self.cmd_vel_publisher_.publish(cmd_vel)
    
    def call_catch_turtle(self, turtle_name):
            while not self.catch_client_.wait_for_service(1.0):
                self.get_logger().warn("WAITING FOR SERVER...... PLEASE INITIALIZE")

            request = TurtleCatch.Request()
            request.turtle = turtle_name

            future = self.catch_client_.call_async(request=request)
            # call the catch_turtle_callback when the service call completes
            future.add_done_callback(partial(self.catch_turtle_callback, turtle_name=turtle_name))
        
    def catch_turtle_callback(self, future, turtle_name):
        response: TurtleCatch.Response = future.result()
        if not response.success:
            self.get_logger().error(f"TURTLE{turtle_name} COULD NOT BE REMOVED")
        

def main(args=None):
    rclpy.init(args=args)
    node = TurtleControllerNode()
    rclpy.spin(node)
    rclpy.shutdown()
    
    
if __name__ == "__main__":
    main()
