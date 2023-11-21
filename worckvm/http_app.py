import uuid
from fastapi import FastAPI
from starlette.convertors import Convertor, register_url_convertor
from . import api
from .monitor import Monitor
from .config import loads

app = FastAPI()
system = loads(open("examples/simple_kvm_combined.yaml").read())


class UuidToObject:
    regex = "[0-9A-Fa-f]{32}"

    @classmethod
    def convert(kls, value: str):
        obj_uuid = uuid.UUID(value)
        return kls.my_type.get(obj_uuid)

    def to_string(value) -> str:
        return value.uuid.hex


class MonitorConverter(UuidToObject, Convertor):
    my_type = Monitor
register_url_convertor("Monitor", MonitorConverter)  # noqa: E305


#class SourceConverter(UuidToObject, Convertor):
#    my_type = Source
#register_url_convertor("Source", SourceConverter)  # noqa: E305

app.post('/monitor/{monitor:Monitor}/grabhid')(api.grab_hid)
app.post('/monitor/{monitor:Monitor}/select')(api.select)
app.get('/monitor/{monitor:Monitor}/status')(api.get_status)
app.get('/monitor/{monitor:Monitor}/available')(api.available_sources)
app.get('/monitors/')(api.list_monitor)
