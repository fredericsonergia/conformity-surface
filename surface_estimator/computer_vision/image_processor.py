import cv2
import pytesseract
import os
from PIL import Image
import numpy as np


class ImageProcessor():
    def __init__(self, file_path):
        self.file_path = file_path
    
    def load(self):
        self.img = cv2.imread(self.file_path)
    
    def get_binary(self, limit):
        gray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
        ret,thresh = cv2.threshold(gray,limit,255,cv2.THRESH_BINARY)

        thresh = 255 - thresh
        # thresh = cv2.dilate(thresh, (10, 10), 1)
        # blurred = cv2.GaussianBlur(thresh, (1,1), 1)
        # thresh = blurred
        return thresh

    def get_contours(self, thresh, background_image):
        gray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
        

        edges = cv2.Canny(gray,50,150,apertureSize = 3)
        minLineLength = 30
        maxLineGap = 20
        lines_edges = cv2.HoughLinesP(edges,1,np.pi/180,50,minLineLength,maxLineGap)
        for line in lines_edges:
            x1,y1,x2,y2 = line[0]
            cv2.line(background_image,(x1,y1),(x2,y2),(0,0,0),1)
        
        minLineLength = 30
        maxLineGap = 10
        lines_thresh = cv2.HoughLinesP(thresh,1,np.pi/180,50,minLineLength,maxLineGap)

        for line in lines_thresh:
            x1,y1,x2,y2 = line[0]
            cv2.line(background_image,(x1,y1),(x2,y2),(0,0,0),1)
        return background_image

    def save_file(self, img, prefix):
        # filename = "{}_{}.png".format(prefix,os.getpid())
        filename = prefix + ".png"
        cv2.imwrite(filename, img)
        return filename

    def OCRize(self, filename):
        text = pytesseract.image_to_string(Image.open(filename))
        os.remove(filename)
        print(text)

processor = ImageProcessor("./static/traits&chiffres.png")
processor.load()
thresh = processor.get_binary(250)
cv2.imshow("thresh",thresh)
cv2.waitKey(0)
no_lines = cv2.imread("./static/no_lines.png")
new_lines = processor.get_contours(thresh, no_lines)
cv2.imshow("new_lines", new_lines)
cv2.waitKey(0)
processor.save_file(new_lines, "./static/building&lines")
# filename = processor.save_file(thresh)
# print(filename)
# processor.OCRize(filename)
# cv2.imshow("",thresh)
# cv2.waitKey(0)