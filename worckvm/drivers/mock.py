#
# Create some NULL action drivers for testing
# without real hardware.
#

from worchestic.matrix import MatrixDriver
from ..driver_registry import register


class TestDriver(MatrixDriver):
    def select(self, inp, out):
        return None


register(TestDriver(), name="mock")
register(TestDriver(), name="mockhid")
