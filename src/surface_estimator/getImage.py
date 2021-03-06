import os
import requests as rq
import numpy as np
from PIL import Image
from matplotlib.offsetbox import TextArea, DrawingArea, OffsetImage, AnnotationBbox
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
from .coordonnees.conversion import gps2Lambert, gps2zone, getZone, lambert, degre2rad
from .utils import stringify, find_closest
import cv2
import matplotlib as mpl
mpl.use('Agg')


# get the image from the internet


class ImagesController():
    def __init__(self, folder):
        self.folder = folder
        self._baseURL = "https://inspire.cadastre.gouv.fr/scpc/"

        self._availableLayers = ["BU.Building", "CP.CadastralParcel", "VOIE_COMMUNICATION", "AMORCES_CAD", "CLOTURE", "DETAIL_TOPO",
                    "BORNE_REPERE", "LIEUDIT", "SUBFISCAL", "HYDRO"]


    def plotOnImage(self, coords, coordinates, code, r, width, height):
        W = width/r
        H = height/r
        bbox = self._getBbox(coords, W, H)
        self.getImage(width, height, r, coords, code)
        img = Image.open(r'' + self.folder + stringify(coords) + '.png')
        batiment = [np.array(lambert(degre2rad(coord[0]), degre2rad(
            coord[1]))) - np.array([coords[0] - 3, 0]) for coord in coordinates]
        batX, batY = [r*(coord[0] - bbox[0]) for coord in batiment], [r *
                                                                    (coord[1] - bbox[1]) for coord in batiment]
        fig, ax = plt.subplots()
        ax.imshow(img, extent=[0, width, 0, height])
        ax.plot(batX, batY, color='firebrick')


    def getPlottedPlan(self, coords, coordinates, code, r, width, height):
        W = width/r
        H = height/r
        bbox = self._getBbox(coords, W, H)
        file_name, zone, bbox = self.getImage(width, height, r, coords, code)
        img = Image.open(r'' + file_name)
        batiment = [np.array(lambert(degre2rad(coord[0]), degre2rad(
            coord[1]))) - np.array([coords[0] - 3, 0]) for coord in coordinates]
        batX, batY = [r*(coord[0] - bbox[0]) for coord in batiment], [r *
                                                                    (coord[1] - bbox[1]) for coord in batiment]
        file_name = file_name[:-4] + "_plotted"+".png"
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.imshow(img, extent=[0, width, 0, height])
        ax.plot(1*np.array(batX), 1*np.array(batY), color='firebrick')
        plt.axis('off')
        plt.savefig(file_name, bbox_inches='tight')
        return file_name, zone, bbox


    def plot_surroundings(self, image, coords, surroundings, bbox, w, h, r):
        img = image
        cnts = []
        for coordinates in surroundings:
            cnts.append(self.get_cnt_from_building(coordinates, coords, bbox, r, w, h))
        cv2.drawContours(img, cnts, -1, (0, 0, 0), 2)
        return img, cnts


    def _truncate_coords(self, coord, w, h):
        x, y = coord
        return [int(x), h-1-int(y)]


    def get_cnt_from_building(self, building, coords, bbox, r, w, h):
        batiment = [(np.array(lambert(degre2rad(coord[0]), degre2rad(
            coord[1]))) - np.array([coords[0] - 3, 0])) for coord in building]
        cnt = np.array([[self._truncate_coords([r*(coord[0] - bbox[0]), r*(coord[1] - bbox[1])], w, h)]
                        for coord in batiment])
        return cnt



    def getImage(self, w, h, r, coords, code, layersIndex=None):
        if layersIndex is None:
            layersIndex=range(len(self._availableLayers))
        layers = [self._availableLayers[i] for i in layersIndex]
        zone = str(getZone(coords))
        codeINSEE = code
        W = w/r
        H = h/r
        bbox = self._getBbox(coords, W, H)
        img = self._download_image(w, h, bbox, codeINSEE, layers, zone)

        if img is None:
            return None
        file_name = stringify(coords) + "/" + stringify(layersIndex) + ".png"
        Folder = self.folder + self._toDirectory(file_name.split('/')[:-1])
        print(Folder)
        if layersIndex == [1]:
            print(img)
        if not os.path.exists(Folder):
            os.makedirs(Folder)
        with open(self.folder + file_name, 'wb') as fp:
            fp.write(img)
        print("Image retrieved")
        return self.folder + file_name, zone, bbox


    def _download_image(self, w, h, bbox, codeINSEE, layers, zone):
        URL = self._baseURL + codeINSEE + ".wms?service=wms&version=1.3&request=GetMap&layers=" + \
            stringify(layers) + "&format=image/png&crs=EPSG:39" + zone + \
            "&bbox=" + stringify(bbox) + "&width="+str(w) + \
            "&height="+str(h)+"&styles="
        res = rq.get(URL)
        i = 0
        while res.content is None and i < 100:
            res = rq.get(URL)
            i += 1
        return res.content


    def get_image_with_pixels(self, w, h, r, coords, center, code, zone, layersIndex=None):
        if layersIndex is None:
            layersIndex=range(len(self._availableLayers))
        layers = [self._availableLayers[i] for i in layersIndex]
        codeINSEE = code
        x, y = coords
        b, a = center
        X, Y = lambert(degre2rad(x), degre2rad(y))
        Xc, Yc = X + (a - w//2)/r, Y + (b - h//2)/r
        W = w/r
        H = h/r
        bbox = self._get_bbox_from_lambert(Xc, Yc, W, H)
        img = self._download_image(w, h, bbox, codeINSEE, layers, zone)
        if img is None:
            return None
        file_name = stringify(coords) + "/" + stringify(center) + \
            stringify(layersIndex) + ".png"
        Folder = self.folder + self._toDirectory(file_name.split('/')[:-1])
        print(Folder)
        if not os.path.exists(Folder):
            os.mkdir(Folder)
        with open(self.folder + file_name, 'wb') as fp:
            fp.write(img)
        print("Image retrieved")
        return self.folder + file_name, zone, bbox


    def _toDirectory(self, liste):
        res = ""
        for i in range(len(liste)):
            res += str(liste[i])
            res += "/"
        return res


    def _getBbox(self, coords, W, H):
        x, y = coords
        X, Y = lambert(degre2rad(x), degre2rad(y))
        bbox = (X - W/2, Y - H/2, X + W/2, Y + H/2)
        return bbox


    def _get_bbox_from_lambert(self, X, Y, W, H):
        bbox = (X - W/2, Y - H/2, X + W/2, Y + H/2)
        return bbox


    def get_centered(self, w, h, r, coords, code, layersIndex=None):
        if layersIndex is None:
            layersIndex=range(len(self._availableLayers))
        file_name, zone, bbox = self.getImage(w, h, r, coords, code, layersIndex)
        img = cv2.imread(file_name)
        if img is None:
            return None
        jaune = [51, 204, 255]
        center = find_closest(img, jaune)
        cadastre = self.get_image_with_pixels(
            w, h, r, coords, center, code, zone, layersIndex)
        if cadastre is None:
            return None
        else:
            file_name_cadastre, zone, bbox = cadastre
            return file_name_cadastre, zone, bbox, center
