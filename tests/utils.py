from worchestic.matrix import Matrix
from worchestic.signals import Source
from worchestic.group import MatrixGroup, SourceGroup


def make_signal(**kwargs):
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
    hid = [make_signal(), make_signal(), make_signal()]
    mat_video = Matrix("video", MockDriver(), video, 3)
    mat_hid = Matrix("hid", MockDriver(), hid, 1)
    for s in hid:
        s.preferred_out = mat_hid.outputs[0]
    for idx, s in enumerate(video):
        s.preferred_out = mat_video.outputs[idx % 2]
    siggrp = SourceGroup(
        video=video,
        hid=hid,
    )
    return {
        'matrixgrp': MatrixGroup(
            siggrp,
            video=mat_video,
            hid=mat_hid
        ),
        'video0': video[0],
        'video2': video[2],
        'video3': video[3],
        'hid0': hid[0],
        'hid1': hid[1],
    }
