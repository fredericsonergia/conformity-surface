
import time
from .algorithmes.closest import closestBuilding, closestCenter, extractCoordinates, buildingGPS2plan
from .computer_vision.combine_solutions import SolutionCombiner
import matplotlib.pyplot as plt
from .main import SurfaceController
from .utils import getXY
import scipy.stats as sps
import numpy as np
from sklearn import tree
import pickle
import graphviz 
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


def train(infos, filename):
    Tau, DeltaD, DeltaS, errors = do_the_test(infos)
    X, y = np.transpose([Tau, DeltaD, DeltaS]), [1-error if error < 0.1 else 0 for error in errors]
    clf = tree.DecisionTreeRegressor(max_depth=4)
    clf = clf.fit(X, y)
    dot_data = tree.export_graphviz(clf, out_file=None) 
    pickle.dump(clf, open(filename, 'wb'))
    graph = graphviz.Source(dot_data) 
    graph.render("confidence")
    
def test(infos, model):
    do_the_test(infos, model)

def do_the_test(infos, model=None):
    errors = []
    Tau = []
    DeltaD = []
    DeltaS = []
    confidence = []
    thresh = 0.1
    i = 0
    file = open("./surface_estimator/test_data/result.csv", "w")
    for info in infos:
        if info != None:
            sc = SolutionCombiner(info[2])
            valid = sc.combine(800, 400, 6, 100)
            if valid == -1:
                continue
            sc.get_surfaces()
            sc.get_confidence(model)
            surf = sc.surfaces[sc.building_index][0]
            error = abs((surf - info[1])/info[1])
            print("score de confiance", sc.conf)
            print("pourcentage d'erreur", error)
            i += 1
            if error > 0:
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
    return Tau, DeltaD, DeltaS, errors

start = time.time()

filename = "./surface_estimator/test_data/binary_model.sav"
# train(infos, filename)
loaded_model = pickle.load(open(filename, 'rb'))
test(infos, loaded_model)

print(time.time()-start)
print("\n DONE \n")
