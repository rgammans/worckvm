import uuid
from typing import Union
from . import monitor
from pydantic import BaseModel


class Source(BaseModel):
    uuid: uuid.UUID
    name: str


class MonitorStatus(BaseModel):
    source: Union[Source, None]
    has_hid: bool

    @classmethod
    def of(kls, monitor: monitor.Monitor):
        status = monitor.get_status()
        return kls(
            source=status.source and status.source.__dict__,
            has_hid=status.has_hid
        )


class Monitor(BaseModel):
    name: str
    uuid: uuid.UUID
    status: MonitorStatus
    neighbours: dict[monitor.Adjacency, 'Monitor']
