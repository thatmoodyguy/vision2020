# MIT License
# Copyright (c) 2019 JetsonHacks
# See license
# Using a CSI camera (such as the Raspberry Pi Version 2) connected to a
# NVIDIA Jetson Nano Developer Kit using OpenCV
# Drivers for the camera and OpenCV are included in the base image

import cv2
import numpy as np
import math
from FPS import FPS
from WebcamVideoStream import WebcamVideoStream
import imutils
import time

# gstreamer_pipeline returns a GStreamer pipeline for capturing from the CSI camera
# Defaults to 1280x720 @ 60fps
# Flip the image by setting the flip_method (most common values: 0 and 2)
# display_width and display_height determine the size of the window on the screen


last_target_coordinates = []

def gstreamer_pipeline(
    capture_width=1280,
    capture_height=720,
    display_width=1280,
    display_height=720,
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

def apply_hsv_filter(img, args):
	hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
	lower = (int(args[0]), int(args[2]), int(args[4]))
	upper = (int(args[1]), int(args[3]), int(args[5]))
	mask = cv2.inRange(hsv, lower, upper)
	return mask

def gaussian_blur(img):
	return cv2.GaussianBlur(img, (11, 11), 0)

def binary_threshold(img, args):
	min = int(args[0])
	max = int(args[1])
	return cv2.threshold(img, min, max, cv2.THRESH_BINARY)[1]

def erode(img, iterations):
	return cv2.erode(img, None, iterations=iterations)

def dilate(img, iterations):
	return cv2.dilate(img, None, iterations=iterations)

def find_contours(img):
	contours, _ = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
	targets = []
	for c in contours:
		ar = aspect_ratio(c)
		a = area(c)
		if a < 500:
			continue
		if ar > 0.8 and ar < 2.5:
			targets.append(c)
	return targets

def aspect_ratio(contour):
	_, _, w, h = bounding_rectangle(contour)
	return float(w) / h

def area(contour):
	return cv2.contourArea(contour)

def bounding_rectangle(contour):
	return cv2.boundingRect(contour)

def center_of_target(contour):
	rr = cv2.boundingRect(contour)

def get_goal_center(rr):
	box = cv2.boxPoints(rr)
	if distance_between(box[1], box[2]) > distance_between(box[2], box[3]):
		return midpoint(box[1], box[2])
	else:
		return midpoint(box[2], box[3])

def distance_between(point1, point2):
	dx = abs(point1[0] - point2[0])
	dy = abs(point1[1] - point2[1])
	return math.sqrt((dx**2) + (dy**2))

def midpoint(point1, point2):
	midx = int((point1[0] + point2[0]) / 2.0)
	midy = int((point1[1] + point2[1]) / 2.0)
	return midx, midy

def save_snapshot(frame, frametype):
    filename = "snapshots/snapshot-{}-{}.jpg".format(time.strftime("%Y%m%d-%H%M%S"), frametype)
    cv2.imwrite(filename, frame, [int(cv2.IMWRITE_JPEG_QUALITY), 90])

def show_camera():
    # To flip the image, modify the flip_method parameter (0 and 2 are the most common)
    print(gstreamer_pipeline(flip_method=0))
    vs = WebcamVideoStream(src=gstreamer_pipeline()).start()
    #cap = cv2.VideoCapture(gstreamer_pipeline(flip_method=0), cv2.CAP_GSTREAMER)
    fps = FPS().start()
    take_snapshot = True

    while True:
        _ = cv2.namedWindow("CSI Camera", cv2.WINDOW_AUTOSIZE)
        # Window
        while cv2.getWindowProperty("CSI Camera", 0) >= 0:
            original_img = vs.read()
            if take_snapshot:
                save_snapshot(original_img, "original")
                take_snapshot = False
            filter = (60,87,120,255,50,255)
            img = apply_hsv_filter(original_img, filter)
            img = erode(img, 1)
            img = dilate(img, 1)

            targets = find_contours(img)
            brColor = (255,255,255)
            for contour in targets:
                rr = cv2.minAreaRect(contour)
                pt = get_goal_center(rr)
                cv2.circle(original_img, pt, 6, brColor, 3)

            cv2.imshow("CSI Camera", original_img)
            # This also acts as
            keyCode = cv2.waitKey(30) & 0xFF
            # Stop the program on the ESC key
            if keyCode == 27:
                break

        fps.stop()
        print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
        print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

        cap.release()
        cv2.destroyAllWindows()
    else:
        print("Unable to open camera")


if __name__ == "__main__":
    show_camera()
