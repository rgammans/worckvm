#
# Create some NULL action drivers for testing
# without real hardware.
#

from ..matrixdriver import Driver

class TestDriver(Driver):
    def select(self, inp, out):
        return None


mockdriver = TestDriver(name="mock")
mockdriver = TestDriver(name="mockhid")
