import unittest
from surface.surface_estimator import IGN_API

class IGNTest(unittest.TestCase):

    def test_getVille(self):
        print("_____ Ville _____")
        ville, code = IGN_API.getVille((2.1120532, 48.8606862))
        self.assertEqual(ville.lower(), 'louveciennes')
        self.assertEqual(code, "78350")

    def test_retrieveData(self):
        print("_____ Retrieve Data _____")
        dep = "78350"
        output = "cadastre-"+dep+"-batiments.json"
        self.assertEqual(type(IGN_API.retrieveData(dep, output)), float)

    def test_getData(self):
        print("_____ Get Data _____")
        dep = "78350"
        data, dt = IGN_API.getData(dep)
        self.assertEqual(list(data.keys()), ['type', 'features'])
