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


class LoadData(HTTPEndpoint):
    @route
    async def post(self, request: Request, data: dict):
        organization_name = data.get("organization_name", None)
        batch_name = data.get("batch_name", None)
        project_name = data.get("project_name", None)

        mounted_dir = "/fiftyone-google-storage/"

        fiftyone_dataset_dir = os.path.join(mounted_dir, organization_name, project_name, batch_name)
        # IMAGES_DIR = os.path.dirname(fiftyone_dataset_dir + "/images/")
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
            dataset_list = fod.list_datasets()

            dataset_params = {
                "dataset_type": fot.COCODetectionDataset(),
                "data_path": IMAGE_URLS_FILE,
                "labels_path": ANNOTATION_FILE,
                "label_types": ["segmentations"],
                "include_id": True,
            }

            if dataset_name in dataset_list:
                old_dataset = fod.load_dataset(dataset_name)
                old_dataset.clear()

                old_dataset.add_dir(**dataset_params)
                response_message = {
                    "success": "Dataset is successfully reloaded!"
                }
            else:
                dataset_params["name"] = dataset_name

                new_dataset = fod.Dataset.from_dir(**dataset_params)
                new_dataset.persistent = True

                response_message = {
                    "success": "Dataset is successfully created!"
                }

            status_code = 200

        return JSONResponse(
            response_message,
            status_code=status_code,
        )
