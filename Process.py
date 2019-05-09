import math

import cv2
import numpy as np
import copy

from Service.PlatformFactory import PlatformFactory

threshold = 60


class Process:

    def __init__(self, cap_region_x_begin, cap_region_y_end, learningRate):
        self.__camera = cv2.VideoCapture(0)
        self.__camera.set(10, 400)
        self._cap_region_x_begin = cap_region_x_begin
        self._cap_region_y_end = cap_region_y_end
        self._learningRate = learningRate
        self.__counterIterable = 0
        self.__pastCoords = [0, 0, 0, 0, 0]
        self.__triggerSwitcher = False
        self.__bgModel = None
        self._bgSubThreshold = 50
        self._platform = PlatformFactory().getClassByPlatform()
        cv2.namedWindow('trackbar', 1)
        cv2.createTrackbar('trh1', 'trackbar', threshold, 100, self.__printThreshold)

    def __printThreshold (self, thr):
        print("Изменено пороговое значение на " + str(thr))

    def change_bgModel(self):
        self.__bgModel = cv2.createBackgroundSubtractorMOG2(0, self._bgSubThreshold)

    def set_default_bgModel(self):
        self.__bgModel = None

    def __get_frame(self):
        ret, frame = self.__camera.read()
        if ret:
            pass
        frame = cv2.bilateralFilter(frame, 5, 500, 100)
        frame = cv2.flip(frame, 1)
        return frame

    def get_camera_status(self):
        return self.__camera.isOpened()

    def close_camera(self):
        self.__camera.release()

    def __calculateFingers(self, res, drawing):
        hull = cv2.convexHull(res, returnPoints=False)
        if len(hull) > 1:
            defects = cv2.convexityDefects(res, hull)
            if type(defects) != type(None):
                cnt = 0
                coordsArray = []
                for i in range(defects.shape[0]):
                    s, e, f, d = defects[i][0]
                    start = tuple(res[s][0])
                    end = tuple(res[e][0])
                    far = tuple(res[f][0])
                    a = math.sqrt((end[0] - start[0]) ** 2 +
                                  (end[1] - start[1]) ** 2)
                    b = math.sqrt((far[0] - start[0]) ** 2 +
                                  (far[1] - start[1]) ** 2)
                    c = math.sqrt((end[0] - far[0]) ** 2 + (end[1] - far[1]) ** 2)
                    angle = math.acos((b ** 2 + c ** 2 - a ** 2) /
                                      (2 * b * c))
                    if angle <= math.pi / 2:
                        cnt += 1
                        coordsArray.append([start, end])

                        cv2.circle(drawing, end, 8, [255, 0, 0], -1)
                        cv2.circle(drawing, start, 8, [255, 0, 0], -1)
                return True, cnt, coordsArray

        return False, 0, []

    def __compareCoords(self, next):
        if len(next) > 0 or len(self.__pastCoords) > 0:

            for i in range(5):

                if i < len(next) and i < len(self.__pastCoords):
                    try:
                        int(next[i][0][0] - self.__pastCoords[i][0][0])
                        if (next[i][0][0] - self.__pastCoords[i][0][0]) > 25 and (next[i][1][0] - self.__pastCoords[i][1][0]) > 25:
                            if next[i][0][0] > self.__pastCoords[i][0][0]:
                                print('Регистрация движения №% s : вправо' % self.__counterIterable)
                                self._platform.swipe_workspace_right()
                                return True
                        if (self.__pastCoords[i][0][0] - next[i][0][0]) > 25 and (self.__pastCoords[i][1][0] - next[i][1][0]) > 25:
                            if next[i][0][0] < self.__pastCoords[i][0][0]:
                                print('Регистрация движения №% s : влево' % self.__counterIterable)
                                self._platform.swipe_workspace_left()
                                return True
                    except Exception:
                        return False

        return False

    def __removeBG(self, frame):
        fgmask = self.__bgModel.apply(frame, learningRate=self._learningRate)
        kernel = np.ones((5, 5), np.uint8)
        cv2.dilate(fgmask, kernel, iterations=1)
        fgmask = cv2.erode(fgmask, kernel, iterations=1)
        result = cv2.bitwise_and(frame, frame, mask=fgmask)
        return result


    def __get_contours(self):
        img = self.__get_img()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blurValue = 41
        blur = cv2.GaussianBlur(gray, (blurValue, blurValue), 0)
        threshold = cv2.getTrackbarPos('trh1', 'trackbar')
        ret, thresh = cv2.threshold(blur, threshold, 255, cv2.THRESH_BINARY)

        thresh1 = copy.deepcopy(thresh)
        contours, hierarchy = cv2.findContours(
            thresh1, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        return contours

    def start(self):
        frame = self.__get_frame()
        cv2.rectangle(frame, (int(self._cap_region_x_begin * frame.shape[1]), 0),
                      (frame.shape[1], int(self._cap_region_y_end * frame.shape[0])), (255, 0, 0), 2)
        cv2.imshow('original', frame)

    def __get_img(self):
        frame = self.__get_frame()
        img = self.__removeBG(frame)
        img = img[0:int(self._cap_region_y_end * frame.shape[0]),
              int(self._cap_region_x_begin * frame.shape[1]):frame.shape[1]]
        return img

    def __get_drawing(self):
        img = self.__get_img()
        return np.zeros(img.shape, np.uint8)

    def __get_result_counter(self):
        contours = self.__get_contours()
        maxArea = -1
        length = len(contours)
        ci = 0
        res = None
        if length > 0:
            for i in range(length):
                temp = contours[i]
                area = cv2.contourArea(temp)
                if area > maxArea:
                    maxArea = area
                    ci = i

            res = contours[ci]
            return res

    def get_processed_img(self ):
        contours = self.__get_contours()
        length = len(contours)
        res = self.__get_result_counter()

        drawing = self.__get_drawing()
        if isinstance(res, type(None)) is False:
            cv2.drawContours(drawing, [res], 0, (177, 255, 0), 2)
            isFinishCal, cnt, coords = self.__calculateFingers(res, drawing)
            if self.__triggerSwitcher:
                if isFinishCal is True and cnt <= 5 and cnt > 1 and self.__compareCoords(coords) is True:
                    self.__counterIterable += 1
                self.__pastCoords = coords

        cv2.imshow('output', drawing)

    def set_trigger_switcher(self):
        if self.__triggerSwitcher is False:
            self.__triggerSwitcher = True

        elif self.__triggerSwitcher is True:
            self.__triggerSwitcher = False
