
from .IGN_API import IGNTest
from .getImage import GetImageTest

import sys

sys.path.append('../surface_estimator')

from surface_estimator import SurfaceController
import unittest



class MainTest(unittest.TestCase):

    def test_main(self):
        print("----- End To End -----")
        controller = SurfaceController()
        controller.set_coordinates((2.1120532, 48.8606862))
        controller.set_surface()
        self.assertAlmostEqual(int(controller.computedSurf), 218)


if __name__ == 'test.main':
    unittest.main()
