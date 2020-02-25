import time
import threading
from lib.udp import UdpCommandListener
from lib.udp import UdpSender

class Comms():
	def __init__(self, robot):
		self.robot = robot
		self.udp_listener_thread = None
		self.udp_sender = UdpSender(self.robot.udp_outbound_data_host, self.robot.udp_outbound_data_port)

	def send_target_info_message(self, target, start_time):
		self.send_message(
			"TURRET",
			"target=T bearing-x={:.2f} bearing-y={:.2f} base_range={:.2f} slope={:.6f} x-pos={} y-pos={}".format(target.bearing_x, target.bearing_y, target.base_range, 
				target.goal_slope, target.target_coordinates[0], target.target_coordinates[1]),
			start_time
		)

	def send_no_target_message(self,start_time):
		self.send_message(
			"TURRET",
			"target=F",
			start_time
		)

	def send_message(self, subject, message, start_time):
		end_time = time.time()
		latency = end_time - start_time
		msg = "{} {} time={} latency={}".format(subject, message, time.time(), latency)
		#print("--> {}:{} UDP: {}".format(self.robot.udp_outbound_data_host, self.robot.udp_outbound_data_port, msg))
		self.send_udp_message_to_robot(msg)

	def init_udp_thread(self):
		if self.udp_listener_thread is None:
			self.udp_listener_thread = threading.Thread(target=self.listen_on_udp)
			print("starting thread")
			self.udp_listener_thread.start()

	def listen_on_udp(self):
		udp = UdpCommandListener("0.0.0.0", self.robot.udp_inbound_command_port, self)
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
		if cmd == "TURRET" and not self.robot.turret_camera is None:
			self.robot.set_live_camera("TURRET")
		if cmd == "FRONT" and not self.robot.front_camera is None:
			print("switching camera to front")
			self.robot.set_live_camera("FRONT")
		elif cmd == "REAR" and not self.robot.rear_camera is None:
			self.robot.set_live_camera("REAR")
		elif cmd == "SNAPSHOT":
			self.take_snapshot_now = True
		else:
			print("No action taken")
		return "OK"