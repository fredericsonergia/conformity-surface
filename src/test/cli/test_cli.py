import sys

sys.path.append("./src")

import cli.batchs as b
import cli.confidence as c
import os
import unittest
import pickle
import json

class TestStringMethods(unittest.TestCase):

    def test_batch(self):
        print("----- Test Batch -----")

        static = "src/test/test_data/static/"
        data = "src/test/test_data/data/"
        file = "src/test/test_data/batch/coords_test.csv"
        output_file = "src/test/test_data/batch/output_test.json"
        w, h, r, R = 800, 400, 6, 100
        model = pickle.load(open("src/test/test_data/confidence/binary_model.sav", 'rb'))
        computer = b.BatchComputer(static_path=static, data_path=data, file_name=file, MAJ=True)
        computer.load_data()
        computer.extract_coordinates()
        computer.get_all(w, h, r, R, model)
        computer.save(output_file)
        output =  open(output_file, 'r')
        json_dict = json.loads(output.read())[0]
        surface = json_dict["surface"]
        self.assertEqual(surface, 216.453923143839)
        self.assertEqual(json_dict["coords"], [2.1120532, 48.860686])
        self.assertTrue("/static/2.1120532,48.860686/205,4020,1,2,3,4,5,6,7,8,9.png" in json_dict["fileName"])
        self.assertEqual(json_dict["metrics"], [{"label": "Tau", "value": 0.06348497868865254}, 
                                                {"label": "DeltaD", "value": 0.5897052965699509}, 
                                                {"label": "DeltaS", "value": 1.6850046734951682}, 
                                                {"label": "TauLignes", "value": 0.018989951677547655}, 
                                                {"label": "conf", "value": 1.0}])
        output.close()
        os.remove(output_file)


    def test_confidence_test(self):
        print("----- Test Confidence Test -----")

        config_file = "src/test/test_data/test.config"
        output_file = "src/test/test_data/confidence/test_output.csv"
        builder = c.ConfidenceBuilder(config_file)
        builder.test(save=True, output_file=output_file)
        file =  open(output_file, 'r')
        output = file.read()
        wanted_output = '1;0,1174407861849998;1,0308625988989482;0,5117576050523772;0,08858009333742663;0,04182347754459609\n'
        self.assertEqual(output, wanted_output)
        file.close()
        os.remove(output_file)
        
    
if __name__ == '__main__':
    unittest.main()