"""
FiftyOne Server /stages route
| Copyright 2017-2022, Voxel51, Inc.
| `voxel51.com <https://voxel51.com/>`_
|
"""
from starlette.endpoints import HTTPEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse

from threading import Thread
import os

from fiftyone.server.decorators import route
from .load_coco_data import load_coco_data


class LoadData(HTTPEndpoint):
    @route
    async def post(self, request: Request, data: dict):
        organization_name = data.get("organization_name", None)
        batch_name = data.get("batch_name", None)
        project_name = data.get("project_name", None)

        mounted_dir = "/fiftyone-google-storage/"

        fiftyone_dataset_dir = os.path.join(mounted_dir, organization_name, project_name, batch_name)
        IMAGE_URLS_FILE = fiftyone_dataset_dir + "/image_urls.json"
        ANNOTATION_FILE = fiftyone_dataset_dir + "/coco.json"
        dataset_name = "_".join([organization_name, project_name, batch_name])

        if not os.path.exists(fiftyone_dataset_dir):
            response_message = {
                "error": "Dataset path is not correct. Please gives the correct one!"
            }
            status_code = 422
        elif not os.path.exists(ANNOTATION_FILE):
            response_message = {
                "error": "Json annotation file is requiered."
            }
            status_code = 422
        else:
            background_thread = Thread(target=load_coco_data, args=(organization_name, IMAGE_URLS_FILE, ANNOTATION_FILE, dataset_name))
            background_thread.start()

            response_message = {
                "success": "Dataset creation is in progress"
            }

            status_code = 200

        return JSONResponse(
            response_message,
            status_code=status_code,
        )
