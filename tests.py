import unittest

import compute_ratio_players_vs_reviews


class TestComputeRatioPlayersVsReviewsMethods(unittest.TestCase):
    def test_main(self):
        self.assertTrue(compute_ratio_players_vs_reviews.main())


if __name__ == '__main__':
    unittest.main()
