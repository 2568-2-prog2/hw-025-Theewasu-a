import unittest
import json
import threading
import time
import requests
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from basic_http import run_server

TEST_HOST = "127.0.0.1"
TEST_PORT = 8082
BASE_URL  = f"http://{TEST_HOST}:{TEST_PORT}/roll_dice"

_server_thread = threading.Thread(target=run_server, args=(TEST_HOST, TEST_PORT), daemon=True)
_server_thread.start()
time.sleep(0.5)


class TestIntegration(unittest.TestCase):

    PROBS = [0.1, 0.2, 0.3, 0.1, 0.2, 0.1]

    def test_server_accepts_get(self):
        resp = requests.get(BASE_URL, json={"probabilities": self.PROBS, "number_of_random": 5})
        self.assertEqual(resp.status_code, 200)

    def test_server_accepts_post(self):
        resp = requests.post(BASE_URL, json={"probabilities": self.PROBS, "number_of_random": 5})
        self.assertEqual(resp.status_code, 200)

    def test_response_is_valid_json(self):
        resp = requests.get(BASE_URL, json={"probabilities": self.PROBS, "number_of_random": 5})
        self.assertIsInstance(resp.json(), dict)

    def test_response_has_required_fields(self):
        resp = requests.get(BASE_URL, json={"probabilities": self.PROBS, "number_of_random": 10})
        data = resp.json()
        self.assertIn("status", data)
        self.assertIn("probabilities", data)
        self.assertIn("dices", data)

    def test_dices_correct_count(self):
        resp = requests.get(BASE_URL, json={"probabilities": self.PROBS, "number_of_random": 15})
        self.assertEqual(len(resp.json()["dices"]), 15)

    def test_dices_values_in_range(self):
        resp = requests.get(BASE_URL, json={"probabilities": self.PROBS, "number_of_random": 200})
        for d in resp.json()["dices"]:
            self.assertIn(d, range(1, 7))

    def test_echoes_probabilities(self):
        resp = requests.get(BASE_URL, json={"probabilities": self.PROBS, "number_of_random": 5})
        self.assertEqual(resp.json()["probabilities"], self.PROBS)

    def test_status_is_success(self):
        resp = requests.get(BASE_URL, json={"probabilities": self.PROBS, "number_of_random": 5})
        self.assertEqual(resp.json()["status"], "success")

    def test_invalid_probs_returns_400(self):
        resp = requests.get(BASE_URL, json={"probabilities": [0.2]*6, "number_of_random": 5})
        self.assertEqual(resp.status_code, 400)

    def test_missing_probs_returns_400(self):
        resp = requests.get(BASE_URL, json={"number_of_random": 5})
        self.assertEqual(resp.status_code, 400)

    def test_error_response_has_message(self):
        resp = requests.get(BASE_URL, json={"number_of_random": 5})
        data = resp.json()
        self.assertIn("message", data)
        self.assertEqual(data["status"], "error")

    def test_wrong_endpoint_returns_404(self):
        resp = requests.get(f"http://{TEST_HOST}:{TEST_PORT}/wrong_path",
                            json={"probabilities": self.PROBS})
        self.assertEqual(resp.status_code, 404)


if __name__ == "__main__":
    unittest.main(verbosity=2)