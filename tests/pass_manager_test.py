import unittest
import random

from DesktopPdf.managers import PassManager, get_random_digits


class TestManagers(unittest.TestCase):
    def test_random_digits(self):
        for n in range(15):
            for _ in range(10_000):
                random_digits = get_random_digits(n=n)
                self.assertEqual(len(random_digits), n)

    def test_registering(self):
        pass_manager = PassManager()

        new_ip = "0.0.0.0"

        pass_manager.register_ip(new_ip)

        self.assertEqual(len(pass_manager._ips_with_access), 2)
        self.assertEqual(pass_manager._ips_with_access[1], new_ip)

if __name__ == "__main__":
    unittest.main()
