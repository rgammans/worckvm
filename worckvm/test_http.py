from http_app import app  # noqa: F401
from matrixdriver import Driver
from config import loads


class TestDriver(Driver):
    def select(self, inp, out):
        return None


mockdriver = TestDriver(name="mock")
mockdriver = TestDriver(name="mockhid")


system = loads(open("examples/simple_kvm_combined.yaml").read())
