import os
import sys
import subprocess
import threading
import yaml
from lib.turret_camera import TurretCamera
from lib.comms import Comms

class Robot():
	def __init__(self,interactive_mode=False):
		self.turret_camera = None

		self.udp_inbound_command_port = 5800
		self.udp_outbound_data_host = "10.45.13.2"
		self.udp_outbound_data_port = 5801
		self.udp_outbound_video_host = "127.0.0.1"
		self.udp_outbound_video_port = 5802
		self.take_snapshot_now = False
		self.interactive_mode = interactive_mode
		self.settings = None
	
	def start(self):
		self.load_settings()
		self.comms = Comms(self)
		self.comms.init_udp_thread()
		self.turret_camera = TurretCamera(self)
		self.turret_camera.run()

	def load_settings(self):
		with open(os.path.join(sys.path[0], "config.yml"), "r") as ymlfile:
			self.settings = yaml.safe_load(ymlfile)

		self.udp_inbound_command_port = self.settings['robot']['udp_inbound_command_port']
		self.udp_outbound_data_host = self.settings['robot']['udp_outbound_host']
		self.udp_outbound_data_port = self.settings['robot']['udp_outbound_port']
		self.udp_outbound_video_host = self.settings['robot']['udp_outbound_video_host']
		self.udp_outbound_video_port = self.settings['robot']['udp_outbound_video_port']







if __name__ == "__main__":
	Robot().start()
