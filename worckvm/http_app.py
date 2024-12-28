import uuid
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.convertors import Convertor, register_url_convertor
from worchestic.signals import Source
from . import api
from .monitor import Monitor, WorcKVMError
import uvicorn

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


def set_options(parser):
    parser.add_argument("--host", type=str, default="0.0.0.0", help="The host to bind to.")
    parser.add_argument("--port", type=int, default=8000, help="The port to bind to.")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload.")
    parser.add_argument("--workers", type=int, default=1, help="Number of worker processes.")
    parser.add_argument("--log-level", type=str, default="info", help="Log level.")
    parser.add_argument("--ssl-keyfile", type=str, help="SSL key file.")
    parser.add_argument("--ssl-certfile", type=str, help="SSL certificate file.")
    parser.add_argument("--ssl-version", type=str, help="SSL version.")
    parser.add_argument("--ssl-cert-reqs", type=str, help="SSL certificate requests.")
    parser.add_argument("--ssl-ca-certs", type=str, help="SSL CA certificates.")
    parser.add_argument("--ssl-ciphers", type=str, help="SSL ciphers.")
    parser.add_argument("--proxy-headers", action="store_true", help="Use proxy headers.")
    parser.add_argument("--root-path", type=str, help="Root path.")
    parser.add_argument("--limit-concurrency", type=int, help="Limit concurrency.")
    parser.add_argument("--timeout-keep-alive", type=int, help="Timeout keep alive.")
    parser.add_argument("--graceful-timeout", type=int, help="Graceful timeout.")
    parser.add_argument("--limit-max-requests", type=int, help="Limit max requests.")
    parser.add_argument("--limit-max-requests-jitter", type=int, help="Limit max requests jitter.")
    parser.add_argument("--reload-dir", type=str, help="Reload dir.")
    parser.add_argument("--reload-delay", type=float, help="Reload delay.")
    parser.add_argument("--ws-ping-interval", type=int, help="WS ping interval.")
    parser.add_argument("--ws-ping-timeout", type=int, help="WS ping timeout.")
    parser.add_argument("--loop", type=str, help="Loop.", default="auto")
    parser.add_argument("--http", type=str, help="HTTP.", default="auto")
    
    


def run(**kwargs):
    uvicorn.run(app, **kwargs)