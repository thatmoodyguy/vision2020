import sys
import cv2
import traceback
import time
import threading
from multiprocessing import Process, Manager
from lib.video import StreamFactory, WebcamVideoStream

class StreamCamera():

	def __init__(self, robot, key, device_name, ndx):
		self.robot = robot
		self.width = robot.settings["cameras"]["stream"]["input_width"]
		self.height = robot.settings["cameras"]["stream"]["input_height"]
		self.fps = robot.settings["cameras"]["stream"]["input_fps"]
		self.output_width = robot.settings["cameras"]["stream"]["output_width"]
		self.output_height = robot.settings["cameras"]["stream"]["output_height"]
		self.output_fps = robot.settings["cameras"]["stream"]["output_fps"]
		self.key = key
		self.device_name = device_name
		self.process = None
		self.ndx = ndx
	
	def run_threaded(self):
		self.process = Process(target=self.run, args=(self.robot.live_camera_ndx,))
		self.process.start()

	def run(self, live_camera):
		output_stream = StreamFactory.output_stream(self)
		print("starting the stream...")
		input_stream = StreamFactory.get_streaming_stream(self).start()
		print('stream started')
		try:
			print("entering try block")
			while self.keep_running():
				frame = self.process_image(input_stream)
				if frame is None:
					continue
				if live_camera.value == self.ndx:
					cv2.putText(frame, "{} VIEW".format(self.key), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)
					frame = cv2.resize(frame, (self.output_width, self.output_height), cv2.INTER_AREA)
					output_stream.write(frame)
				# Check for keyboard interaction
				keyCode = cv2.waitKey(30) & 0xFF
				# Stop the program on the ESC key
				if keyCode == 27:
					break
			if self.interactive:
				fps.stop()
		except:
			print(traceback.format_exc())
		finally:
			input_stream.release()
			output_stream.release()

	def keep_running(self):
		return True

	def process_image(self, stream):
		return stream.read()



