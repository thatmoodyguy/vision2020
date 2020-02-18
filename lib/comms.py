from lib.udp import UdpSender
import time

class Comms():
    def __init__(self, robot):
        self.robot = robot
        
    def send_target_info_message(self, target, start_time):
        self.send_message(
            "TURRET",
            "1\t{:.2f}\t{:.2f}\t{:.2f}\t{:.6f}".format(target.bearing_x, target.bearing_y, target.base_range, target.goal_slope),
            start_time
        )

    def send_no_target_message(self,start_time):
        self.send_message(
            "TURRET",
            "0",
            start_time
        )

    def send_message(self, subject, message, start_time):
        end_time = time.time()
        latency = end_time - start_time
        msg = "{:.4f}\t{:.4f}\t{}\t{}".format(latency, time.time(), subject, message)
        print(msg)
        #TODO: send via udp