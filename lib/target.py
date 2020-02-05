import cv2

def contour_sort(e):
    return cv2.contourArea(e)

class Target():
    def __init__(self, image, original_image):
        self.image = image
        self.original_image = original_image
        self.annotated_image = original_image
        self.acquired = False
        self.contour = None

    def acquire_target(self):
        print("starting target acquisition")
        contours = self.find_potential_targets(self.image)
        if len(contours) == 0:
            self.acquired = False
            self.contour = None
        else:
            self.acquired = True
            self.contour = contours[0]
            #TODO:  calculate and send stats
            #TODO:  annotate the image with target markings!
        
    def find_potential_targets(self, img):
        contours, _ = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        targets = []
        for c in contours:
            ar = self.aspect_ratio(c)
            a = self.area(c)
            if a < 500:
                continue
            if ar > 0.8 and ar < 2.5:
                targets.append(c)
        return targets

    def aspect_ratio(self, contour):
        _, _, w, h = self.bounding_rectangle(contour)
        return float(w) / h

    def area(self, contour):
        return cv2.contourArea(contour)

    def bounding_rectangle(self, contour):
        return cv2.boundingRect(contour)

    def center_of_vision_target(self,contour):
        rr = cv2.boundingRect(contour)

    def get_goal_center(self,contour):
        box = cv2.boxPoints(cv2.minAreaRect(contour))
        if self.distance_between(box[1], box[2]) > self.distance_between(box[2], box[3]):
            return midpoint(box[1], box[2])
        else:
            return midpoint(box[2], box[3])

    def distance_between(self, point1, point2):
        dx = abs(point1[0] - point2[0])
        dy = abs(point1[1] - point2[1])
        return math.sqrt((dx**2) + (dy**2))

    def midpoint(self, point1, point2):
        midx = int((point1[0] + point2[0]) / 2.0)
        midy = int((point1[1] + point2[1]) / 2.0)
        return midx, midy

    def bearing(self):
        target_x = self.target_coordinates[0]
        center_x = self.image_width / 2.0
        if target_x == center_x:
            return 0.0
        pixels_off = abs(center_x - target_x)
        heading_abs = self.turret_camera.camera_fov_degrees_x * float(pixels_off) / self.image_width
        if target_x < center_x:
            return heading_abs * -1.0
        else:
            return heading_abs

    def range(self):
        target_y = self.target_coordinates[1]
        center_y = self.image_height / 2.0
        offset_in_pixels = center_y - target_y
        print("vertical pixel offset: {}".format(offset_in_pixels))
        vertical_angle = (offset_in_pixels * self.turret_camera.camera_fov_degrees_y) / self.image_height
        print("vertical angle: {}".format(vertical_angle))
        outer_goal_center_height_inches = 98.25
        camera_height = 24.125
        vertical_offset_inches = abs(outer_goal_center_height_inches - camera_height)
        distance = abs(vertical_offset_inches / (math.tan(math.radians(vertical_angle))))
        return distance