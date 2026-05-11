# SpellBot
An interactive robot robotic system that arranges colored letter blocks to spell user-defined words. This is the final project for CS150 Intro to ROS, Spring 2026, taught by Dr. Elaine Short.  
<img src="https://a.storyblok.com/f/169662/1125x1500/d81c866521/png-ur3e_01_r.png/m/fit-in/1072x1364" width="150"> <img src="https://www.turtlebot.com/assets/images/TurtleBot4_Header.png" width="250">

## Description  
The current project programs a robotic arm (specifically the [UR3e](https://www.universal-robots.com/products/ur3e/)) to pick up a target letter block and place it in a pre-determined place. Before that, the block would be delivered by a Turtlebot, which navigates itself to the robot arm. The system is interactive through its closed-loop sensing mechanism: the user places a letter block on a platform, the robot arm detects the block’s position using a camera, and then autonomously plans and executes the pick-up action and places the block accordingly.  

The The final form of the project includes an interactive page where users can instruct the specific word to rearrange into, using multiple blocks that enables forming a word. Please see TODOs below for more.  

## Folder structure  
Please see files from src/arm_setup/arm_setup for relevant nav2 and moveit/ur3e files. Please see each file's header for documentation.  
The camera publisher is the self-written node.  

## Installation  
Please make sure to calibrate the robot.  
```bash
colcon build --packages-select arm_setup --symlink-install
source /opt/ros/kilted/setup.bash  
```
Download or clone the package arm_setup before building + sourcing it.  
```bash
python3 wayfinding.py  
ros2 launch arm_setup main.launch.py
```
Run the above files / launch files respectively to run the turtlebot and the robot arm. 

## Workflow (ROS nodes)   
Turtlebot (Nav2): mapping via Nav2 -> save map and start / finish coordinates from rviz  
Robot arm (Ur3e): Camera sensors -> pixels from image -> coordinates of block through pixels -> motion planning to pick up item from item cooredinates -> send action goal to robot arm -> repeat.  

## Demonstration  
TBD

## Libraries  
This project uses the [Robot Operating System 2 (ROS2)](https://www.ros.org/) and its affiliated libraries. Such as  
[Moveit](https://moveit.ai/) for motion planning and action goals  
[Nav2](https://docs.nav2.org/)  for Turtle bot  
OpenCV for computer vision  
Smach for high level state machine  

## Acknowledgements  
Robotics teaching lab staff for robot and rosbridge documentations <3  
The camera publisher is implemented by hand.  
Color recognition is inspired by this repository on Github.  

## TODOs  
- create userinterface
- allow multiple blocks / color recognition  
