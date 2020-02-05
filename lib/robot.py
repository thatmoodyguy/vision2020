from turret_camera import TurretCamera
from udp import UdpCommandListener
from udp import UdpSender
import subprocess
import threading

class Robot():
	def __init__(self):
		self.turret_camera = None
		self.udp_listener_thread = None
		self.udp_inbound_command_port = 5800
		self.udp_outbound_host = "10.45.13.2"
		self.udp_outbount_port = 5801
		self.udp_sender = None
		self.take_snapshot_now = False
	
	def startup(self):

	def init_udp_thread(self):
        if self.udp_listener_thread is None:
            self.udp_listener_thread = threading.Thread(target=self.listen_on_udp)
            print("starting thread")
            self.udp_listener_thread.start()

    def listen_on_udp(self):
        udp = UdpCommandListener("0.0.0.0", self.udp_inbound_command_port, self)
        print("listening to udp")
        udp.start()

    def send_udp_message_to_robot(self, message):
        self.udp_sender.send(message.encode("utf-8"))

	def process_udp_command(self, data):
		cmds = data.decode("utf-8").upper().split()
        if len(cmds) == 0:
            return "OK"
        cmd = cmds.pop(0)
        print("UDP received command: {}".format(cmd))
        if cmd == "FRONT" and not self.front_camera is None:
            self.live_camera = self.front_camera
        elif cmd == "REAR" and not self.rear_camera is None:
            self.live_camera = self.rear_camera
        elif cmd == "SNAPSHOT":
            self.take_snapshot_now = True
        return "OK"




if __name__ == "__main__":
    Robot().start()
