import numpy as np


def distancePoint(point1, point2):
    return np.sqrt((point1[0]-point2[0])**2 + (point1[1]-point2[1])**2)


def getXY(batiment):
    return [coord[0] for coord in batiment], [coord[1] for coord in batiment]


def taille(batiment):
    x, y = getXY(batiment)
    DX = max(x) - min(x)
    DY = max(y) - min(y)
    return DX, DY
