import math

import cv2
import numpy as np
import copy


class Process:

    def __init__(self, cap_region_x_begin, cap_region_y_end, learningRate):
        self.__camera = cv2.VideoCapture(0)
        self.__camera.set(100, 400)
        self._cap_region_x_begin = cap_region_x_begin
        self._cap_region_y_end = cap_region_y_end
        self._learningRate = learningRate

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

    def calculateFingers(self, res, drawing):
        """Метод возвращает true если палец обнаружен"""
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
                                      (2 * b * c))  # cosine theorem
                    if angle <= math.pi / 2:  # angle less than 90 degree, treat as fingers
                        cnt += 1
                        coordsArray.append([start, end])

                        cv2.circle(drawing, end, 8, [255, 0, 0], -1)
                        cv2.circle(drawing, start, 8, [255, 0, 0], -1)
                # print("------------------")
                # print(coordsArray)

                return True, cnt, coordsArray

        return False, 0, []

    def compareCoords(self, next, current, counterIterable):
        if len(next) > 0 or len(current) > 0:

            for i in range(5):

                if i < len(next) and i < len(current):
                    try:
                        int(next[i][1][0] - current[i][1][0])
                        if (next[i][1][0] - current[i][1][0]) > 10:
                            if next[i][1][0] > current[i][1][0]:
                                print('Регистрация движения №% s : вправо' % counterIterable)
                                return True
                        if (current[i][1][0] - next[i][1][0]) > 10:
                            if next[i][1][0] < current[i][1][0]:
                                print('Регистрация движения №% s : влево' % counterIterable)
                                return True
                    except Exception:
                        return False

        return

    def __removeBG(self, frame, bgModel):
        fgmask = bgModel.apply(frame, learningRate=self._learningRate)
        kernel = np.ones((3, 3), np.uint8)
        fgmask = cv2.erode(fgmask, kernel, iterations=1)
        result = cv2.bitwise_and(frame, frame, mask=fgmask)
        return result


    def get_contours(self, bgModel):
        img = self.__get_img(bgModel)
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

    def __get_img(self, bgModel):
        frame = self.__get_frame()
        img = self.__removeBG(frame, bgModel)
        img = img[0:int(self._cap_region_y_end * frame.shape[0]),
              int(self._cap_region_x_begin * frame.shape[1]):frame.shape[1]]

        return img

    def get_drawing(self, bgModel):
        img = self.__get_img(bgModel)
        return np.zeros(img.shape, np.uint8)