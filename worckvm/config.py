import io
import yaml
from contextlib import suppress
from dataclasses import dataclass
from typing import List

from worchestic.matrix import Matrix
from worchestic.group import SourceGroup, MatrixGroup
from worchestic.signals import Source
from .monitor import Monitor, Adjacency
from .matrixdriver import Driver

_matrixes = {}


class DuplicateConnection(ValueError):
    """Multiple device connected to the same input"""

class MissingConfigKey(ValueError):
    """An expected value was missing from a config object"""

class NoSuchMatrix(KeyError):
    """Cant find a  matching matrix"""

class UnknownDriver(KeyError):
    """Cant find the named driver"""


class DuplicateSourceType(ValueError):
    """A sourceset can only contain a single source of each type"""

class MatrixNotInGroup(ValueError):
    """A Monitor's video must be connected to a matrix in it's matrixgroup"""

def set_matrix(name, matrix):
    global _matrixes
    _matrixes[name] = matrix


def get_matrix(name):
    try:
        return _matrixes[name]
    except KeyError as e:
        raise NoSuchMatrix(*e.args)


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

    try:
        driver = Driver.get(data.get('driver'))
    except KeyError as e:
        raise UnknownDriver(*e.args)

    m = Matrix(
        namestr,
        driver,
        [None] * data['nr_inputs'],
        data['nr_outputs']
    )
    if name is not None:
        set_matrix(name, m)
    return m


@yaml_tag("MatrixDriver")
def build_driver(loader, node):
    """
    YAML constructor to build and register Driver instances from the YAML configuration.
    """
    data = loader.construct_mapping(node)
    name = data.get('name')
    if not name:
        raise ValueError("Driver definition must include a 'name' field.")

    # Create and register the Driver instance
    driver = Driver(name=name)
    return driver


@yaml_tag("MatrixOutput")
def get_matrix_output(loader, node):
    data = loader.construct_mapping(node)
    try:
        m = get_matrix(data['matrix_name'])
        return m.outputs[data['output_idx']]
    except KeyError as e:
        raise MissingConfigKey(*e.args)
    

@yaml_tag("MatrixInput")
class MatrixInputProxy:
    def __init__(self, loader, node):
        data = loader.construct_mapping(node)
        self.matrix = get_matrix(data['matrix_name'])
        self.idx = data['input_idx']

    def set_to(self, src):
        if self.matrix.inputs[self.idx] is not None:
            raise DuplicateConnection()
        self.matrix.replug_input(self.idx, src)


@yaml_tag("MatrixGroup")
def matrixgroup(loader, node):
    data = loader.construct_mapping(node, deep=True)
    mats = {}

    # Process matricies
    try:
        for matrix_name in data['matricies']:
            mats[matrix_name] = get_matrix(matrix_name)
    except KeyError as e:
        raise MissingConfigKey(*e.args)

    # Process source sets.
    groups = {}
    grp_len = len(data['sources'])
    for idx, srcset in enumerate(data['sources']):
        for src_type, src in srcset.sources.items():
            # Assign each source to a SourceGroup type, using the sourceset idx
            # as the soruce idx in that group
            groups.setdefault(src_type, [None] * grp_len)[idx] = src

    return MatrixGroup(SourceGroup(**groups), **mats)


@yaml_tag("Layout")
def set_layout(loader, node):
    data = loader.construct_mapping(node, deep=True)
    main_monitor = data['monitor']

    for direction in Adjacency:
        label = f"to_{direction.name.lower()}"
        if neighbour := data.get(label):
            main_monitor.set_neighbour(direction, neighbour)

    return None


@yaml_tag("Monitor")
def make_monitor(loader, node):
    data = loader.construct_mapping(node, deep=True)
    matrixgrp = data['matrix_group']

    def find_matrix_groupname(output):
        for name, mat in matrixgrp.matricies.items():
            if mat is output.port[0]:
                return name
        else:
            raise MatrixNotInGroup(output.port[0].name)

    vid_out = data['connected_to']
    hid_out = data['hid_output']
    extra = {}

    for direction in Adjacency:
        label = f"to_{direction.name.lower()}"
        if neighbour := data.get(label):
            extra[label] = neighbour

    return Monitor(
        matrixgrp,
        vid_out.port[1], find_matrix_groupname(vid_out),
        find_matrix_groupname(hid_out), hid_out.port[1],
        name=data.get('name', ''),
        **extra
    )


@yaml_tag("SourceSet")
class SourceSet:
    ""
    def __init__(self, loader, node):
        data = loader.construct_mapping(node, deep=True)
        self.name = data['name']
        self.sources = {}
        for src in data['sources']:
            src_type = src['type']
            if src_type in self.sources:
                raise DuplicateSourceType(src_type)
            self.sources[src_type] = Source(
                name=src.get('name', f"{self.name} ({src_type})"),
                preferred_out=src.get('preferred_output'),
            )
            if connection := src.get('connected_to'):
                # Connection is expected to in a MatrixInputProxy
                connection.set_to(self.sources[src_type])



def loads(str_data: str):   
    return yaml.full_load(io.StringIO(str_data))
