from .ble import run_ble
from .matrixdriver import Driver
from .config import loads


class TestDriver(Driver):
    def select(self, inp, out):
        return None


mockdriver = TestDriver(name="mock")
mockdriver = TestDriver(name="mockhid")


system = loads(open("examples/simple_kvm_combined.yaml").read())
run_ble()
