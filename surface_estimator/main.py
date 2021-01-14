from .calcul import surface
from .closest import closestBuilding, getClosestBuildings, extractCoordinates, closestCenter
from .archive import getVille, getData
from .conversion import buildingGPS2plan, gps2plan
from .coordinates import getLocationFromAddress
from .utils import getXY, distancePoint
from .getImage import plotOnImage, getPlottedPlan
import matplotlib.pyplot as plt
import json

maxDist = 50

# address = input("Entrez votre adresse ('' = géolocalisation) : ")


def main(info, closestFunction=closestCenter, doThePlot=False):
    address, testSurf, testCoords = info
    if address != '':
        coordinates = getLocationFromAddress(address)
        if coordinates == None:
            print(address)
            coordinates = testCoords
    else:
        from .preciseCoordinates import coordinates as coord
        coordinates = coord
    # coordinates1 = [2.1378258,43.92235001023937]
    # coordinates = [2.1378258,48.882290575830936]
    MAJ = False
    R = 100
    coordinates = testCoords

    distanceTest = distancePoint(gps2plan(testCoords), gps2plan(coordinates))
    if distanceTest > R:
        coordinates = testCoords
        distanceTest = distancePoint(
            gps2plan(testCoords), gps2plan(coordinates))

    ville, code = getVille(coordinates)
    if ville == None or code == None:
        print("City not found")
        return None
    print(ville, code)
    data, dt = getData(code, MAJ)
    closest = closestFunction(coordinates, data)
    testClosest = closestFunction(testCoords, data)
    closestList = getClosestBuildings(coordinates, data, R)
    coords = extractCoordinates(closest)
    buildingCoords = extractCoordinates(testClosest)
    planCoords = buildingGPS2plan(coords)
    testPlanCoords = buildingGPS2plan(buildingCoords)
    surroundings = [buildingGPS2plan(extractCoordinates(close))
                    for close in closestList]
    computedSurf = surface(planCoords)
    print(testSurf, computedSurf)
    getPlottedPlan(testCoords, buildingCoords)
    if doThePlot:
        print(planCoords)
        print(info, coordinates)
        plotOnImage(testCoords, buildingCoords)
        # plot(surroundings, planCoords, coordinates, testPlanCoords, testCoords)
        # plt.show()
    # print(computedSurf, "m2")

    return str(computedSurf)


def plot(surroundings, planCoords, coordinates, testPlanCoords, testCoords):
    for building in surroundings:
        x, y = getXY(building)
        plt.plot(x, y, color='blue')

    plt.scatter(gps2plan(coordinates)[0],
                gps2plan(coordinates)[1], color="red")
    plt.scatter(gps2plan(testCoords)[0], gps2plan(
        testCoords)[1], color="green")

    x, y = getXY(planCoords)
    plt.plot(x, y, color='red')
    x, y = getXY(testPlanCoords)
    plt.plot(x, y, color='green')


# print(main(("adress", 1, (4.70777, 45.876799)), closestBuilding, doThePlot=True))
