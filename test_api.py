import unittest
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from dice import Dice

class TestValidateProbabilities(unittest.TestCase):
    # --- Valid cases ---
    def test_valid_biased(self):
        valid, msg = Dice.validate_probabilities([0.1, 0.2, 0.3, 0.1, 0.2, 0.1])
        self.assertTrue(valid, msg)

    def test_valid_uniform(self):
        valid, msg = Dice.validate_probabilities([1/6, 1/6, 1/6, 1/6, 1/6, 1/6])
        self.assertTrue(valid, msg)

    def test_valid_one_face_certain(self):
        valid, msg = Dice.validate_probabilities([0, 0, 1, 0, 0, 0])
        self.assertTrue(valid, msg)

    def test_valid_integers_accepted(self):
        valid, msg = Dice.validate_probabilities([0, 0, 0, 0, 0, 1])
        self.assertTrue(valid, msg)

    # wrong number of entries
    def test_invalid_too_few(self):
        valid, msg = Dice.validate_probabilities([0.2, 0.2, 0.2, 0.2, 0.2])
        self.assertFalse(valid)
        self.assertIn("6", msg)

    def test_invalid_too_many(self):
        valid, msg = Dice.validate_probabilities([0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.3])
        self.assertFalse(valid)
        self.assertIn("6", msg)

    def test_invalid_empty(self):
        valid, msg = Dice.validate_probabilities([])
        self.assertFalse(valid)

    # wrong sum
    def test_invalid_sum_over_one(self):
        valid, msg = Dice.validate_probabilities([0.2, 0.2, 0.2, 0.2, 0.2, 0.2])  # sum = 1.2
        self.assertFalse(valid)

    def test_invalid_sum_under_one(self):
        valid, msg = Dice.validate_probabilities([0.1, 0.1, 0.1, 0.1, 0.1, 0.1])  # sum = 0.6
        self.assertFalse(valid)

    def test_invalid_all_zeros(self):
        valid, msg = Dice.validate_probabilities([0, 0, 0, 0, 0, 0])
        self.assertFalse(valid)

    # non-numeric / negative
    def test_invalid_contains_string(self):
        valid, msg = Dice.validate_probabilities([0.1, 0.2, 0.3, 0.1, 0.2, "0.1"])
        self.assertFalse(valid)

    def test_invalid_contains_none(self):
        valid, msg = Dice.validate_probabilities([0.1, 0.2, 0.3, 0.1, 0.2, None])
        self.assertFalse(valid)

    def test_invalid_negative(self):
        valid, msg = Dice.validate_probabilities([0.3, 0.2, 0.3, 0.1, 0.2, -0.1])
        self.assertFalse(valid)

    def test_invalid_not_a_list(self):
        valid, msg = Dice.validate_probabilities("0.1,0.2,0.3,0.1,0.2,0.1")
        self.assertFalse(valid)


class TestRollBiasedDice(unittest.TestCase):
    PROBS = [0.1, 0.2, 0.3, 0.1, 0.2, 0.1]
    def test_output_range(self):
        # All values must be between 1 and 6
        results = Dice.roll_biased_dice(self.PROBS, 1000)
        for r in results:
            self.assertGreaterEqual(r, 1)
            self.assertLessEqual(r, 6)

    def test_output_count(self):
        # Must return exactly number_of_random results
        results = Dice.roll_biased_dice(self.PROBS, 50)
        self.assertEqual(len(results), 50)

    def test_output_type(self):
        # Results must be a list of integers
        results = Dice.roll_biased_dice(self.PROBS, 10)
        self.assertIsInstance(results, list)
        for r in results:
            self.assertIsInstance(r, int)

    def test_deterministic_single_face(self):
        # P(6)=1.0 must always produce 6
        results = Dice.roll_biased_dice([0, 0, 0, 0, 0, 1.0], 200)
        self.assertTrue(all(r == 6 for r in results))

    def test_statistical_distribution(self):
        # observed frequency must be within 2% of expected (60,000 rolls)
        n = 60_000
        results = Dice.roll_biased_dice(self.PROBS, n)
        for face, expected_p in enumerate(self.PROBS, start=1):
            observed = results.count(face) / n
            self.assertAlmostEqual(observed, expected_p, delta=0.02,
                msg=f"Face {face}: expected ~{expected_p:.2f}, got {observed:.4f}")

    def test_single_roll(self):
        # A single roll must return a list with one valid value
        results = Dice.roll_biased_dice([1/6]*6, 1)
        self.assertEqual(len(results), 1)
        self.assertIn(results[0], range(1, 7))

    def test_large_batch(self):
        # Should handle large batches without error
        results = Dice.roll_biased_dice([1/6]*6, 100_000)
        self.assertEqual(len(results), 100_000)


if __name__ == "__main__":
    unittest.main(verbosity=2)
