#!/bin/python3

from askcryptobot import get_crypto_dict
import unittest


class test_scenarios(unittest.TestCase):
    def test_basic(self):
        testcase = "non_symbol"
        expected = None
        self.assertEqual(get_crypto_dict(testcase), expected)

    def test_basic2(self):
        testcase = "symbol"
        not_expected = None
        self.assertNotEqual(get_crypto_dict(testcase), not_expected)


if __name__ == "__main__":
    unittest.main()
