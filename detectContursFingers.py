# pylint: disable=no-member

import cv2
import numpy as np
import copy
import math

from Process import Process

pastCoords = [0, 0, 0, 0, 0]
cap_region_x_begin = 0.5
cap_region_y_end = 0.8
threshold = 60
bgSubThreshold = 50
learningRate = 0
counterIterable = 0
isBgCaptured = 0
triggerSwitch = False


def printThreshold(thr):
    """Метод типа void"""
    print("! Changed threshold to "+str(thr))

def main(counterIterable, isBgCaptured, threshold, triggerSwitch, pastCoords):
    camera = cv2.VideoCapture(0)
    camera.set(10, 400)
    cv2.namedWindow('trackbar')
    cv2.createTrackbar('trh1', 'trackbar', threshold, 100, printThreshold)
    process = Process(cap_region_x_begin, cap_region_y_end, learningRate)
    while process.get_camera_status() is True:
        process.start()
        if isBgCaptured == 1:

            contours = process.get_contours(bgModel)
            length = len(contours)
            maxArea = -1
            ci = 0
            if length > 0:
                for i in range(length):
                    temp = contours[i]
                    area = cv2.contourArea(temp)
                    if area > maxArea:
                        maxArea = area
                        ci = i

                res = contours[ci]
                hull = cv2.convexHull(res)
                drawing = process.get_drawing(bgModel)
                cv2.drawContours(drawing, [res], 0, (177, 255, 0), 2)
                isFinishCal, cnt, coords = process.calculateFingers(res, drawing)

                if triggerSwitch is True:
                    if isFinishCal is True and cnt <= 5 and cnt > 1 and process.compareCoords(coords, pastCoords, counterIterable) == True:
                        counterIterable += 1
                    pastCoords = coords
            cv2.imshow('output', drawing)
        k = cv2.waitKey(10)
        if k == 27:
            process.close_camera()
            cv2.destroyAllWindows()
            break
        elif k == ord('b'):
            bgModel = cv2.createBackgroundSubtractorMOG2(0, bgSubThreshold)
            isBgCaptured = 1
        elif k == ord('r'):
            bgModel = None
            triggerSwitch = False
            isBgCaptured = 0
        elif k == ord('n'):
            triggerSwitch = True


if __name__ == '__main__':
    main(counterIterable, isBgCaptured, threshold, triggerSwitch, pastCoords)
