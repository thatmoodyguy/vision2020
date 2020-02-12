import os
import glob
import cv2
import numpy as np


criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

objp = np.zeros((5*9, 3), np.float32)
objp[:,:2] = np.mgrid[0:5,0:9].T.reshape(-1,2)

objpoints = []
imgpoints = []
first_match = None

os.chdir("/home/john/projects/vision2020/snapshots/")
cnt = 0
for file in glob.glob("*.jpg"):
    print(file)
    img = cv2.imread(file)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, corners = cv2.findChessboardCorners(gray, (5,9),None)
    if ret == True:
        if first_match is None:
            first_match = img
            continue
        cnt = cnt + 1
        objpoints.append(objp)
        corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
        imgpoints.append(corners2)
        img = cv2.drawChessboardCorners(img, (5,9), corners2, ret)
        cv2.imshow('img',img)
        cv2.waitKey(500)
    else:
        print("ret: {}".format(ret))
        cv2.imshow('img',img)
        cv2.waitKey(500)
    
#cv2.destroyAllWindows()
print("Successful count: {}".format(cnt))
print("calibrating...")
ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1],None, None)
h,w = first_match.shape[:2]
newmtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist,(w,h),0,(w,h))
mapx, mapy = cv2.initUndistortRectifyMap(mtx, dist, None, newmtx, (w,h), 5)
dst = cv2.remap(first_match, mapx, mapy, cv2.INTER_LINEAR)
#x,y,w,h = roi
#dst = dst[y:y+h, x:x+w]
cv2.imshow('img', dst)
while True:
    cv2.waitKey(500)
cv2.destroyAllWindows()




