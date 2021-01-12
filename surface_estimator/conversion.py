import numpy as np

RT = 6371008

longueur1degre = RT*np.pi/180

def gps2plan(coordinatesDegre):
    xDeg, yDeg = coordinatesDegre
    y = yDeg * longueur1degre
    x = xDeg * np.cos(yDeg*np.pi/180) * longueur1degre
    return x, y

def buildingGPS2plan(building):
    return [gps2plan(coord) for coord in building]

