
from surface_estimator.getImage import getImage, get_image_with_pixels
from surface_estimator.IGN_API import getVille
from surface_estimator.utils import in_ring, neighbours, stringify, find_closest, is_color
from surface_estimator.algorithmes.closest import distance_polygon
from collections import OrderedDict
from surface_estimator.algorithmes.calcul_surface import surface, perimetre
from .image_processor import ImageProcessor
import matplotlib.pyplot as plt
import numpy as np
import cv2
from scipy.spatial import distance as dist
import imutils
import matplotlib as mpl


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
    def __init__(self, coordinates=(0, 0)):
        self.title = "title"
        self.coordinates = coordinates

    def get_images(self, w, h, r, folder):
        ville, code = getVille(self.coordinates)
        file_name, zone, bbox = getImage(w, h, r, self.coordinates, code, [0])
        self.img = cv2.imread(folder + file_name)
        jaune = [51, 204, 255]
        center = find_closest(self.img, jaune)
        self.file_name_cadastre, zone, bbox, folder = get_image_with_pixels(
            w, h, r, self.coordinates, center, code, zone, [1])
        self.file_name_bu, zone, bbox, folder = get_image_with_pixels(
            w, h, r, self.coordinates, center, code, zone, [0])
        self.file_name_back, zone, bbox, folder = get_image_with_pixels(
            w, h, r, self.coordinates, center, code, zone, [2, 1, 0, 4, 5, 7, 8, 9])

    def load(self, folder, all=False, file=None):
        if all:
            self.cadastre = cv2.imread(self.file_name_cadastre)
            self.bu = cv2.imread(self.file_name_bu)
            self.back = cv2.imread(self.file_name_back)
        else:
            if file is None:
                file = self.file_name
            else:
                self.file_name = file
            self.img = cv2.imread(file)

    def show(self):
        cv2.imshow(self.title, self.back)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def binarize(self):
        gray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
        thresh = cv2.inRange(gray, 50, 220)
        return thresh

    def get_connex(self, start_coords, image):
        couleur = image[start_coords]
        if couleur == 0:
            return []
        h, w = image.shape[:2]
        potential_neighbours = [start_coords]
        visited = []
        connex = [start_coords]
        while len(potential_neighbours) > 0:
            current_point = potential_neighbours.pop()
            neighboursList = neighbours(current_point, w, h)
            for neighbour in neighboursList:
                if neighbour not in visited and image[neighbour] == couleur:
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

    def get_surface_connex(self, connex, r):
        return len(connex)/r**2

    def get_lines(self):
        processor = ImageProcessor(image=self.cadastre)
        thresh = processor.get_binary(250)
        no_lines = self.bu
        new_lines = processor.get_contours(thresh, no_lines)
        cv2.imshow("new_lines", new_lines)
        cv2.waitKey(0)
        self.file_name = processor.save_file(
            new_lines, "./static/" + stringify(self.coordinates) + "/" + "new_lines")

    def get_surfaces(self, r):
        contours = find_contours(self.file_name)
        surfaces = []
        h, w = self.img.shape[:2]
        center = (w//2, h//2)
        dist_mini = float("inf")
        for cnt in contours:
            building = get_building_from_contour(cnt)
            d = distance_polygon(center, building)
            S = surface(building)
            per = perimetre(building)
            if d/r < dist_mini:
                dist_mini = d/r
                closest = cnt
                surface_closest = S/r**2
                per_closest = per*2/r**2
                surf = surface_closest+per_closest
            surfaces.append((S/r**2 + per*2/r**2, d/r))
        self.closest = closest
        print(surface_closest, surface_closest+per_closest)
        return surfaces, (closest, surface_closest, per_closest, surf)

    def draw_surface(self):
        draw_cnts([self.closest], self.back)
        cv2.imwrite("./static/" + stringify(self.coordinates) +
                    "/" + "contour.png", self.back)


def find_contours(image_path):
    image = cv2.imread(image_path)
    resized = imutils.resize(image, width=800)
    ratio = image.shape[0] / float(resized.shape[0])
    # blur the resized image slightly, then convert it to both
    # grayscale and the L*a*b* color spaces
    blurred = cv2.GaussianBlur(resized, (3, 3), 0)
    gray = cv2.cvtColor(blurred, cv2.COLOR_BGR2GRAY)
    lab = cv2.cvtColor(blurred, cv2.COLOR_BGR2LAB)
    thresh = cv2.inRange(gray, 200, 210)

    cv2.imwrite("./static/" + stringify((2.2609962353137605,
                                         48.88626507243932)) + "/" + "thresh.png", thresh)

    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                            cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    contours = []
    for c in cnts:
        if len(c) > 2:
            cl = ColorLabeler()
            color = cl.label(lab, c)
            if color == "yellow":
                contours.append(c)
    return contours


def draw_cnts(cnts, image):
    black = np.zeros((image.shape))
    black = image
    for c in cnts:
        print(c)
        cv2.drawContours(black, [c], -1, (0, 0, 255), 2)
        cv2.imshow("Image", black)
        cv2.waitKey(0)


def get_building_from_contour(cnt):
    building = [point[0] for point in cnt]
    return building


def surface_computer(coordinates):
    w, h, r = 800, 400, 6
    bf = BuildingFinder(coordinates=(2.1120532, 48.8606862))
    bf.get_images(w, h, r, "./static/")
    bf.load("./static/", all=True)
    bf.get_lines()
    surfaces, closest = bf.get_surfaces(6)
    closest, surface_closest, per_closest, surf = closest
    Ms = sum([surface[0] for surface in surfaces])/len(surfaces)
    print("N(batiment) =", len(surfaces))
    print("Résolution :", w*h)
    NJaune = sum([surface[0] for surface in surfaces])*r**2
    print("NJaune (px) =", NJaune)

    Tau = NJaune/(w*h - NJaune)
    DeltaS2 = abs(surf**2 - Ms**2)/Ms**2
    Md = sum([surface[1] for surface in surfaces])/len(surfaces)
    print("Ms =", Ms)
    print("Tau =", Tau)
    print("Md =", Md/(h/r))
    print("DeltaS =", np.sqrt(DeltaS2))
    print("confiance", np.sqrt((1-Tau)*np.sqrt(DeltaS2) + (Md/(h/r))**2)/2)

    building = get_building_from_contour(closest)

    bf.draw_surface()
