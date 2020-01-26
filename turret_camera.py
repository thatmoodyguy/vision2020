import cv2
import numpy as np
from lib.video import StreamFactory, WebcamVideoStream, FPS
from lib import filters
from lib.comms import Comms
from lib.target import Target

class TurretCamera():

    def __init__(self, interactive_mode = False):
        self.camera_height = 20.0
        self.camera_vertical_pitch = 0.0
        self.camera_fov_degrees_x = 96.1
        self.camera_fov_degrees_y = 55.4
        self.flip_camera_mode = 0
        self.interactive = interactive_mode
        self.comms = Comms()

    def run(self):
        stream = StreamFactory.get_stream().start()
        if self.interactive:
            _ = cv2.namedWindow("CSI Camera", cv2.WINDOW_AUTOSIZE)
            fps = FPS().start()
        while self.keep_running():
            frame = self.read_and_process_image(stream)
            if self.interactive:
                cv2.imshow("CSI Camera", frame)
                # Check for keyboard interaction
                keyCode = cv2.waitKey(30) & 0xFF
                # Stop the program on the ESC key
                if keyCode == 27:
                    break
        if self.interactive:
            fps.stop()

        stream.release()

        if self.interactive:
            print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
            print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))
            cv2.destroyAllWindows()

    def keep_running():
        if self.interactive():
            cv2.getWindowProperty("CSI Camera", 0) >= 0
        else:
            True

    def read_and_process_image(self, stream):
        original_img = stream.read()

        filter = (60,87,120,255,50,255)
        img = filters.apply_hsv_filter(original_img, filter)
        img = filters.erode(img, 1)
        img = filters.dilate(img, 1)

        target = Target(img).acquire_target()

        if target.acquired == False:
            self.comms.send_no_target_message()
        else:
            self.comms.send_target_info_message(target)

        return target.annotated_image


if __name__ == "__main__":
    TurretCamera(True).run()

