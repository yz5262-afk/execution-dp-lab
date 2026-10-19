import unittest
from execution_dp import exact_dp,brute_force,approximate_dp
class DPTests(unittest.TestCase):
    def test_exact_matches_enumeration(self):
        for alpha,pi in [(0.001,0.5),(0.12,0.7)]:
            for n,t in [(8,3),(12,4),(18,3)]:
                result=exact_dp(n,t,alpha,pi)
                self.assertEqual(result['total'],brute_force(n,t,alpha,pi)[0])
                self.assertEqual(sum(result['schedule']),n)
    def test_grid_solution_never_exceeds_exact(self):
        for n in [12,18,24]:
            self.assertLessEqual(approximate_dp(n,3,order_step=3)['total'],exact_dp(n,3)['total'])
if __name__=='__main__': unittest.main()
