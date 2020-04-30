"""
FiftyOne serve query definitions.

| Copyright 2017-2020, Voxel51, Inc.
| `voxel51.com <https://voxel51.com/>`_
|
"""
import fiftyone.core.query as foq


class Query(foq.DatasetQuery):
    """Server side class definition of a DatasetQuery"""

    def __init__(self, pipeline):
        """Initialize a query"""
        super(Query, self).__init__()
        self._pipeline = pipeline
