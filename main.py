# pylint: disable=no-member

import cv2

from Process import Process

cap_region_x_begin = 0.5
cap_region_y_end = 0.8

learningRate = 0
isBgCaptured = 0

def main(isBgCaptured):
    process = Process(cap_region_x_begin, cap_region_y_end, learningRate)
    while process.get_camera_status() is True:
        process.start()
        if isBgCaptured == 1:
            process.get_processed_img()
        k = cv2.waitKey(10)
        if k == 27:
            process.close_camera()
            cv2.destroyAllWindows()
            break
        elif k == ord('b'):
            process.change_bgModel()
            isBgCaptured = 1
        elif k == ord('r'):
            process.set_default_bgModel()
            isBgCaptured = 0
        elif k == ord('n'):
           process.set_trigger_switcher()


if __name__ == '__main__':
    main(isBgCaptured)
