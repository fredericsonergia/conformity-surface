
from surface_estimator.getImage import getImage, get_image_with_pixels
from surface_estimator.IGN_API import getVille
from surface_estimator.utils import in_ring, neighbours
from collections import OrderedDict
import matplotlib.pyplot as plt
import pytesseract
import numpy as np
import cv2
from scipy.spatial import distance as dist
import imutils
import matplotlib as mpl
mpl.use("MacOSX")


class ColorLabeler():
    def __init__(self):
        self.colors = OrderedDict({"white": [255, 255, 255], "yellow": [
                                  249, 204, 85], "lyellow": [251, 227, 162], "black": [50, 50, 50]})
        self.lab = np.zeros((len(self.colors), 1, 3), dtype="uint8")
        self.colorNames = []
        for (i, (name, rgb)) in enumerate(self.colors.items()):
            self.lab[i] = rgb
            self.colorNames.append(name)
        self.lab = cv2.cvtColor(self.lab, cv2.COLOR_RGB2LAB)

    def label(self, image, c):
        mask = np.zeros(image.shape[:2], dtype="uint8")
        cv2.drawContours(mask, [c], -1, 255, -1)
        mask = cv2.erode(mask, None, iterations=2)
        mean = cv2.mean(image, mask=mask)[:3]
        # initialize the minimum distance found thus far
        minDist = (np.inf, None)
        # loop over the known L*a*b* color values
        for (i, row) in enumerate(self.lab):
            # compute the distance between the current L*a*b*
            # color value and the mean of the image
            d = dist.euclidean(row[0], mean)
            # if the distance is smaller than the current distance,
            # then update the bookkeeping variable
            if d < minDist[0]:
                minDist = (d, i)
        # return the name of the color with the smallest distance
        return self.colorNames[minDist[1]]


class BuildingFinder():
    def __init__(self, coordinates):
        self.title = "title"
        self.coordinates = coordinates

    def get_image(self, w, h, r):
        ville, code = getVille(self.coordinates)
        file_name, zone = getImage(w, h, r, self.coordinates, code)
        jaune = [51, 204, 255]
        center = self.find_closest(jaune)
        self.file_name, zone = get_image_with_pixels(
            w, h, r, self.coordinates, center, code, zone)

    def load(self, file=None):
        if file is None:
            file = self.file_name
        self.img = cv2.imread(file)

    def show(self):
        cv2.imshow(self.title, self.img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def find_closest(self, jaune):
        h, w = self.img.shape[:2]
        center = (h//2, w//2)
        notFound = True
        if is_color(list(self.img[center]), jaune):
            notFound = False
            coordinates = center
        R = 0
        while notFound and R < min(h, w):
            for i in range(-R, R):
                for j in range(-R, R):
                    if in_ring((i, j), (0, 0), R, R-1):
                        if is_color(list(self.img[center[0] - i, center[1] - j]), jaune):
                            coordinates = (center[0] - i, center[1] - j)
                            notFound = False
            R += 1
        if notFound:
            coordinates = (-1, -1)
        return coordinates

    def get_connex(self, start_coords):
        couleur = self.img[start_coords]
        h, w = self.img.shape[:2]
        print(h, w)
        potential_neighbours = [start_coords]
        visited = []
        connex = [start_coords]
        while len(potential_neighbours) > 0:
            current_point = potential_neighbours.pop()
            neighboursList = neighbours(current_point, w, h)
            for neighbour in neighboursList:
                if neighbour not in visited and is_color(self.img[neighbour], couleur):
                    potential_neighbours.append(neighbour)
                visited.append(neighbour)
            connex.append(current_point)
        return connex

    def mask(self, connex):
        h, w = self.img.shape[:2]
        newImg = np.zeros((h, w))
        for point in connex:
            newImg[point] = 1
        return newImg

    def get_surface(self, connex, r):
        return len(connex)/r**2


def is_color(pixel, color):
    return list(pixel) == list(color)


def find_contours(image):
    image = cv2.imread(image)
    resized = imutils.resize(image, width=800)
    ratio = image.shape[0] / float(resized.shape[0])
    # blur the resized image slightly, then convert it to both
    # grayscale and the L*a*b* color spaces
    blurred = cv2.GaussianBlur(resized, (3, 3), 0)
    gray = cv2.cvtColor(blurred, cv2.COLOR_BGR2GRAY)
    lab = cv2.cvtColor(blurred, cv2.COLOR_BGR2LAB)
    # thresh = cv2.threshold(gray, 220, 255, cv2.THRESH_BINARY)[1]
    thresh = cv2.inRange(gray, 200, 210)
    # plt.imshow(thresh)
    # plt.show()
    # find contours in the thresholded image
    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                            cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    black = np.zeros((image.shape))

    for c in cnts:
        if len(c) > 2:
            # compute the center of the contour
            M = cv2.moments(c)
            # cX = int((M["m10"] / M["m00"]) * ratio)
            # cY = int((M["m01"] / M["m00"]) * ratio)
            # detect the shape of the contour and label the color
            cl = ColorLabeler()
            color = cl.label(lab, c)
            print(color)
            # multiply the contour (x, y)-coordinates by the resize ratio,
            # then draw the contours and the name of the shape and labeled
            # color on the image
            # c = c.astype("float")
            # c *= ratio
            # c = c.astype("int")
            # text = "{} {}".format(color, shape)
            cv2.drawContours(black, [c], -1, (255, 255, 255), 1)
            # cv2.putText(image, text, (cX, cY),
            #             cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
            # show the output image
    cv2.imshow("Image", black)
    cv2.waitKey(0)


find_contours("./static/building&lines.png")
