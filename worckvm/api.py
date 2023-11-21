from .monitor import Monitor
from typing import List, Dict
from . import serialisers as ser
from worchestic.signals import Source
#import Source, MonitorStatus


def get_status(monitor) -> ser.MonitorStatus:
    return ser.MonitorStatus.of(monitor)


def grab_hid(monitor) -> Dict:
    monitor.grab_hid()
    return {'success': True}


def available_sources(monitor) -> List[Source]:
    return monitor.available_sources()


def select(monitor, src_id: str):
    src = get_src_by_uuid(monitor,src_id)
    if src is not None:
        monitor.select(src)
        return 'success'
    return 'Source not found'

#
def list_monitor() -> List[ser.Monitor]:
    return [
        ser.Monitor(
            name="",
            uuid=m.uuid,
            status=ser.MonitorStatus.of(m),
            neighbours=m.neighbours
        )
        for m in Monitor.list()
    ]


def get_monitor_by_uuid(uuid=None) -> Monitor:
    for m in Monitor.list():
        if str(m.uuid).lower() == str(uuid).lower():
            return m
    return None

def get_src_by_uuid(monitor, src_id) -> Source:
    src = available_sources(monitor)
    for s in src:
        if s is not None and str(s.uuid).lower() == str(src_id).lower():
            return s
    return None
   