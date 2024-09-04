

class Driver:
    _registry = {}

    def __init__(self, *args, **kwargs):
        self.name = kwargs.pop('name')
        self._registry[self.name] = self
        super().__init__(*args, **kwargs)

    @classmethod
    def get(kls, name):
        return kls._registry[name]

    def select(self, inp, out):
        pass
        #raise NotImplementedError("Implement this is you own driver")
