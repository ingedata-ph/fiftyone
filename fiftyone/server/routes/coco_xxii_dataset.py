import json
from pathlib import Path

import fiftyone as fo
from tqdm import tqdm

def hello_fiftyone():
    return "fiftyone"

def bbox_coco_to_fiftyone(bbox: list[float], width: int, height: int) -> list[float]:
    """ This function converts a coco bbox to a fiftyone bbox
    Args:
        bbox (List[float]): a list containing bbox coordinates in coco format
        width (int): the image's width (px)
        height (int): the image's height (px)
    Returns:
            List[float]
            """
    return [bbox[0] / width, bbox[1] / height, bbox[2] / width, bbox[3] / height]


def coco_annotations_to_detections(coco_annots: list[dict], width: int, height: int, labelmap: dict) -> fo.Detections:
    """ converts a list of coco annotations dicts of a given image into a fo.Detections object
    Args:
        coco_annots (list[Dict]): a list of coco annotations dict
        width (int): the image's width (px)
        height (int): the image's height (px)
        labelmap (dict): a dict mapping between the class ids (keys) and the class names (values) of the dataset
    Returns :
        fo.Detections: coco_annots converted into a fo.Detections """

    # a list that will contain fo.Detection objects
    detections = []

    # convert each coco annotation into a fo.Detection object
    for obj in coco_annots:
        # convert annotation to fo.Detection
        fo_det = fo.Detection(label=labelmap[obj["category_id"]],
                              bounding_box=bbox_coco_to_fiftyone(obj["bbox"], width, height),
                              confidence=obj["confidence"] if "confidence" in obj else None
                              )
        # add available attributes to fo.Detection
        attributes = obj.get("attributes", None)
        if type(attributes) == dict:
            for key, value in attributes.items():
                fo_det[key] = value

        # add the created fo.Detection object to detections list
        detections.append(fo_det)

    return fo.Detections(detections=detections)


def coco_xxii_to_fiftyone(name: str, coco_json: Path, images_dir: Path) -> fo.Dataset:
    """ Creates a fiftyone.Dataset object from a COCO XXII JSON dataset and stores it in FiftyOne's DB
    Args:
        name (str): Name of the fo.Dataset that will be created
        coco_json (Path): Path to the COCO .json file
        images_dir (Path): Path to the directory containing the dataset's images
    Returns:
       fo.Dataset """

    # load COCO json into a python dict
    with open(coco_json) as jfile:
        coco_dict = json.load(jfile)

    # get the labelmap of the dataset
    labelmap = {category["id"]: category["name"] for category in coco_dict["categories"]}

    # create a dict mapping between image ids and the list of their annotations
    all_annotations = {}
    for obj in tqdm(coco_dict["annotations"]):
        if obj["image_id"] in all_annotations:
            all_annotations[obj["image_id"]].append(obj)
        else:
            all_annotations[obj["image_id"]] = [obj]

    # create fiftyone.Sample for each image
    samples = []
    for img in coco_dict["images"]:
        sample = fo.Sample(filepath=images_dir / img["file_name"])
        # add annotations to the sample
        if img["id"] in all_annotations:
            sample["ground_truth"] = coco_annotations_to_detections(coco_annots=all_annotations[img["id"]],
                                                                    width=img["width"],
                                                                    height=img["height"],
                                                                    labelmap=labelmap
                                                                    )
        else:
            print(f"WARNING: this image has no annotations: {img['file_name']}")

        # add available tags to the sample
        tags = img.get("tags", None)
        if type(tags) == dict:
            for key, value in tags.items():
                sample[key] = value
        # add created sample to samples list
        samples.append(sample)

    # create fo.Dataset object containing the created samples
    dataset = fo.Dataset(name=name)
    dataset.add_samples(samples, dynamic=True)

    return dataset

