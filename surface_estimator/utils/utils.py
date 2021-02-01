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


def stringify(liste):
    res = ""
    for i in range(len(liste)):
        res += str(liste[i])
        if i != len(liste) - 1:
            res += ","
    return res


def find_closest(image, jaune):
    h, w = image.shape[:2]
    center = (h//2, w//2)
    notFound = True
    if is_color(list(image[center]), jaune):
        notFound = False
        coordinates = center
    R = 0
    while notFound and R < min(h, w):
        for i in range(-R, R):
            for j in range(-R, R):
                if in_ring((i, j), (0, 0), R, R-1):
                    if is_color(list(image[center[0] - i, center[1] - j]), jaune):
                        coordinates = (center[0] - i, center[1] - j)
                        notFound = False
        R += 1
    if notFound:
        coordinates = (-1, -1)
    return coordinates


def is_color(pixel, color):
    return list(pixel) == list(color)


def get_inside_point(batiment, coef, w, h):
    index = -1
    i = 0
    n = len(batiment)
    while index < 0 and i < n:
        x, y = batiment[i]
        if x < w and y < h and x >= 1 and y >= 1:
            index = i
        i += 1
    if index < 0:
        return -1, -1
    sumX, sumY = coef*batiment[index]
    for i in range(1, len(batiment)):
        sumX += batiment[i][0]*(1-coef)/(n-1)
        sumY += batiment[i][1]*(1-coef)/(n-1)
    return min(int(sumX), w-1), min(int(sumY), h-1)
