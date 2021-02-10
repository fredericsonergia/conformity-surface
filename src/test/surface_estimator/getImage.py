import unittest
from surface.surface_estimator import getImage


class GetImageTest(unittest.TestCase):
    def test_getImage(self):
        print("____ Get Image _____")
        w, h, r = 800, 400, 6
        coords = (2.1120532, 48.8606862)
        code = "78350"
        file_name, zone, bbox = getImage.getImage(w, h, r, coords, code)
        self.assertEqual(file_name, "2.1120532,48.8606862/0,1,2,3,4,5,6,7,8,9.png")
        self.assertEqual(zone, "49")
