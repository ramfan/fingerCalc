import math

import cv2
import numpy as np


class Process:

    def __init__(self):
        self.__camera = cv2.VideoCapture(0)
        self.__camera.set(100, 400)

    def get_frame(self):
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
                trigger = False
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

    def removeBG(self, frame, bgModel, learningRate):
        """Метод удаляет фон и возвращает новое изображение"""
        fgmask = bgModel.apply(frame, learningRate=learningRate)
        kernel = np.ones((3, 3), np.uint8)
        fgmask = cv2.erode(fgmask, kernel, iterations=1)
        res = cv2.bitwise_and(frame, frame, mask=fgmask)
        return res