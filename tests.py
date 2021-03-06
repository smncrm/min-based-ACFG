import unittest
import min_acfg


class MyTestCase(unittest.TestCase):
    def test_construct_structure(self):
        g = [[0, 1, 2], [3, 4], [5]]
        d = [[5], [4, 3], [2, 0, 1]]

        gamma = min_acfg.Structure(g)
        delta = min_acfg.Structure(d)
        self.assertEqual(gamma, delta)

    def test_move_empty_coalition(self):
        g = [[0, 1, 2], [3, 4], [5]]
        c = []

        self.assertEqual(min_acfg.Structure(g).move_coalition(c),
                         min_acfg.Structure(g))

    def test_move_existing_coalition(self):
        g = [[0, 1, 2], [3, 4], [5]]
        c = [0, 1, 2]

        self.assertEqual(min_acfg.Structure(g).move_coalition(c),
                         min_acfg.Structure(g))

    def test_move_all_coalitions(self):
        g = [[0, 1, 2], [3, 4], [5]]
        c = [0, 1, 2, 3, 4, 5]
        g_exp = [[0, 1, 2, 3, 4, 5]]

        self.assertEqual(min_acfg.Structure(g).move_coalition(c),
                         min_acfg.Structure(g_exp))

    def test_move_coalition(self):
        g = [[0, 1, 2], [3, 4], [5]]
        c = [3, 2]
        g_exp = [[0, 1], [2, 3], [4], [5]]

        self.assertEqual(min_acfg.Structure(g).move_coalition(c),
                         min_acfg.Structure(g_exp))

    def test_calc_value_alone(self):
        v = min_acfg.calc_value([1], 4, 1, [2, 3])
        self.assertEqual(v, 0)

    def test_calc_value_alone_and_no_friends(self):
        v = min_acfg.calc_value([1], 4, 1, [])
        self.assertEqual(v, 0)

    def test_calc_value_only_enemies(self):
        n = 5
        v = min_acfg.calc_value([1, 4, 5], n, 1, [2, 3])
        self.assertEqual(v, -2)

    def test_compare_structures(self):
        uts_g = [0, 10, 15, -5]
        uts_d = [5, 10, 10, -10]

        self.assertEqual(min_acfg.compare_structures(uts_g, uts_d), 1)

    def test_compare_structures_eq(self):
        uts_g = [0, 10, 15, -5]
        uts_d = [5, 10, 10, -5]

        self.assertEqual(min_acfg.compare_structures(uts_g, uts_d), 0)


if __name__ == '__main__':
    unittest.main()
