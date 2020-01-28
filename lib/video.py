from threading import Thread
import cv2
import datetime
import time

class StreamFactory:
    @classmethod
    def get_stream(cls, flip_method=0):
        return WebcamVideoStream(src=cls.gstreamer_pipeline(flip_method=0)).start()

    @classmethod
    def output_stream(cls):
      framerate = 30
      return cv2.VideoWriter('appsrc ! videoconvert ! '
                      'x264enc noise-reduction=10000 speed-preset=ultrafast tune=zerolatency ! '
                      'rtph264pay config-interval=1 pt=96 !'
                      'udpsink host=10.45.13.118 port=5000',
                      0, framerate, (1280, 720))
    
    @classmethod
    def gstreamer_pipeline(cls,
        capture_width=1280,
        capture_height=720,
        display_width=1280,
        display_height=720,
        framerate=60,
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
            "video/x-raw, format=(string)BGR ! appsink"
            % (
                capture_width,
                capture_height,
                framerate,
                flip_method,
                display_width,
                display_height
            )
        )

class WebcamVideoStream:
	def __init__(self, src=0):
		# initialize the video camera stream and read the first frame
		# from the stream
		self.stream = cv2.VideoCapture(src, cv2.CAP_V4L)
		time.sleep(1)
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
