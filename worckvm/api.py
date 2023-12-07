from .monitor import Monitor
from typing import List, Dict
from . import serialisers as ser


def get_status(monitor) -> ser.MonitorStatus:
    return ser.MonitorStatus.of(monitor)


def grab_hid(monitor) -> Dict:
    monitor.grab_hid()
    return {'success': True}


def available_sources(monitor) -> List[ser.Source]:
    return monitor.available_sources()


def select(monitor, source):
    monitor.select(source)


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
