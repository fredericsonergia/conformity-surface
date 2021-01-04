import numpy as np
from conversion import gps2plan
from utils import distancePoint



def distanceBatiment(point, batiment):
    minDist = float("inf")
    for pointBat in batiment:
        dist = distancePoint(gps2plan(point), gps2plan(pointBat))
        if dist < minDist: 
            minDist = dist
    return minDist

def closestBuilding(point, cityData):
    closest = []
    minDist = float("inf")
    features = cityData["features"]
    for building in features:
        coordinates = building["geometry"]["coordinates"][0][0]
        dist = distanceBatiment(point, coordinates)
        if dist < minDist:
            minDist = dist
            closest = building
    return closest

