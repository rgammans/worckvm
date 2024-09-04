from monitor import Monitor
from typing import List, Dict
import serialisers as ser


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
            name=m.name,
            uuid=m.uuid,
            status=ser.MonitorStatus.of(m),
            neighbours={k: v.uuid for k, v in m.neighbours.items()},
        )
        for m in Monitor.list()
    ]
