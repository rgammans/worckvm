import uuid
from typing import List
from fastapi import FastAPI
from starlette.convertors import Convertor, register_url_convertor
from . import api
from .monitor import Monitor
from .config import loads
from . import serialisers as ser

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

@app.post('/monitor/{uuid}/grabhid')
def grab_hid(uuid: str):
    m:Monitor = api.get_monitor_by_uuid(uuid)
    if m and m.get_status().has_hid:
        return api.grab_hid(m)
    return "device has no hid"


@app.post('/monitor/{uuid}/select/{source_id}')
def select_monitor(uuid: str,source_id: str):
    m:Monitor = api.get_monitor_by_uuid(uuid)
    if m:
        return api.select(m, source_id)


@app.get('/monitor/{uuid}/status')
def get_status(uuid: str):
    m:Monitor = api.get_monitor_by_uuid(uuid)
    if m:
        return api.get_status(m)


@app.get('/monitor/{uuid}/available',response_model=List[ser.Source])
def get_available_sources(uuid: str):
    m:Monitor = api.get_monitor_by_uuid(uuid)
    if m:
        return api.available_sources(m)

app.get('/monitors/')(api.list_monitor)
