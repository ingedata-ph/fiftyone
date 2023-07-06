"""
FiftyOne Server /stages route
| Copyright 2017-2022, Voxel51, Inc.
| `voxel51.com <https://voxel51.com/>`_
|
"""
from starlette.endpoints import HTTPEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse

import fiftyone.core.dataset as fod
import fiftyone.types as fot
import fiftyone.core.session as fos
import os

from fiftyone.server.decorators import route
from .coco_xxii_dataset import hello_fiftyone


class LoadDataXxii(HTTPEndpoint):
    @route
    async def get(self, request: Request, data: dict):
        fiftyone = hello_fiftyone()
        response_message = { "hello": fiftyone }


        return JSONResponse(
            response_message,
            status_code=200,
        )
