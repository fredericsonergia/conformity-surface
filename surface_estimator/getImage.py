import os
import requests as rq
import numpy as np
from PIL import Image
from matplotlib.offsetbox import TextArea, DrawingArea, OffsetImage, AnnotationBbox
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
from .coordonnees.conversion import gps2Lambert, gps2zone, getZone, lambert, degre2rad
from .IGN_API import getVille
import matplotlib as mpl
mpl.use('Agg')


# get the image from the internet
w = 800
h = 400

r = 6

W = w/r
H = h/r

folder = "static/"

# x = 4.863412
# y = 45.8529598


def plotOnImage(coords, coordinates, code):
    bbox = getBbox(coords)
    getImage(w, h, coords, code)
    img = Image.open(r'' + folder + stringify(coords) + '.png')
    batiment = [np.array(lambert(degre2rad(coord[0]), degre2rad(
        coord[1]))) - np.array([coords[0] - 3, 0]) for coord in coordinates]
    batX, batY = [r*(coord[0] - bbox[0]) for coord in batiment], [r *
                                                                  (coord[1] - bbox[1]) for coord in batiment]
    fig, ax = plt.subplots()
    ax.imshow(img, extent=[0, w, 0, h])
    ax.plot(batX, batY, color='firebrick')
    # plt.show()


def getPlottedPlan(coords, coordinates, code):
    bbox = getBbox(coords)
    getImage(w, h, coords, code)
    img = Image.open(r'' + folder + stringify(coords) + '.png')
    batiment = [np.array(lambert(degre2rad(coord[0]), degre2rad(
        coord[1]))) - np.array([coords[0] - 3, 0]) for coord in coordinates]
    batX, batY = [r*(coord[0] - bbox[0]) for coord in batiment], [r *
                                                                  (coord[1] - bbox[1]) for coord in batiment]
    file_name = stringify(coords) + "_plotted"+".png"
    fig, ax = plt.subplots()
    ax.imshow(img, extent=[0, w, 0, h])
    ax.plot(batX, batY, color='firebrick')
    plt.axis('off')
    plt.savefig(folder + file_name, bbox_inches='tight')


# x = 4.706264264112325
# y = 45.87721353563377


# X, Y = lambert(degre2rad(x), degre2rad(y))
# print(X,Y)

# bbox = (X - W/2, Y - H/2, X + W/2, Y + H/2)
# bbox = (1636355.34,8186674.09,1636488.6733333333,8186740.756666667)
# print(1832443.79 - W/2, 5187772.12 -H/2, 1832443.79 + W/2, 5187772.12+H/2)
# print(1832516.3385950415,5187700.467304348,1832609.49231405,5187744.497652174)
# print(bbox)
baseURL = "https://inspire.cadastre.gouv.fr/scpc/"

availableLayers = ["AMORCES_CAD", "CP.CadastralParcel", "CLOTURE", "DETAIL_TOPO",
                   "BU.Building", "BORNE_REPERE", "LIEUDIT", "SUBFISCAL", "HYDRO", "VOIE_COMMUNICATION"]


def getImage(w, h, coords, code, layersIndex=range(len(availableLayers))):
    layers = [availableLayers[i] for i in layersIndex]
    zone = str(getZone(coords))
    codeINSEE = code
    w, h = str(w), str(h)
    bbox = getBbox(coords)
    URL = baseURL + codeINSEE + ".wms?service=wms&version=1.3&request=GetMap&layers=" + \
        stringify(layers) + "&format=image/png&crs=EPSG:39" + zone + \
        "&bbox=" + stringify(bbox) + "&width="+w+"&height="+h+"&styles="
    res = rq.get(URL)
    file_name = stringify(coords)+".png"
    if not os.path.exists(folder):
        os.mkdir(folder)
    with open(folder + file_name, 'wb') as fp:
        fp.write(res.content)
    print("Image retrieved")


def stringify(liste):
    res = ""
    for i in range(len(liste)):
        res += str(liste[i])
        if i != len(liste) - 1:
            res += ","
    return res


def getBbox(coords):
    x, y = coords
    X, Y = lambert(degre2rad(x), degre2rad(y))
    bbox = (X - W/2, Y - H/2, X + W/2, Y + H/2)
    return bbox
# coords = x, y

# getImage(w,h,coords)
