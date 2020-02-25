import os
import sys
import subprocess
import threading
import yaml
from lib.turret_camera import TurretCamera
from lib.stream_camera import StreamCamera
from lib.comms import Comms
from multiprocessing import Value

class Robot():
	def __init__(self,interactive_mode=False):
		self.turret_camera = None
		self.front_camera = None
		self.rear_camera = None
		self.udp_inbound_command_port = 5800
		self.udp_outbound_data_host = "10.45.13.2"
		self.udp_outbound_data_port = 5801
		self.udp_outbound_video_host = "127.0.0.1"
		self.udp_outbound_video_port = 5802
		self.take_snapshot_now = False
		self.interactive_mode = interactive_mode
		self.settings = None
		self.live_camera_ndx = Value('i', 0) 
	
	def start(self):
		self.load_settings()
		self.comms = Comms(self)
		self.comms.init_udp_thread()
		self.comms.send_udp_message_to_robot("UDP PING!")
		self.set_live_camera("TURRET")
		self.init_cameras()

	def set_live_camera(self, key):
		if key == "TURRET":
			ndx = 0
		elif key == "FRONT":
			ndx = 1
		elif key == "REAR":
			ndx = 2
		else:
			return False
		self.live_camera_ndx.value = ndx

	def load_settings(self):
		with open(os.path.join(sys.path[0], "config.yml"), "r") as ymlfile:
			self.settings = yaml.safe_load(ymlfile)

		self.udp_inbound_command_port = self.settings['robot']['udp_inbound_command_port']
		self.udp_outbound_data_host = self.settings['robot']['udp_outbound_host']
		self.udp_outbound_data_port = self.settings['robot']['udp_outbound_port']
		self.udp_outbound_video_host = self.settings['robot']['udp_outbound_video_host']
		self.udp_outbound_video_port = self.settings['robot']['udp_outbound_video_port']

	def init_cameras(self):
		devices = self.camera_devices()

		self.turret_camera = TurretCamera(self)
		self.turret_camera.run_threaded()
		print("turret camera thread started")

		front_serial = self.settings['cameras']['front']['serial']
		front_camera_def = devices.get(front_serial)
		if front_camera_def is None:
			print("WARNING: No front camera found")
		else:
			self.front_camera = StreamCamera(self, "FRONT", front_camera_def["device_name"], 1)
			self.front_camera.run_threaded()

		rear_serial = self.settings['cameras']['rear']['serial']
		rear_camera_def = devices.get(rear_serial)
		if rear_camera_def is None:
			print("WARNING: No rear camera found")
		else:
			self.rear_camera = StreamCamera(self, "REAR", rear_camera_def["device_name"], 2)
			self.rear_camera.run_threaded()
		print("cameras running")

	def camera_devices(self):
		devices = {}
		for i in range(0,6):
			device_name = "/dev/video{}".format(str(i))
			serial_number = self.value_from_udev(device_name, "ID_SERIAL_SHORT")
			if len(serial_number) > 2 and devices.get(serial_number) is None:
				devices[serial_number] = {"device_name": device_name, "serial_number": serial_number}
		print("devices found: {}".format(devices))
		return devices

	def value_from_udev(self, device_name, key):
		cmd = "udevadm info --query=property {} | grep {}".format(device_name, key)
		value = ""
		try:
			value = subprocess.check_output(cmd, shell = True)
			value = value.decode().strip().split("=")[1]
		except:
			return ""
		return value