import os
import sys
import subprocess
import threading
import yaml
from lib.turret_camera import TurretCamera
from lib.udp import UdpCommandListener
from lib.udp import UdpSender
from lib.comms import Comms



class Robot():
	def __init__(self,interactive_mode=False):
		self.turret_camera = None
		self.udp_listener_thread = None
		self.udp_inbound_command_port = 5800
		self.udp_outbound_data_host = "10.45.13.2"
		self.udp_outbound_data_port = 5801
		self.udp_outbound_video_host = "127.0.0.1"
		self.udp_outbound_video_port = 5802
		self.udp_sender = None
		self.take_snapshot_now = False
		self.interactive_mode = interactive_mode
		self.settings = None
	
	def start(self):
		self.comms = Comms(self)
		self.load_settings()
		self.init_udp_thread()
		self.turret_camera = TurretCamera(self)
		self.turret_camera.run()

	def load_settings(self):
		with open(os.path.join(sys.path[0], "config.yml"), "r") as ymlfile:
			self.settings = yaml.safe_load(ymlfile)
		


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
