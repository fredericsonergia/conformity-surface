from calcul import surface
from closest import closestBuilding
from archive import getVille, getData
from conversion import buildingGPS2plan, gps2plan
from coordinates import getLocationFromAddress
from utils import getXY
import matplotlib.pyplot as plt
import json

address = input("Entrez votre adresse ('' = géolocalisation) : ")

if address != '':
    coordinates = getLocationFromAddress(address)
else: 
    from preciseCoordinates import coordinates as coord
    coordinates = coord
# coordinates1 = [2.1378258,43.92235001023937]
# coordinates = [2.1378258,48.882290575830936]
print(coordinates)

MAJ = False

ville, code = getVille(coordinates)
print(ville, code)
data = getData(code, MAJ)

closest = closestBuilding(coordinates, data)
coords = closest["geometry"]["coordinates"][0][0]
planCoords = buildingGPS2plan(coords)


x,y = getXY(planCoords)

plt.plot(x,y)
print(surface(planCoords), "m2")
plt.show()
