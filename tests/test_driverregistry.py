from unittest import TestCase
from worckvm import driver_registry


class RegistryTests(TestCase):
    def setUp(self):
        driver_registry._reset()

    def test_constructing_a_driver_instance_caches_it(self):
        x = object()
        driver_registry.register(x, name="test")
        self.assertIs(driver_registry.get("test"), x)
