
import time
from .algorithmes.closest import closestBuilding, closestCenter, extractCoordinates, buildingGPS2plan
from .computer_vision.combine_solutions import SolutionCombiner
import matplotlib.pyplot as plt
from .main import SurfaceController
from .utils import getXY
import scipy.stats as sps
import numpy as np
import matplotlib as mpl
mpl.use("MacOSX")

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


def do_the_test(infos):
    errors = []
    Tau = []
    DeltaD = []
    DeltaS = []
    confidence = []
    i = 0
    file = open("./surface_estimator/test_data/result.csv", "w")
    for info in infos:
        if info != None:
            sc = SolutionCombiner(info[2])
            valid = sc.combine(800, 400, 6, 100)
            if valid == -1:
                continue
            sc.get_surfaces()
            sc.get_confidence()
            surf = sc.surfaces[sc.building_index][0]
            error = abs((surf - info[1])/info[1])
            print("score de confiance", sc.conf)
            print("pourcentage d'erreur", error)
            i += 1
            if error > .1:
                Tau.append(sc.tU)
                DeltaD.append(sc.DeltaD)
                DeltaS.append(sc.DeltaS)
                errors.append(error**2)
                confidence.append(sc.conf)
                line = str(i) + ";" + str(error) + ";" + str(sc.DeltaS) + ";" + \
                    str(sc.DeltaD) + ";" + str(sc.tU) + \
                    ";" + str(sc.conf) + "\n"
                file.write(line)

    file.close()
    print(np.sqrt(sum(errors))/len(errors))
    print("Conf :", sps.stats.pearsonr(confidence, errors))
    print("DeltaD :", sps.stats.pearsonr(DeltaD, errors))
    print("DeltaS :", sps.stats.pearsonr(DeltaS, errors))
    print("Tau :", sps.stats.pearsonr(Tau, errors))

    plt.hist(np.log(errors)/np.log(10), range=(min(np.log(errors) /
                                                   np.log(10)), max(np.log(errors)/np.log(10))), bins=50)
    plt.xlabel('Erreur relative')
    plt.ylabel('Nombre de cas')
    plt.show()


print("\n DONE \n")
