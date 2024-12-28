import uuid
from typing import Union, Dict
from . import monitor
from pydantic import BaseModel, SerializeAsAny

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
    # We can't expand monitor's here as it's a dually linked
    # list which would expand to infinite depth.
    neighbours: Dict[monitor.Adjacency, uuid.UUID]

    def __init__(self, *args, **kwargs):
        # If the first argument is a monitor, construct from that.
        if len(args) > 0 and isinstance(m := args[0], monitor.Monitor):
            return super().__init__(
                name=m.name,
                uuid=m.uuid,
                status=MonitorStatus.of(m),
                neighbours={k: v.uuid for k, v in m.neighbours.items()},
            )
        return super().__init__(*args, **kwargs)
