import cv2
import os
from PIL import Image
import numpy as np


class ImageProcessor():
    def __init__(self, file_path=None, image=None):
        if not file_path is None:
            self.file_path = file_path
            self.load()
        if not image is None:
            self.img = image

    def load(self):
        self.img = cv2.imread(self.file_path)

    def get_binary(self, limit):
        gray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
        ret, thresh = cv2.threshold(gray, limit, 255, cv2.THRESH_BINARY)

        thresh = 255 - thresh
        kernel = np.ones((3, 3), np.uint8)

        thresh = cv2.dilate(thresh, kernel, 2)
        blurred = cv2.GaussianBlur(thresh, (1, 1), 1)
        thresh = blurred

        return thresh

    def get_contours(self, thresh, background_image):
        gray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)

        edges = cv2.Canny(gray, 50, 255, apertureSize=5)
        # cv2.imshow("canny", edges)
        # cv2.waitKey(0)
        minLineLength = 20
        maxLineGap = 20
        lines_edges = cv2.HoughLinesP(
            edges, 1, np.pi/180, 50, minLineLength, maxLineGap)
        for line in lines_edges:
            x1, y1, x2, y2 = line[0]
            cv2.line(background_image, (x1, y1), (x2, y2), (0, 0, 0), 2)

        minLineLength = 20
        maxLineGap = 20
        lines_thresh = cv2.HoughLinesP(
            thresh, 1, np.pi/180, 50, minLineLength, maxLineGap)

        for line in lines_thresh:
            x1, y1, x2, y2 = line[0]
            cv2.line(background_image, (x1, y1), (x2, y2), (0, 0, 0), 2)
        return background_image

    def save_file(self, img, prefix):
        # filename = "{}_{}.png".format(prefix,os.getpid())
        filename = prefix + ".png"
        cv2.imwrite(filename, img)
        return filename
