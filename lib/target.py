import cv2
import math

def contour_sort(e):
    return cv2.contourArea(e)

class Target():
    def __init__(self, robot, image, original_image):
        self.image = image
        self.original_image = original_image
        self.annotated_image = original_image
        self.acquired = False
        self.contour = None
        self.bearing_x = 0.0
        self.bearing_y = 0.0
        self.base_range = 0.0
        self.goal_slope = 0.0
        self.robot = robot
        self.image_width = robot.turret_camera.width
        self.image_height = robot.turret_camera.height

    def acquire_target(self):
        contours = self.find_potential_targets(self.image)
        if len(contours) == 0:
            self.acquired = False
            self.contour = None
        else:
            self.acquired = True
            self.contour = contours[0]
            top_points = self.calc_goal_top_points(self.contour)
            self.target_coordinates = self.calc_goal_center(top_points)
            self.bearing_x = self.calc_bearing_x()
            self.bearing_y = self.calc_bearing_y()
            self.goal_slope = self.calc_goal_slope(top_points)
            self.base_range = self.calc_base_range(self.bearing_y)

            cv2.circle(self.annotated_image, self.target_coordinates, 6, (255,255,0), 3)
            x = int(self.image_width / 2)
            cv2.line(self.annotated_image, (x,0), (x, self.image_height), (255,255,255), 2)
            cv2.putText(self.annotated_image, "TURRET VIEW", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)
        
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

    def calc_goal_top_points(self, contour):
        box = cv2.boxPoints(cv2.minAreaRect(contour))
        if self.distance_between(box[1], box[2]) > self.distance_between(box[2], box[3]):
            return [box[1], box[2]]
        else:
            return [box[2], box[3]]
    
    def calc_goal_center(self,top_points):
        return self.midpoint(top_points)

    def calc_goal_slope(self, points):
        dx = points[1][0] - points[0][0]
        dy = points[1][1] - points[0][1]
        if dx != 0:
            return (dy / dx)
        return 0

    def distance_between(self, point1, point2):
        dx = abs(point1[0] - point2[0])
        dy = abs(point1[1] - point2[1])
        return math.sqrt((dx**2) + (dy**2))

    def midpoint(self, points):
        point1, point2 = points
        midx = int((point1[0] + point2[0]) / 2.0)
        midy = int((point1[1] + point2[1]) / 2.0)
        return midx, midy

    def calc_bearing_x(self):
        target_x = self.target_coordinates[0]
        center_x = self.image_width / 2.0
        if target_x == center_x:
            return 0.0
        pixels_off = abs(center_x - target_x)
        heading_abs = self.robot.turret_camera.camera_fov_degrees_x * float(pixels_off) / self.image_width
        if target_x < center_x:
            return heading_abs * -1.0
        else:
            return heading_abs

    def calc_bearing_y(self):
        target_y = self.target_coordinates[1]
        center_y = self.image_height / 2.0
        offset_in_pixels = center_y - target_y
        angle = (float(offset_in_pixels) * self.robot.turret_camera.camera_fov_degrees_y) / self.image_height
        return angle + self.robot.turret_camera.camera_vertical_pitch

    def calc_base_range(self, y_bearing):
        outer_goal_center_height_inches = 98.25
        camera_height = self.robot.turret_camera.camera_height
        vertical_offset_inches = abs(outer_goal_center_height_inches - camera_height)
        if self.bearing_y == 0.0:
            #TODO: Figure this out!
            return 0.0
        else:
            distance = abs(vertical_offset_inches / (math.tan(math.radians(self.bearing_y))))
            return distance