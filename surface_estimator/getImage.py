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

folder = "./static/"


def plotOnImage(coords, coordinates, code, r, width, height):
    W = width/r
    H = height/r
    bbox = getBbox(coords, W, H)
    getImage(width, height, r, coords, code)
    img = Image.open(r'' + folder + stringify(coords) + '.png')
    batiment = [np.array(lambert(degre2rad(coord[0]), degre2rad(
        coord[1]))) - np.array([coords[0] - 3, 0]) for coord in coordinates]
    batX, batY = [r*(coord[0] - bbox[0]) for coord in batiment], [r *
                                                                  (coord[1] - bbox[1]) for coord in batiment]
    fig, ax = plt.subplots()
    ax.imshow(img, extent=[0, width, 0, height])
    ax.plot(batX, batY, color='firebrick')
    # plt.show()


def getPlottedPlan(coords, coordinates, code, r, width, height):
    W = width/r
    H = height/r
    bbox = getBbox(coords, W, H)
    getImage(width, height, r, coords, code)
    img = Image.open(r'' + folder + stringify(coords) + '.png')
    batiment = [np.array(lambert(degre2rad(coord[0]), degre2rad(
        coord[1]))) - np.array([coords[0] - 3, 0]) for coord in coordinates]
    batX, batY = [r*(coord[0] - bbox[0]) for coord in batiment], [r *
                                                                  (coord[1] - bbox[1]) for coord in batiment]
    file_name = stringify(coords) + "_plotted"+".png"
    fig, ax = plt.subplots()
    ax.imshow(img, extent=[0, width, 0, height])
    ax.plot(batX, batY, color='firebrick')
    plt.axis('off')
    plt.savefig(folder + file_name, bbox_inches='tight')


baseURL = "https://inspire.cadastre.gouv.fr/scpc/"

availableLayers = ["BU.Building", "CP.CadastralParcel", "VOIE_COMMUNICATION", "AMORCES_CAD", "CLOTURE", "DETAIL_TOPO",
                   "BORNE_REPERE", "LIEUDIT", "SUBFISCAL", "HYDRO"]


def getImage(w, h, r, coords, code, layersIndex=range(len(availableLayers))):
    layers = [availableLayers[i] for i in layersIndex]
    zone = str(getZone(coords))
    codeINSEE = code
    W = w/r
    H = h/r
    bbox = getBbox(coords, W, H)
    URL = baseURL + codeINSEE + ".wms?service=wms&version=1.3&request=GetMap&layers=" + \
        stringify(layers) + "&format=image/png&crs=EPSG:39" + zone + \
        "&bbox=" + stringify(bbox) + "&width="+str(w) + \
        "&height="+str(h)+"&styles="
    print(URL)
    res = rq.get(URL)
    file_name = stringify(coords)+".png"
    if not os.path.exists(folder):
        os.mkdir(folder)
    with open(folder + file_name, 'wb') as fp:
        fp.write(res.content)
    print("Image retrieved")
    return file_name, zone


def get_image_with_pixels(w, h, r, coords, center, code, zone, layersIndex=range(len(availableLayers))):
    layers = [availableLayers[i] for i in layersIndex]
    codeINSEE = code
    x, y = coords
    b, a = center
    X, Y = lambert(degre2rad(x), degre2rad(y))
    Xc, Yc = X + (a - w//2)/r, Y + (b - h//2)/r
    W = w/r
    H = h/r
    bbox = get_bbox_from_lambert(Xc, Yc, W, H)
    URL = baseURL + codeINSEE + ".wms?service=wms&version=1.3&request=GetMap&layers=" + \
        stringify(layers) + "&format=image/png&crs=EPSG:39" + zone + \
        "&bbox=" + stringify(bbox) + "&width="+str(w) + \
        "&height="+str(h)+"&styles="
    res = rq.get(URL)
    file_name = stringify(coords) + "_centered.png"
    if not os.path.exists(folder):
        os.mkdir(folder)
    with open(folder + file_name, 'wb') as fp:
        fp.write(res.content)
    print("Image retrieved")
    return file_name, zone


def stringify(liste):
    res = ""
    for i in range(len(liste)):
        res += str(liste[i])
        if i != len(liste) - 1:
            res += ","
    return res


def getBbox(coords, W, H):
    x, y = coords
    X, Y = lambert(degre2rad(x), degre2rad(y))
    bbox = (X - W/2, Y - H/2, X + W/2, Y + H/2)
    return bbox


def get_bbox_from_lambert(X, Y, W, H):
    bbox = (X - W/2, Y - H/2, X + W/2, Y + H/2)
    return bbox
