from enum import Enum
import uuid
from dataclasses import dataclass
from typing import ForwardRef
from worchestic.signals import Source
import logging


logger = logging.getLogger(__name__)


class WorcKVMError(Exception):
    pass

class InconsistentLayout(ValueError, WorcKVMError):
    pass
class NoMatchingHIDFound(ValueError, WorcKVMError):
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
    _registry = {}

    @dataclass
    class Status:
        source: Source
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
        self.uuid = self.register(self)
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

    @classmethod
    def register(kls, self):
        guid = uuid.uuid4()
        kls._registry[guid] = self
        return guid

    @classmethod
    def list(kls):
        return kls._registry.values()

    @classmethod
    def reset_registry(kls):
        """Forget all previous;y created monitors.

        mostly useful of ensuring tests are indepedent
        """
        kls._registry = {}

    @classmethod
    def get(kls, guid):
        return kls._registry[guid]

    def set_neighbour(self, direction: Adjacency, neighbour: ForwardRef('Monitor')):
        if extant := self.neighbour_to(direction) is not None:
            raise InconsistentLayout(
                f"{extant} is already {direction} from {self}"
            )
        self.neighbours[direction] = neighbour

    def neighbour_to(self, direction: Adjacency):
        return self.neighbours.get(direction)

    def grab_hid(self):
        companions = self.matrixgrp.signals.get_companions(self.output.source)
        current_hid = self.matrixgrp.get_output(
            self.hid_group_name, self.hid_output_idx
        )
        if not (current_hid.source in companions):
            # HID is not one ouf our companions.
            # so find a HId routeable companion
            hids = self.matrixgrp.available(self.hid_group_name)
            try:
                my_hid = _first(hids & companions)
            except StopIteration:
                raise NoMatchingHIDFound(companions)
            self.matrixgrp.select(
                self.hid_group_name,
                self.hid_output_idx,
                my_hid, no_companions=True  # don't encourage other changes.
            )
            current_hid = self.matrixgrp.get_output(
                self.hid_group_name, self.hid_output_idx
            )

    def get_status(self):
        companions = self.matrixgrp.signals.get_companions(self.output.source)
        current_hid = self.matrixgrp.get_output(
            self.hid_group_name, self.hid_output_idx
        )
        return self.Status(
            source=self.output.source,
            has_hid=(current_hid.source in companions)
        )

    def select(self, source):
        self.matrixgrp.select(self.video_group_name, self.video_out_idx, source)

    def available_sources(self):
        src = self.matrixgrp.available(self.video_group_name)
        return (  # Bracket to allow wrapping..
            [s for s in src if s.preferred_out is self.output] +
            [s for s in src if s.preferred_out is not self.output]
        )

def _first(seq):
    "returns the first element in a seq"
    return next(iter(seq))
