
import time
import fire
import sys
sys.path.append("../")

from surface_estimator.algorithmes.closest import closestBuilding, closestCenter, extractCoordinates, buildingGPS2plan
from surface_estimator.computer_vision.combine_solutions import SolutionCombiner
import matplotlib.pyplot as plt
from surface_estimator.main import SurfaceController
from surface_estimator.utils import getXY
import scipy.stats as sps
import numpy as np
from sklearn import tree
import pickle
import graphviz
import matplotlib as mpl
import argparse
import configparser
from surface_estimator.getImage import ImagesController
from surface_estimator.IGN_API import IGN_API
mpl.use("MacOSX")

class ConfidenceBuilder(object):
    def __init__(self, config_file):

        config = configparser.ConfigParser()
        config.read(config_file)
        Image, Batch, Confidence, Data = config['IMAGE'], config['BATCH'], config['CONFIDENCE'], config['DATA']

        self.w, self.h, self.r, self.R = int(Image["width in px"]), int(Image["height in px"]), float(
            Image["ratio in px/m"]), float(Image["Radius in m"])
        self.train_input_file = Confidence["train_set_file"]
        self.data_output = Confidence["result_output"]
        self.test_input_file = Confidence["test_set_file"]
        self.model_path = Confidence["model_path"]
        data_path, static_path = Data["data_path"], Data["static_path"]
        self.imgCtrl = ImagesController(static_path)
        self.ign = IGN_API(data_path)

    def _set_train_file(self, file_name):
        with open(file_name, 'r') as f:
            train = f.readlines()
        self.train = [self._getInfos(line) for line in train]

    def _set_test_file(self, file_name):
        with open(file_name, 'r') as f:
            test = f.readlines()
        self.test = [self._getInfos(line) for line in test]


    def _getInfos(self, line):
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

    def train(self, max_depth=10, min_samples_leaf=5, method="binary", save=False, output_file=None):
        self._set_train_file(self.train_input_file)
        model_filename = self.model_path
        infos = self.train
        Tau, DeltaD, DeltaS, TauLignes, errors = self._do_the_test(infos, save=save, output_file=output_file)
        X, y = np.transpose([Tau, DeltaD, DeltaS, TauLignes])
        if method == "binary":
            y = [1 if error < .1 else 0 for error in errors]
        elif method == "regression": 
            y = [1 if error < 1 else 0 for error in errors]
        else: 
            print("no method defined")
            return None
        clf = tree.DecisionTreeRegressor(max_depth=max_depth, min_samples_leaf=min_samples_leaf)
        clf = clf.fit(X, y)
        dot_data = tree.export_graphviz(clf, out_file=None)
        pickle.dump(clf, open(model_filename, 'wb'))
        graph = graphviz.Source(dot_data)
        graph.render("confidence")

    def test(self, save=False, output_file=None):
        model_filename = self.model_path
        self._set_test_file(self.test_input_file)
        model = pickle.load(open(model_filename, 'rb'))
        loaded_model = pickle.load(open(model_filename, 'rb'))
        test_dataset = self.test
        self._do_the_test(test_dataset, model, save=save, output_file=output_file)


    def _do_the_test(self, infos, model=None, save=False, output_file=None):
        errors = []
        Tau = []
        DeltaD = []
        DeltaS = []
        confidence = []
        TauLignes = []
        thresh = 0.1
        i = 0
        if save:
            if output_file is None:
                print("No output file")
                return None
            else:
                file = open(output_file, "w")
        for info in infos:
            if info != None:
                sc = SolutionCombiner(self.imgCtrl, self.ign, coordinates=info[2])
                valid = sc.combine(self.w, self.h, self.r, self.R)
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
                    TauLignes.append(sc.tLignes)
                    errors.append(error**2)
                    confidence.append(sc.conf)
                    line = str(i) + ";" + str(error) + ";" + str(sc.DeltaS) + ";" + \
                        str(sc.DeltaD) + ";" + str(sc.tU) + \
                        ";" + str(sc.tLignes) + "\n"
                    if save:
                        file.write(line.replace(".", ","))
        file.close()
        return Tau, DeltaD, DeltaS, TauLignes,  errors


if __name__ == '__main__':
    fire.Fire(ConfidenceBuilder)

