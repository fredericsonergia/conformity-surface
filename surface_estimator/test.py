
import time
from .algorithmes.closest import closestBuilding, closestCenter
import matplotlib.pyplot as plt
from .main import SurfaceController
import numpy as np
import matplotlib as mpl
mpl.use('MacOSX')

with open("./surface_estimator/test_data/201216_Fichier Cadastre surface.csv", 'r') as f:
    lines = f.readlines()


def getInfos(line):
    splitted = line.lower().split(';')
    for a in splitted[0]:
        if a not in '0123456789':
            print("Not a line")
            return None
    if len(splitted) < 5:
        return None
    address = splitted[1].split(":")[0].split(
        "parcelle")[0] + ', ' + splitted[2]
    surface = splitted[5]
    eps = 1 if "e" in splitted[8] else -1
    coords = [eps*float(splitted[7].replace(',', '.')),
              float(splitted[6].replace(',', '.'))]
    if surface == '':
        print("Surface NaN")
        return None
    for a in surface:
        if a not in '0123456789':
            print("Surface NaN")
            return None
    return address, float(surface), coords


infos = [getInfos(line) for line in lines]

res = []
DT = []
Max = 0
start = time.time()
for info in infos:
    if info != None:
        controller = SurfaceController()
        controller.set_coordinates(info[2])
        controller.set_surface()
        error = controller.compare(info[1])
        res.append(error)
        DT.append(controller.dt)
print(time.time() - start)

print("Temps : ")

plt.hist(DT, range=(0, max(DT)), bins=50)
plt.xlabel('Temps de récupération des données')
plt.ylabel('Nombre de cas')
plt.show()

plt.hist(res, range=(0, 1), bins=50)
plt.xlabel('Erreur relative')
plt.ylabel('Nombre de cas')
mseSurf = 0
i = 0
for errors in res:
    if errors != None:
        mseSurf += errors**2
        i += 1
print(np.sqrt(mseSurf)/i)
plt.show()


print("\n DONE \n")
