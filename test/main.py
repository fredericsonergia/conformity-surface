import unittest
import sys
sys.path.append('../')
from surface.surface_estimator import SurfaceController
from IGN_API import IGNTest
from getImage import GetImageTest

class MainTest(unittest.TestCase):

    def test_main(self):
        print("----- End To End -----")
        controller = SurfaceController()
        controller.set_coordinates((2.1120532, 48.8606862))
        controller.set_surface()
        self.assertAlmostEqual(int(controller.computedSurf), 218)


if __name__ == '__main__':
    unittest.main()

