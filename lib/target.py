import cv2

def contour_sort(e):
    return cv2.contourArea(e)

class Target():
    def __init__(self, image):
        self.image = image
        self.annotated_image = image
        self.acquired = False

    def acquire_target(self):
        contours = find_potential_targets(self.image)
        if contours.count == 0:
            self.acquired = False
            return
        return contours.sort(reverse=True,key=contour_sort)[0]
        
    def find_potential_targets(img):
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