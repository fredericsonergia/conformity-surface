from surface_estimator.computer_vision.combine_solutions import SolutionCombiner
import argparse
import configparser
import pickle


class BatchComputer():
    def __init__(self, file_name, MAJ):
        self.file_name = file_name
        self.MAJ = MAJ

    def load_data(self):
        with open(self.file_name) as coordinates_file:
            self.lines = coordinates_file.readlines()
            coordinates_file.close()

    def extract_coordinates(self):
        """
        method to extract the coordinates from the data
        change the method for an other data structure
        """
        self.coordinates = []
        for line in self.lines:
            coords = [float(line.split(";")[0]),
                      float(line.split(";")[1][:-1])]
            self.coordinates.append(coords)

    def get_all(self, w, h, r, R, model):
        """
        Get the corresponding data for all coordinates in the file
        """
        self.result = "["
        for coordinates in self.coordinates:
            sc = SolutionCombiner(coordinates, self.MAJ)
            valid = sc.combine(w, h, r, R)
            if valid == -1:
                print("Invalid Image")
                continue
            sc.get_surfaces()
            sc.get_confidence(model)
            self.result += str(sc) + ",\n"
        self.result += ']'

    def save(self, file_name):
        """
        save the data onto a file
        """
        file = open(file_name, "w")
        file.write(self.result)


ap = argparse.ArgumentParser()
ap.add_argument("-c", "--config", required=True,
                help="path to the configuration file")
ap.add_argument("-m", '--maj', required=False,
                help="update the building data")
args = vars(ap.parse_args())
MAJ = False if "maj" in args.keys() is None else args["maj"]
config = configparser.ConfigParser()
config.read(args["config"])
Image, Batch, Confidence = config['IMAGE'], config['BATCH'], config['CONFIDENCE']
w, h, r, R = int(Image["width in px"]), int(Image["height in px"]), float(
    Image["ratio in px/m"]), float(Image["Radius in m"])
input_file, output_file = Batch["input"], Batch["output"]
model = pickle.load(open(Confidence["path"], 'rb'))

computer = BatchComputer(input_file, args["maj"])
computer.load_data()
computer.extract_coordinates()
computer.get_all(w, h, r, R, model)
computer.save(output_file)
