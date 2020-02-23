import sys
import cv2
import traceback
import time
import numpy as np
from lib.video import StreamFactory, WebcamVideoStream, FPS
from lib import filters
from lib.comms import Comms
from lib.target import Target

class TurretCamera():

	def __init__(self, robot):
		self.robot = robot
		self.camera_height = 28.25
		self.camera_vertical_pitch = 25.0
		self.camera_fov_degrees_x = 96.1
		self.camera_fov_degrees_y = 55.4
		self.calibration_matrix = np.array([[766.03930116, 0.0,637.20361122],
 											[0.0, 764.7621599, 410.02183367],
 											[0.0, 0.0, 1.0]])
		self.calibration_distortion = np.array([-0.3502228, 0.16896179, -0.00040508, -0.00060941, -0.04960559])
		self.ideal_matrix = np.array([[765.44085693, 0.0, 636.70582847],
 										[0.0, 743.22351074, 398.47404206],
										[0.0, 0.0, 1.0]])
		self.flip_camera_mode = 0
		self.interactive = self.robot.interactive_mode
		if self.interactive:
			print("INTERACTIVE MODE!!!!!")
		else:
			print("RUNNING IN HEADLESS MODE!!!!!")
		self.comms = self.robot.comms
		mapx, mapy = self.calculate_dedistortion_map()
		self.dedistortion_map_x = mapx
		self.dedistortion_map_y = mapy

	def run(self):
		output_stream = StreamFactory.output_stream()
		print("starting the stream...")
		input_stream = StreamFactory.get_stream().start()
		print('stream started')
		fps = FPS()
		try:
			print("entering try block")
			if self.interactive:
				window = cv2.namedWindow("CSI Camera", cv2.WINDOW_AUTOSIZE)
				fps.start()
			while self.keep_running():
				frame = self.read_and_process_image(input_stream)
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

	def calculate_dedistortion_map(self):
		return cv2.initUndistortRectifyMap(self.calibration_matrix, 
											self.calibration_distortion, 
											None, 
											self.ideal_matrix, 
											(1280,720), 5)

	def read_and_process_image(self, stream):
		start_time = time.time()
		original_img = stream.read()

		filter = (60,87,120,255,50,255)
		img = filters.apply_hsv_filter(original_img, filter)
		img = filters.erode(img, 1)
		img = filters.dilate(img, 1)

		target = Target(self.robot, img, original_img)
		target.acquire_target()
		if target.acquired == False:
			self.comms.send_no_target_message(start_time)
		else:
			self.comms.send_target_info_message(target, start_time)
		#target.annotated_image = cv2.resize(target.annotated_image, (640,360))
		return target.annotated_image

if __name__ == "__main__":
	TurretCamera(True).run()

