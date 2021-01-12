import numpy as np
from .conversion import gps2plan, buildingGPS2plan
from .utils import distancePoint, getXY
from .calcul import point_dans_polygone
from .arbrekd import plus_proche_voisin


def distanceBatiment(point, batiment):
    minDist = float("inf")
    for pointBat in batiment:
        dist = distancePoint(gps2plan(point), gps2plan(pointBat))
        if dist < minDist:
            minDist = dist
    return minDist


def distanceCentre(point, batiment):
    n = len(batiment)
    x, y = getXY(batiment)
    x_moy, y_moy = sum(x)/n, sum(y)/n
    return distancePoint(gps2plan(point), gps2plan((x_moy, y_moy)))


def closestBuilding(point, cityData):
    closest = []
    minDist = float("inf")
    features = cityData["features"]
    for building in features:
        coordinates = extractCoordinates(building)
        if point_dans_polygone(coordinates, point):
            return building
        dist = distance_polygon(gps2plan(point),buildingGPS2plan(coordinates))
        if dist < minDist:
            minDist = dist
            closest = building
    return closest


def getClosestBuildings(point, cityData, radius, center=False):
    closestList = []
    features = cityData["features"]
    for building in features:
        coordinates = extractCoordinates(building)
        dist = distanceCentre(point, coordinates) if center else distanceBatiment(
            point, coordinates)
        if dist < radius:
            closestList.append(building)
    return closestList


def extractCoordinates(building):
    geometry = building["geometry"]
    Type, coordinates = geometry["type"], geometry["coordinates"]
    if Type == "MultiPolygon":
        coordinates = coordinates[0][0]
    elif Type == "Polygon":
        coordinates = coordinates[0]
    else:
        coordinates = coordinates
    return coordinates


def distance_segment(point, segment):
    B, M = segment
    A, B, M = np.array(point), np.array(B), np.array(M)
    BM = M - B
    BA = A - B
    AM = M - A
    BH = np.dot(BA, BM)/np.linalg.norm(BM)
    if np.dot(BA, BM) < 0 or np.dot(AM, BM) < 0:
        return min(np.linalg.norm(BA), np.linalg.norm(AM))
    else:
        return np.sqrt(np.linalg.norm(BA)**2 - BH**2)


def distance_polygon(point, polygon):
    minDist = float("inf")
    for i in range(len(polygon)-1):
        dist = distance_segment(point, [polygon[i], polygon[i+1]])
        if dist < minDist:
            minDist = dist
    return minDist

def centre(polygon):
    n = len(polygon)
    x, y = getXY(polygon)
    return sum(x)/n, sum(y)/n

def closestCenter(point, cityData):
    features = cityData["features"]
    # first get the centers
    centres = []
    for building in features:
        coordinates = extractCoordinates(building)
        centres.append(centre(buildingGPS2plan(coordinates)))
        if point_dans_polygone(coordinates, point):
            return building
    # then recover the closest
    voisin = plus_proche_voisin(gps2plan(point), centres)
    return features[voisin.data]

# triangle = [[0, 0], [0, 1], [1, 0], [0, 0]]
# carre = [[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]]

# polygone = [[0, 0], [0.5, -1], [1.5, -0.2], [2, -0.5],
#             [2, 0], [1.5, 1], [0.3, 0, ], [0.5, 1], [0, 0]]

# print("triangle", distanceBatiment([0.5, 2], triangle))
# print("carre", distanceBatiment([0.5, 2], carre))
# print("polygone", distanceBatiment([0, 1], polygone))

# print("triangle", distance_polygon([1, 1], triangle))
# print("carre", distance_polygon([0.5, 2], carre))
# print("polygone", distance_polygon([0, 1], polygone))
