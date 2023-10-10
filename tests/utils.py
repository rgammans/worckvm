from worchestic.matrix import Matrix
from worchestic.signals import Source
from worchestic.group import MatrixGroup, SourceGroup


def make_signal():
    """Creates a signal useful for log messages during testing
    Speficically it set the name to the str of the uuid
    """
    s = Source("")
    s.name = str(s.uuid)
    return s


class MockDriver:
    def select(self, *args): pass


def create_fabric():
    """Creates a pair of matrix fabrics (hib & video) close enout
    to the common use cases.

    intended as a backend to help us exercise our tests
    """
    video = [make_signal(), make_signal(), make_signal(), make_signal()]
    hid = [make_signal(), make_signal(), make_signal(), make_signal()]
    mat_video = Matrix("video", MockDriver(), video, 3)
    mat_hid = Matrix("hid", MockDriver(), hid, 1)
    siggrp = SourceGroup(
        video=video,
        hid=hid,
#        assign_outputs={
#            'video': mat_video.outputs[0],
#            'hid': mat_hid.outputs[0],
#        }
    )
    return {
        'matrixgrp': MatrixGroup(
            siggrp,
            video=mat_video,
            hid=mat_hid
        ),
        'video0': video[0],
        'hid0': hid[0],
        'hid1': hid[1],
    }