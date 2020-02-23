# MIT License
# Copyright (c) 2019 JetsonHacks
# See license
# Using a CSI camera (such as the Raspberry Pi Version 2) connected to a
# NVIDIA Jetson Nano Developer Kit using OpenCV
# Drivers for the camera and OpenCV are included in the base image

import cv2
import numpy as np
import math
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

def save_snapshot(frame, cat):
    angle = input("input the angle (or q to quit):")
    if angle == "q":
        return False
    distance = input("input distance in inches:")
    filename = "snapshots/{}_{}_{}_{}.jpg".format(cat, angle, distance, time.strftime("%Y%m%d-%H%M%S"))
    cv2.imwrite(filename, frame, [int(cv2.IMWRITE_JPEG_QUALITY), 100])
    return True

def show_camera():
    # To flip the image, modify the flip_method parameter (0 and 2 are the most common)
    print(gstreamer_pipeline(flip_method=0))
    cap = cv2.VideoCapture(gstreamer_pipeline(flip_method=0), cv2.CAP_GSTREAMER)

    while True:
        window_handle = cv2.namedWindow("CSI Camera", cv2.WINDOW_AUTOSIZE)
        # Window
        while cv2.getWindowProperty("CSI Camera", 0) >= 0:
            _, original_img = cap.read()

            cv2.imshow("CSI Camera", original_img)
            # This also acts as
            keyCode = cv2.waitKey(30) & 0xFF
            # Stop the program on the ESC key, take snapshot on space bar
            if keyCode == 32:
                if save_snapshot(original_img, "measure"):
                    print("Snapshot taken at {}".format(time.strftime("%H%M%S")))
                else:
                    break
            if keyCode == 27:
                break

        cap.release()
        cv2.destroyAllWindows()
    else:
        print("Unable to open camera")


if __name__ == "__main__":
    show_camera()
