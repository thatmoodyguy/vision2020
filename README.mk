# Vision2020
## Testing for FRC 2020 season

## Useful websites
- [Chessboard calibration technique](https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_calib3d/py_calibration/py_calibration.html)
- [OpenCV threading technique](https://www.pyimagesearch.com/2015/12/21/increasing-webcam-fps-with-python-and-opencv/)

## Current plan
- Determine POV of camera
- Get video streaming
- Set up app structure
- Calculate target coordinates
- Stream target coordinates via UDP
-
gst-launch-1.0 udpsrc port=5802 ! application/x-rtp,encoding-name=H264,payload=96 ! rtph264depay ! h264parse ! queue ! avdec_h264 ! xvimagesink sync=false async=false -e
