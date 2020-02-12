from lib.robot import Robot
import sys

interactive = False
if len(sys.argv) > 0:
    if sys.argv[1] == "-i":
        interactive = True
robot = Robot(interactive)
robot.start()

