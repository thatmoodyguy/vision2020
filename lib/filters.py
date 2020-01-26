import cv2
import numpy

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