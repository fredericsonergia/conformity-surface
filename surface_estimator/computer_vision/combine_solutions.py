
from surface_estimator.IGN_API import getData, getVille
from surface_estimator.getImage import get_centered, plot_surroundings
from surface_estimator.algorithmes.closest import getClosestBuildings, extractCoordinates, distance_polygon
from surface_estimator.algorithmes.calcul_surface import perimetre
from surface_estimator.computer_vision.contours import find_contours, BuildingFinder, ColorLabeler
from surface_estimator.utils import get_inside_point
import numpy as np
import cv2


class SolutionCombiner():
    def __init__(self, coordinates):
        self.coordinates = coordinates
        self.code = None
        pass

    def get_back(self, w, h, r):
        """ 
        get the background image from cadastre 
        """
        ville, self.code = getVille(self.coordinates)
        centered = get_centered(
            w, h, r, self.coordinates, self.code, [0])
        if centered is None:
            return -1
        self.file_name, self.zone, self.bbox = centered
        img = cv2.imread(self.file_name)

    def get_buildings(self, R):
        """
        get the surroundings building data from Archives
        """
        if self.code is None:
            pass
        else:
            data, dt = getData(self.code)
            self.closestList = getClosestBuildings(
                self.coordinates, data, R)
            surroundings = [((extractCoordinates(close)), close["properties"]["type"])
                            for close in self.closestList]
            self.hard_buildings = [building[0]
                                   for building in surroundings if building[1] == '01']

    def combine(self, w, h, r, R):
        """
        plot the surroundings on the image
        """
        valid = self.get_back(w, h, r)
        if valid == -1:
            return -1
        self.r = r
        W, H = w/r, h/r
        self.get_buildings(R)
        image = cv2.imread(self.file_name)
        plotted, self.contours = plot_surroundings(
            image, self.coordinates, self.hard_buildings, self.bbox, w, h, r)
        file_name = self.file_name[:-4] + "_combined.png"
        self.file_name_combined = file_name
        self.image = plotted
        cv2.imwrite(file_name, self.image)

    def get_center_surface(self):
        """
        Compute the surface of the building in the middle of the image
        """
        r = self.r
        surfaces = []
        h, w = self.image.shape[:2]
        center = (w//2, h//2)
        finder = BuildingFinder()
        finder.load("./" + self.file_name_combined.split("/")
                    [1], file=self.file_name_combined)
        thresh = finder.binarize()
        x, y = (w//2, h//2)
        connex = finder.get_connex((y, x), thresh)
        self.surf = (len(connex))/r**2

    def get_surfaces(self):
        """
        Compute the surface of the closest buildings
        """

        r = self.r
        surfaces = []
        h, w = self.image.shape[:2]
        center = (w//2, h//2)
        lab = cv2.cvtColor(self.image, cv2.COLOR_BGR2LAB)
        finder = BuildingFinder()
        finder.load("./" + self.file_name_combined.split("/")
                    [1], file=self.file_name_combined)
        self.thresh = finder.binarize()
        thresh = self.thresh
        i = 0
        k = 0
        dist = float("inf")

        self.ret, labels = cv2.connectedComponents(thresh)
        ret = self.ret

        contours = cv2.findContours(
            thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]

        # print(contours)
        for label in range(1, ret):
            cnt = contours[ret-label-1]
            if len(cnt) > 2:
                cl = ColorLabeler()
                color = cl.label(lab, cnt)
                if color == "yellow":
                    mask = np.array(labels, dtype=np.uint8)
                    mask[labels == label] = 255
                    building = [point[0] for point in cnt]
                    d = distance_polygon(center, building)
                    per = perimetre(building)
                    if d < dist:
                        dist = d
                        self.building_index = k
                        self.cnt = cnt
                    surfaces.append(
                        ((len(mask[labels == label])+per*2)/r**2, d/r))
                    k += 1
        self.surfaces = surfaces
        # print(surfaces)
        # cv2.drawContours(mask, [cnt], -1, 200, 2)
        # cv2.imshow('component', mask)
        # cv2.waitKey(0)

        # for cnt in self.contours:
        #     i += 1
        #     if len(cnt) > 2:
        #         cl = ColorLabeler()
        #     color = cl.label(lab, cnt)
        #     if color == "yellow":
        #         building = [point[0] for point in cnt]
        #         x, y = get_inside_point(building, 0.9, w, h)
        #         d = distance_polygon(center, building)
        #         per = perimetre(building)
        #         print(int(i*100/len(self.contours)), "%")
        #         if (x, y) == (-1, -1):
        #             continue
        #         connex = finder.get_connex((y, x), thresh)
        #         if d < dist:
        #             dist = d
        #             index = k
        #         surfaces.append(((len(connex)+per*1)/r**2, d/r))
        #         k += 1
        # self.surfaces = surfaces
        # self.building_index = index
        # print(surfaces)

    def get_confidence(self):
        """
        Compute the confidence index on the computations
        """
        h, w = self.image.shape[:2]
        r = self.r
        surfaces = self.surfaces
        NJaune = sum([surface[0] for surface in self.surfaces])*r**2
        Ms = sum([surface[0] for surface in surfaces])/len(surfaces)
        tU = NJaune/(w*h - NJaune)
        surf = self.surfaces[self.building_index][0]
        DeltaS2 = abs(surf**2 - Ms**2)/Ms**2
        Md = sum([surface[1] for surface in surfaces])/len(surfaces)
        # print("N(batiment) =", len(surfaces))
        # print("Résolution :", w*h)
        # print("NJaune (px) =", NJaune)
        # print("Ms =", Ms)
        # print("Tau =", tU)
        # print("Md =", Md/(h/r))
        # print("DeltaS =", np.sqrt(DeltaS2))
        # print("confiance", np.sqrt((1-tU)*np.sqrt(DeltaS2) + (Md/(h/r))**2)/2)
        self.tU = tU
        self.DeltaD = Md/(h/r)
        self.DeltaS = np.sqrt(DeltaS2)
        self.conf = np.sqrt((1-tU)*np.sqrt(DeltaS2) + (Md/(h/r))**2)/2

    def draw(self, title):
        cv2.imshow('thresh', self.thresh)
        cv2.waitKey(0)
        cnt = self.cnt
        cv2.drawContours(self.image, [cnt], -1, (0, 0, 255), 2)
        cv2.imshow(title, self.image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
# sc = SolutionCombiner((2.1119255999999997, 48.860658423076934))
# sc.combine(800, 400, 6, 100)
# sc.get_surfaces()
# sc.get_confidence()
