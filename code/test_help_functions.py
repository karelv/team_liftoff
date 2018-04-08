import unittest
from help_functions import distance

class TestDistance(unittest.TestCase):

    def test_distance(self):
            self.assertAlmostEqual(distance((53.2194, 6.5665),(53.2144, 6.5625)) ,  0.616666274341978)

if __name__ == '__main__':
    unittest.main()
