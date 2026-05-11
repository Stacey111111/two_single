#!/usr/bin/env python3
"""
New Gesture Controller - For fist and ok gestures only

Functions:
  fist  -> Zigzag pattern movement
  ok    -> Circle movement

Author: Your Name
Date: 2026-05-08
"""

import time
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import Twist


class NewGestureController(Node):
    """
    New gesture controller
    Handles only fist and ok gestures
    """

    def __init__(self):
        super().__init__("new_gesture_controller")
        
        # Subscribe to gesture commands
        self.subscription = self.create_subscription(
            String,
            "/gesture/command",
            self.command_callback,
            10
        )
        
        # Publish velocity commands
        self.cmd_pub = self.create_publisher(
            Twist,
            "/cmd_vel",
            10
        )
        
        # State tracking
        self.last_command = ""
        self.is_executing = False  # Prevent action overlap
        
        self.get_logger().info("="*60)
        self.get_logger().info("New Gesture Controller Started!")
        self.get_logger().info("="*60)
        self.get_logger().info("Supported gestures:")
        self.get_logger().info("  fist  -> Zigzag pattern")
        self.get_logger().info("  ok    -> Circle movement")
        self.get_logger().info("="*60)

    def stop_robot(self):
        """
        Stop the robot
        """
        twist = Twist()
        twist.linear.x = 0.0
        twist.angular.z = 0.0
        self.cmd_pub.publish(twist)

    def zigzag_movement(self):
        """
        Zigzag movement pattern
        
        Movement pattern:
          Forward+Left -> Forward+Right -> Forward+Left -> ...
        """
        self.get_logger().info("Executing zigzag pattern!")
        
        self.is_executing = True
        
        try:
            # Parameters
            linear_speed = 0.12   # Forward speed m/s
            angular_speed = 0.4   # Turn speed rad/s
            duration = 1.0        # Duration per segment (seconds)
            cycles = 3            # Number of zigzag cycles
            
            for i in range(cycles):
                self.get_logger().info(f"  Zigzag {i+1}/{cycles}")
                
                # Segment 1: Forward + Turn left
                twist = Twist()
                twist.linear.x = linear_speed
                twist.angular.z = angular_speed  # Positive = left turn
                
                start_time = time.time()
                while time.time() - start_time < duration:
                    self.cmd_pub.publish(twist)
                    time.sleep(0.1)
                
                # Segment 2: Forward + Turn right
                twist = Twist()
                twist.linear.x = linear_speed
                twist.angular.z = -angular_speed  # Negative = right turn
                
                start_time = time.time()
                while time.time() - start_time < duration:
                    self.cmd_pub.publish(twist)
                    time.sleep(0.1)
            
            # Stop at the end
            self.stop_robot()
            
            self.get_logger().info("Zigzag complete!")
            
        except Exception as e:
            self.get_logger().error(f"Zigzag movement error: {e}")
            self.stop_robot()
        
        finally:
            self.is_executing = False

    def circle_movement(self):
        """
        Circle movement pattern
        
        Movement pattern:
          Continuous forward + Continuous left turn = Circle
        """
        self.get_logger().info("Executing circle movement!")
        
        self.is_executing = True
        
        try:
            # Parameters
            linear_speed = 0.12   # Forward speed m/s
            angular_speed = 0.5   # Turn speed rad/s (determines circle size)
            duration = 6.3        # Duration (seconds) - approximately one circle
            
            # Calculate circle radius (approximate)
            # radius approximately equals linear_speed / angular_speed
            radius = linear_speed / angular_speed
            self.get_logger().info(f"  Circle radius approximately {radius:.2f} m")
            
            # Draw circle continuously
            twist = Twist()
            twist.linear.x = linear_speed
            twist.angular.z = angular_speed  # Continuous left turn
            
            start_time = time.time()
            while time.time() - start_time < duration:
                self.cmd_pub.publish(twist)
                time.sleep(0.1)
            
            # Stop
            self.stop_robot()
            
            self.get_logger().info("Circle complete!")
            
        except Exception as e:
            self.get_logger().error(f"Circle movement error: {e}")
            self.stop_robot()
        
        finally:
            self.is_executing = False

    def command_callback(self, msg):
        """
        Gesture command callback
        
        Receives gesture commands and executes corresponding actions
        """
        command = msg.data.lower()
        
        # Ignore duplicate commands
        if command == self.last_command:
            return
        
        # Ignore new commands while executing
        if self.is_executing:
            self.get_logger().warn(f"Currently executing, ignoring command: {command}")
            return
        
        self.last_command = command
        
        self.get_logger().info(f"Received command: {command}")
        
        # Process gesture commands
        if command == "fist":
            # Fist gesture -> Zigzag
            self.zigzag_movement()
            
        elif command == "ok":
            # OK gesture -> Circle
            self.circle_movement()
            
        else:
            # Ignore other commands
            self.get_logger().debug(f"Unknown command (ignored): {command}")


def main(args=None):
    """
    Main function
    """
    rclpy.init(args=args)
    
    node = NewGestureController()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("Received exit signal")
    finally:
        node.stop_robot()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
