from enum import Enum
from dataclasses import dataclass
from typing import ForwardRef
from worchestic.matrix import InputSignal
import logging


logger = logging.getLogger(__name__)


class InconsistentLayout(ValueError):
    pass


class Adjacency(Enum):
    LEFT = 0b00
    RIGHT = 0b01
    TOP = 0b10
    BOTTOM = 0b11

    def opposite(self):
        return self.__class__(self.value ^ 1)


class Monitor:
    """A monitor represent a sink for a source, and is normally
    statically connected to a single MatrixOutput

    Multiple monitor may have a 'postional' relationship such
    as LEFT, or RIGHT of each other. This positioning information
    can be used for UI hinting, but has little direct use.
    mostly
    """

    @dataclass
    class Status:
        source: InputSignal
        has_hid: bool

    def __init__(self, matrixgrp, video_out_idx: int,
                 video_group_name='video',
                 hid_group_name='hid',
                 hid_output_idx=0, **kwargs):
        """
        @param: matrixgrp:  The matrixgrp connected to rhis Monitor
        @param: video_out_idx int: The video output of the matrix group for
                    this monitor
        @param: video_group_name str: The name of sub matrix in the matrix
                    group which handles the video for this monitor
        @param: hid_group_name str: The name of sub matrix in the matrix
                    group which handles the hid devices sed for this monitor
        @param: hid_group_name str: The idx of the output of thre hid sub
                    matrix used for this monitor's hid companions
        """
        self.matrixgrp = matrixgrp
        self.video_out_idx = video_out_idx
        self.video_group_name = video_group_name
        self.hid_output_idx = hid_output_idx
        self.hid_group_name = hid_group_name
        self.output = matrixgrp.get_output(video_group_name, video_out_idx)
        self.neighbours = {}
        for direction in Adjacency:
            if neighbour := kwargs.get(f"to_{direction.name.lower()}"):
                opdir = direction.opposite()
                neighbour.set_neighbour(opdir, self)
                self.neighbours[direction] = neighbour

    def set_neighbour(self, direction: Adjacency, neighbour: ForwardRef('Monitor')):
        if extant := self.neighbour_to(direction) is not None:
            raise InconsistentLayout(
                f"{extant} is already {direction} from {self}"
            )
        self.neighbours[direction] = neighbour

    def neighbour_to(self, direction: Adjacency):
        return self.neighbours.get(direction)

    def grab_hid(self):
        return None

    def get_status(self):
        companions = self.matrixgrp.signals.get_companions(self.output.source)
        current_hid = self.matrixgrp.get_output(
            self.hid_group_name, self.hid_output_idx
        )
        print("E")
        print(f"hid current:{current_hid.source}, vid companions: {companions}")
        return self.Status(
            source=self.output.source,
            has_hid=(current_hid.source in companions)
        )

    def select(self, source):
        self.matrixgrp.select(self.video_group_name, self.video_out_idx, source)
