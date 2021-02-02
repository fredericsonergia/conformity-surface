from surface_estimator.computer_vision.combine_solutions import SolutionCombiner
import argparse


class BatchComputer():
    def __init__(self, file_name):
        self.file_name = file_name

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
            coords = [float(line.split(";")[0]), float(line.split(";")[1][:-1])]
            self.coordinates.append(coords)

    def get_all(self, w, h, r, R):
        """
        Get the corresponding data for all coordinates in the file
        """
        self.result = ""
        for coordinates in self.coordinates:
            sc = SolutionCombiner(coordinates)
            valid = sc.combine(w, h, r, R)
            if valid == -1:
                return FileNotFoundError
            sc.get_surfaces()
            sc.get_confidence()
            self.result += str(sc) + "\n"
        self.result
    
    def save(self, file_name):
        """
        save the data onto a file
        """
        file = open(file_name, "w")
        file.write(self.result)

w, h, r, R, = 800, 400, 6, 100

ap = argparse.ArgumentParser()
ap.add_argument("-i", "--input", required=True,
	help="path to the input file")
ap.add_argument("-o", "--output", required=True,
	help="path to the ouptut file")
args = vars(ap.parse_args())
computer = BatchComputer(args["input"])
computer.load_data()
computer.extract_coordinates()
computer.get_all(w, h, r, R)
computer.save(args["output"])
