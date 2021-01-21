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


def in_ring(point, center, R1, R2):
    if R2 < 0:
        R2 = 0
    if R1 <= R2:
        return False
    return R2**2 <= (point[0] - center[0])**2 + (point[1] - center[1])**2 <= R1**2


def neighbours(point, w, h):
    x, y = point
    neighboursList = []
    for i in [-1, 1]:
        if 0 <= x + i < h:
            neighboursList.append((x+i, y))
        if 0 <= y + i < w:
            neighboursList.append((x, y+i))
    return neighboursList
