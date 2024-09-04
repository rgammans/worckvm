import uuid
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.convertors import Convertor, register_url_convertor
from worchestic.signals import Source
import api , config
from monitor import Monitor, WorcKVMError


class UuidToObject:
    regex = "[0-9A-Fa-f]{32}"

    @classmethod
    def convert(kls, value: str):
        obj_uuid = uuid.UUID(value)
        try:

            return kls.my_type.get(obj_uuid)
        except KeyError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error":
                        f"{value} is not known as a {kls.my_type.__name__}"}
            )

    def to_string(value) -> str:
        return value.uuid.hex


class MonitorConverter(UuidToObject, Convertor):
    my_type = Monitor
register_url_convertor("Monitor", MonitorConverter)  # noqa: E305


class SourceConverter(UuidToObject, Convertor):
    my_type = Source
register_url_convertor("Source", SourceConverter)  # noqa: E305


app = FastAPI()

# added to allow expo web to work on local machine
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)


@app.exception_handler(WorcKVMError)
async def worc_errors(req: Request, error: WorcKVMError):
    return JSONResponse(
        status_code=400,
        content={"detail": {"error": f"{type(error).__name__} : {error}"}}
    )


app.post('/monitor/{monitor:Monitor}/grabhid')(api.grab_hid)
app.post('/monitor/{monitor:Monitor}/select/{source:Source}')(api.select)
app.get('/monitor/{monitor:Monitor}/status')(api.get_status)
app.get('/monitor/{monitor:Monitor}/available')(api.available_sources)
app.get('/monitors/')(api.list_monitor)

system = config.loads(open("../examples/dual_complex_kvm.yaml").read())