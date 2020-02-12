from lib.udp import UdpSender
import time

class Comms():
    def __init__(self, robot):
        self.robot = robot
        
    def send_target_info_message(self, target):
        self.send_message(
            "TURRET",
            "1\t{:.2f}\t{:.2f}\t{:.2f}\t{:.6f}".format(target.bearing_x, target.bearing_y, target.base_range, target.goal_slope)
        )

    def send_no_target_message(self):
        self.send_message(
            "TURRET",
            "0"
        )

    def send_message(self, subject, message):
        msg = "{:.4f}\t{}\t{}".format(time.time(), subject, message)
        print(msg)
        #TODO: send via udp