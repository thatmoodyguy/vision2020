import sys
import cv2
import traceback
import time
import threading
from multiprocessing import Process
import numpy as np
from lib.video import StreamFactory, WebcamVideoStream, FPS
from lib import filters
from lib.comms import Comms
from lib.target import Target

class TurretCamera():

	def __init__(self, robot):
		self.robot = robot
		self.process = None
		self.camera_height = robot.settings["robot"]["turret_camera_height"]
		self.camera_vertical_pitch = robot.settings["robot"]["turret_camera_vertical_pitch"]
		self.camera_fov_degrees_x = robot.settings["cameras"]["turret"]["fov_degrees_x"]
		self.camera_fov_degrees_y = robot.settings["cameras"]["turret"]["fov_degrees_y"]
		self.flip_camera_mode = 0
		self.comms = None
		self.width = robot.settings["cameras"]["turret"]["input_width"]
		self.height = robot.settings["cameras"]["turret"]["input_height"]
		self.fps = robot.settings["cameras"]["turret"]["input_fps"]
		self.output_width = robot.settings["cameras"]["turret"]["output_width"]
		self.output_height = robot.settings["cameras"]["turret"]["output_height"]
		self.output_fps = robot.settings["cameras"]["turret"]["output_fps"]
		self.interactive = self.robot.interactive_mode
		self.key = "TURRET"
		self.ndx = 0
		self.last_coords = []
		self.last_target_at = 0
		if self.interactive:
			print("INTERACTIVE MODE!!!!!")
		else:
			print("RUNNING IN HEADLESS MODE!!!!!")

	def run_threaded(self):
		self.process = Process(target=self.run, args=(self.robot.live_camera_ndx,))
		self.process.start()

	def run(self, live_camera):
		self.comms = Comms(self.robot)
		output_stream = StreamFactory.output_stream(self)
		print("starting the stream...")
		input_stream = StreamFactory.get_stream(self, 2).start()
		print('stream started')
		fps = FPS()
		try:
			print("entering try block")
			if self.interactive:
				window = cv2.namedWindow("CSI Camera", cv2.WINDOW_AUTOSIZE)
				fps.start()
			while self.keep_running():
				frame = self.read_and_process_image(input_stream)
				if frame is None:
					continue
				if live_camera.value == self.ndx:
					output_stream.write(frame)
				if self.interactive:
					cv2.imshow("CSI Camera", frame)
					# Check for keyboard interaction
					keyCode = cv2.waitKey(30) & 0xFF
					# Stop the program on the ESC key
					if keyCode == 27:
						break
			if self.interactive:
				fps.stop()
				print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
				print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))
		except:
			print(traceback.format_exc())
		finally:
			input_stream.release()
			output_stream.release()

		if self.interactive:
			cv2.destroyAllWindows()

	def keep_running(self):
		if self.interactive:
			return cv2.getWindowProperty("CSI Camera", 0) >= 0
		else:
			return True

	def read_and_process_image(self, stream):
		start_time = time.time()
		original_img = stream.read()
		if original_img is None:
			return None;
		
		filter = (60,87,120,255,50,255)
		img = filters.apply_hsv_filter(original_img, filter)
		img = filters.erode(img, 1)
		img = filters.dilate(img, 1)

		target = Target(self.robot, img, original_img, self)
		target.acquire_target()
		if target.acquired == False:
			self.comms.send_no_target_message(start_time)
		else:
			self.comms.send_target_info_message(target, start_time)
		if self.width != self.output_width or self.height != self.output_height:
			target.annotated_image = cv2.resize(target.annotated_image, (self.output_width, self.output_height))
		return target.annotated_image


