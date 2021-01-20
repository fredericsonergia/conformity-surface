
import numpy as np
import cv2
from surface_estimator.utils import in_ring, neighbours
from surface_estimator.IGN_API import getVille
from surface_estimator.getImage import getImage, get_image_with_pixels


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

    def load(self, file=self.file_name):
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

    def label(self):

        gray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
        thresh = cv2.threshold(self.img, 60, 255, cv2.THRESH_BINARY)[1]
        cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                                cv2.CHAIN_APPROX_SIMPLE)
        print(cnts)
        mask = np.zeros(self.img.shape[:2], dtype="uint8")
        cv2.drawContours(mask, cnts[0], -1, 255, -1)
        mask = cv2.erode(mask, None, iterations=2)
        mean = cv2.mean(self.img, mask=mask)[:3]
        cv2.imshow("Image", self.img)
        cv2.waitKey(0)

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
