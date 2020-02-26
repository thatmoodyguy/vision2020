from threading import Thread
import cv2
import datetime
import time

class StreamFactory:
		@classmethod
		def get_stream(cls, camera, flip_method):
			gstream = cls.gstreamer_pipeline(flip_method=flip_method, width=camera.width, height=camera.height, framerate=camera.fps)
			print("Input Stream: {}".format(gstream))
			return WebcamVideoStream(src=gstream)
		
		@classmethod
		def get_streaming_stream(cls, camera):
			return WebcamVideoStream(src=camera.device_name, cap=cv2.CAP_V4L2, width=camera.width, height=camera.height)

		@classmethod
		def output_stream(cls, camera):
			framerate = camera.output_fps
			host = camera.robot.udp_outbound_video_host
			port = camera.robot.udp_outbound_video_port
			return cv2.VideoWriter('appsrc ! videoconvert ! '
											'omxh264enc control-rate=2 bitrate=1500000 ! '
											'video/x-h264, stream-format=byte-stream ! '
											'rtph264pay mtu=1400 ! '
											'udpsink host={} port={}'.format(host,port),
											0, framerate, (camera.output_width, camera.output_height))
		
		@classmethod
		def gstreamer_pipeline(cls,
				width=1280,
				height=720,
				framerate=30,
				flip_method=0,
		):
				return (
						"nvarguscamerasrc wbmode=0 ee-mode=0 aeantibanding=0 aelock=true exposuretimerange=\"5000000 5000000\" ! "
						"video/x-raw(memory:NVMM), "
						"width=(int)%d, height=(int)%d, "
						"format=(string)NV12, framerate=(fraction)%d/1 ! "
						"nvvidconv flip-method=%d ! "
						"video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! "
						"videoconvert ! "
						"video/x-raw, format=(string)BGR ! appsink drop=true max-buffers=1"
						% (
								width,
								height,
								framerate,
								flip_method,
								width,
								height
						)
				)

		@classmethod
		def v4l2_gstreamer_pipeline(cls,
				width=640,
				height=480,
				framerate=30,
				device_name="/dev/video1",
		):
				return (
						("v4l2src device={} ! "
						"'video/x-raw, width=(int)%d, height=(int)%d, framerate=(fraction)%d/1, format=(string)I420' ! "
						"videoconvert ! "
						"appsink maxbuffers=1 drop=true"
						).format(
								device_name, 
								width,
								height,
								framerate,
								width,
								height
						)
				)

class WebcamVideoStream:
	def __init__(self, src=0, cap = cv2.CAP_GSTREAMER, width=0, height=0):
		print(src)
		# initialize the video camera stream and read the first frame
		# from the stream
		self.stream = cv2.VideoCapture(src, cap)
		if width > 0:
			#self.stream.set(cv2.CAP_PROP_FOURCC, cv2.FOURCC('M', 'J', 'P', 'G'))
			self.stream.set(cv2.CAP_PROP_FRAME_WIDTH, width)
			self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

		if self.stream.isOpened():
			(self.grabbed, self.frame) = self.stream.read()

		# initialize the variable used to indicate if the thread should
		# be stopped
		self.stopped = False

	def start(self):
		# start the thread to read frames from the video stream
		Thread(target=self.update, args=()).start()
		return self

	def release(self):
		if not self.stream is None:
			self.stream.release()

	def update(self):
		# keep looping infinitely until the thread is stopped
		while True:
			# if the thread indicator variable is set, stop the thread
			if self.stopped:
				return

			# otherwise, read the next frame from the stream
			(self.grabbed, self.frame) = self.stream.read()

	def read(self):
		# return the frame most recently read
		return self.frame

	def stop(self):
		# indicate that the thread should be stopped
		self.stopped = True

class FPS:
	def __init__(self):
		# store the start time, end time, and total number of frames
		# that were examined between the start and end intervals
		self._start = None
		self._end = None
		self._numFrames = 0

	def start(self):
		# start the timer
		self._start = datetime.datetime.now()
		return self

	def stop(self):
		# stop the timer
		self._end = datetime.datetime.now()

	def update(self):
		# increment the total number of frames examined during the
		# start and end intervals
		self._numFrames += 1

	def elapsed(self):
		# return the total number of seconds between the start and
		# end interval
		return (self._end - self._start).total_seconds()

	def fps(self):
		# compute the (approximate) frames per second
		return self._numFrames / self.elapsed()


