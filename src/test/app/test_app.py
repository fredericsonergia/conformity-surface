import unittest
from starlette.testclient import TestClient
import sys
sys.path.append("./src")

import app.main as m # <-- App under Test
import app.config as config
import configparser
import pickle

def get_settings_override():
    configFile = configparser.ConfigParser()
    configFile.read("src/test/test_data/test.config")
    Image, Confidence, Data = configFile['IMAGE'], configFile['CONFIDENCE'], configFile["DATA"]
    w, h, r, R = int(Image["width in px"]), int(Image["height in px"]), float(
        Image["ratio in px/m"]), float(Image["Radius in m"])
    data_path, static_path = Data["data_path"], Data["static_path"]
    model_path = Confidence["model_path"]
    loaded_model = pickle.load(open(Confidence["model_path"], 'rb'))
    return config.Settings(w=w, h=h, r=r, R=R, data_path=data_path, static_path=static_path, loaded_model=loaded_model)


class IntegrationTests(unittest.TestCase):
    def setUp(self):
        self.app = TestClient(m.app)
        m.app.dependency_overrides[m.get_settings] = get_settings_override


    def test_coordinates(self):
        data = {"coordinates": '2.1120532,48.860686'}
        response = self.app.post('/surface/coordinates', json=data)
        self.assertEqual(response.status_code, 200)

    def test_coordinates_fromCV(self):
        data = {"coordinates": '2.1120532,48.860686'}
        response = self.app.post('/surface/coordinates/fromCV', json=data)
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()