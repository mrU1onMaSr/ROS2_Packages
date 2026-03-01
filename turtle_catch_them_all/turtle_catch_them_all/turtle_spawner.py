#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from turtlesim.srv import Spawn, Kill
from random import uniform
from functools import partial
from my_robot_interfaces.msg import TurtleArray, Turtle
from my_robot_interfaces.srv import TurtleCatch
    
class TurtleSpawnerNode(Node):
    def __init__(self):
        super().__init__("turtle_spawner")

        # init params
        self.declare_parameter("spawn_frequency", 1.0)
        self.spawn_frequency: float = self.get_parameter("spawn_frequency").get_parameter_value().double_value

        self.declare_parameter("turtle_name_prefix","turtle_")
        self.name_prefix: str = self.get_parameter("turtle_name_prefix").value # type: ignore

        # init clients, servers, publishers, subscribers
        self.spawn_client_ = self.create_client(Spawn, "/spawn")
        self.kill_client_ = self.create_client(Kill, "/kill")
        self.turtle_publisher_ = self.create_publisher(TurtleArray, "alive_turtles", 10)
        self.catch_server_ = self.create_service(TurtleCatch, "catch_turtle", self.call_catch_turtle) # type: ignore

        # init timer
        self.timer_ = self.create_timer(self.spawn_frequency, self.call_spawn)

        # init message
        self.get_logger().info("SPAWER IS RUNNING")

        # init vars
        self.turtle_number_ = 1
        self.turtle_list_: list[Turtle] = []
    
    def call_catch_turtle(self, request: TurtleCatch.Request, response: TurtleCatch.Response):
        self.call_kill_turtle(request.turtle)
        response.success = True
        return response


    def call_spawn(self):
        # wait for server
        while not self.spawn_client_.wait_for_service(1.0):
            self.get_logger().warn("WAITING FOR SERVER...... PLEASE INITIALIZE")

        # create random positon for turtle
        spawn_x = uniform(0.0, 11.0)
        spawn_y = uniform(0.0, 11.0)
        spawn_theta = uniform(0.0, 6.28)

        # create name for turtle
        self.turtle_number_ += 1
        spawn_name = self.name_prefix + str(self.turtle_number_)
        
        # spawn turtle
        self.spawn_turtles(spawn_x, spawn_y, spawn_theta, spawn_name)


    def spawn_turtles(self, x, y, theta, name):
        spawn = Spawn.Request()
        spawn.x = x
        spawn.y = y
        spawn.theta = theta
        spawn.name = name
        future = self.spawn_client_.call_async(spawn)
        future.add_done_callback(partial(self.callback_spawn, request=spawn))
    

    def callback_spawn(self, future, request: Spawn.Request):
        response: Spawn.Response = future.result()
        if response.name != "":   
            #self.get_logger().info(f"{response.name} HAS BEEN CREATED")
            new_turtle = Turtle()
            new_turtle.name = request.name
            new_turtle.x = request.x
            new_turtle.y = request.y
            new_turtle.theta = request.theta
            self.turtle_list_.append(new_turtle)
            self.publish_turtles()
    

    def publish_turtles(self):
        turtles = TurtleArray()
        turtles.turtle_array = self.turtle_list_
        self.turtle_publisher_.publish(turtles)


    def call_kill_turtle(self, turtle_name):
        while not self.kill_client_.wait_for_service(1.0):
            self.get_logger().warn("WAITING FOR SERVER...... PLEASE INITIALIZE")

        request = Kill.Request()
        request.name = turtle_name

        future = self.kill_client_.call_async(request=request)
        future.add_done_callback(partial(self.kill_turtle_callback, turtle_name=turtle_name))
    
    def kill_turtle_callback(self, future, turtle_name):
        
        for (i, turtle) in enumerate(self.turtle_list_):
            if turtle.name == turtle_name:
                del self.turtle_list_[i]
                self.publish_turtles()
                break
                

def main(args=None):
    rclpy.init(args=args)
    node = TurtleSpawnerNode()
    rclpy.spin(node)
    rclpy.shutdown()
    
    
if __name__ == "__main__":
    main()
