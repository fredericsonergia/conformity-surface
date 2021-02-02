from .computer_vision.combine_solutions import SolutionCombiner


class BatchComputer():
    def __init__(self):
        pass

    def load_data(self, file_name):
        with open(file_name) as coordinates_file:
            self.lines = coordinates_file.readlines()
            coordinates_file.close()

    def extract_coordinates(self):
        """
        method to extract the coordinates from the data
        change the method for an other data structure
        """
        self.coordinates = self.lines

    def get_all(self, w, h, r, R):
        """
        Get the corresponding data for all coordinates in the file
        """
        res = ""
        for coordinates in self.coordinates:
            sc = SolutionCombiner(coordinates)
            valid = sc.combine(w, h, r, R)
            if valid == -1:
                return FileNotFoundError
            sc.get_surfaces()
            sc.get_confidence()
            res += str(sc) + "\n"
        self.result = res
    
    def save(self, file_name):
        """
        save the data onto a file
        """
        file = open(file_name, "w")
        file.write(self.result)