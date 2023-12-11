from unittest import TestCase
from worckvm import matrixdriver


class DriverTests(TestCase):
    def setUp(self):
        pass

    def test_constructing_a_driver_instance_caches_it(self):
        x = matrixdriver.Driver(name="test")
        self.assertIs(x, matrixdriver.Driver.get("test"))

    def test_driver_has_an_nyi_method_select(self):
        x = matrixdriver.Driver(name="test2")
        with self.assertRaises(NotImplementedError):
            x.select(1, 2)
