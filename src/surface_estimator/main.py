from .algorithmes.calcul_surface import surface
from .algorithmes.closest import closestBuilding, getClosestBuildings, extractCoordinates, closestCenter
from .IGN_API import IGN_API
from .coordonnees.conversion import buildingGPS2plan, gps2plan
from .coordonnees.coordinates import getLocationFromAddress
from .coordonnees.preciseCoordinates import getLocation
from .utils import getXY, distancePoint, taille
from .getImage import ImagesController
import matplotlib.pyplot as plt
import json

maxDist = 50


class SurfaceController():
    def __init__(self, imgCtrl: ImagesController, ignApi: IGN_API, closestFunction=closestBuilding, MAJ=False):
        self.imgCtrl = imgCtrl
        self.IGNAPI = ignApi
        self.MAJ = MAJ
        self.closestFunction = closestFunction
        self.coordinates = None
        self.ville = None
        self.code = None
        self.data = None
        self.dt = None
        self.address = None
        self.closest = None
        self.computedSurf = None

    def update(self):
        self.set_ville()
        self.set_ville_data()
        self.set_closest()

    def set_ville(self):
        ville, code = self.IGNAPI.getVille(self.coordinates)
        self.ville = ville
        self.code = code
        if self.ville == None or self.code == None:
            print("City not found")
        return -1

    def set_ville_data(self):
        self.data, self.dt = self.IGNAPI.getData(self.code, self.MAJ)

    def set_coordinates(self, coordinates):
        self.coordinates = coordinates
        self.update()

    def set_address(self, address):
        self.address = address
        coordinates = getLocationFromAddress(self.address)
        self.set_coordinates(coordinates)

    def set_coordinates_with_geoloc(self):
        res = getLocation()
        coordinates = [float(res[1]), float(res[0])]
        set_coordinates(self, coordinates)

    def set_closest(self):
        if self.coordinates is None:
            return None
        else:
            self.closest = self.closestFunction(self.coordinates, self.data)

    def set_surface(self):
        coords = extractCoordinates(self.closest)
        planCoords = buildingGPS2plan(coords)
        self.computedSurf = surface(planCoords)

    def compare(self, givenSurface):
        if self.computedSurf is None:
            self.set_surface()
        return abs(givenSurface - self.computedSurf)/givenSurface

    def get_surroundings(self, radius):
        closestList = getClosestBuildings(self.coordinates, self.data, radius)
        surroundings = [(buildingGPS2plan(extractCoordinates(close)), close["properties"]["type"])
                        for close in closestList]
        return surroundings

    def get_ratio(self, w, h):
        buildingcoords = extractCoordinates(self.closest)
        planCoords = buildingGPS2plan(buildingcoords)
        DX, DY = taille(planCoords)
        r = min(h/(2*DY), w/(2*DX), 6)
        return r

    def get_image(self, w, h):
        r = self.get_ratio(w, h)
        buildingcoords = extractCoordinates(self.closest)
        n = len(buildingcoords)
        center = [sum([coord[0] for coord in buildingcoords])/n,
                  sum([coord[1] for coord in buildingcoords])/n]
        self.image_coordinates = center
        self.file_name, zone, bbox = self.imgCtrl.getPlottedPlan(center, buildingcoords, self.code, r, w, h)

    def doThePlot(self, w, h):
        r = self.get_ratio(w, h)
        buildingcoords = extractCoordinates(self.closest)
        n = len(buildingcoords)
        center = [sum([coord[0] for coord in buildingcoords])/n,
                  sum([coord[1] for coord in buildingcoords])/n]
        self.image_coordinates = center
        self.imgCtrl.plotOnImage(center, buildingcoords, self.code, r, w, h)



    

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
