import io
import yaml

from worchestic.matrix import Matrix

_matrixes = {}


def set_matrix(name, matrix):
    global _matrixes
    _matrixes[name] = matrix


def get_matrix(name):
    return _matrixes[name]


def yaml_tag(name: str):
    def wrap(fn):
        yaml.add_constructor(f"!{name}", fn)
        return fn
    return wrap


@yaml_tag("Matrix")
def build_matrix(loader, node):
    data = loader.construct_mapping(node)
    name = data.get('name')
    namestr = data.get('name', "<Matrix:unknown")
    m = Matrix(
        namestr,
        None,   # TODO Driver
        [None] * data['nr_inputs'],
        data['nr_outputs']
    )
    if name is not None:
        set_matrix(name, m)
    return m


@yaml_tag("MatrixOutput")
def get_matrix_output(loader, node):
    data = loader.construct_mapping(node)
    m = get_matrix(data['name'])
    return m.outputs[data['output_idx']]


def loads(str_data: str):
    return yaml.full_load(io.StringIO(str_data))
