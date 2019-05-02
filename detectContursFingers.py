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
blurValue = 41
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
    process = Process()
    while process.get_camera_status() is True:
        frame = process.get_frame()
        cv2.rectangle(frame, (int(cap_region_x_begin * frame.shape[1]), 0),
                      (frame.shape[1], int(cap_region_y_end * frame.shape[0])), (255, 0, 0), 2)
        cv2.imshow('original', frame)
        if isBgCaptured == 1:
            img = process.removeBG(frame, bgModel, learningRate)
            img = img[0:int(cap_region_y_end * frame.shape[0]),
                  int(cap_region_x_begin * frame.shape[1]):frame.shape[1]]

            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            blur = cv2.GaussianBlur(gray, (blurValue, blurValue), 0)
            ret, thresh = cv2.threshold(blur, threshold, 255, cv2.THRESH_BINARY)
            threshold = cv2.getTrackbarPos('trh1', 'trackbar')

            thresh1 = copy.deepcopy(thresh)
            contours, hierarchy = cv2.findContours(
                thresh1, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            length = len(contours)
            maxArea = -1
            if length > 0:
                for i in range(length):
                    temp = contours[i]
                    area = cv2.contourArea(temp)
                    if area > maxArea:
                        maxArea = area
                        ci = i

                res = contours[ci]
                hull = cv2.convexHull(res)
                drawing = np.zeros(img.shape, np.uint8)
                cv2.drawContours(drawing, [res], 0, (177, 255, 0), 2)
                # cv2.imwrite(fileName, drawing)
                isFinishCal, cnt, coords = process.calculateFingers(res, drawing)

                if triggerSwitch is True:
                    if isFinishCal is True and cnt <= 5 and cnt > 1 and process.compareCoords(coords, pastCoords, counterIterable) == True:
                        counterIterable += 1

                        # print(counterIterable)
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
