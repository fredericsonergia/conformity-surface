import unittest
from surface.surface_estimator import getImage

class GetImageTest(unittest.TestCase):
    def test_getImage(self):
        print("image")
        w, h, r = 800, 400, 6
        coords = (2.1120532, 48.8606862)
        code = "78350"
        file_name, zone = getImage.getImage(w, h, r, coords, code)
        self.assertEqual(file_name, "2.1120532,48.8606862.png")
        self.assertEqual(zone, "49")
