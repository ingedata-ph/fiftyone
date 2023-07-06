from pathlib import Path
from argparse import ArgumentParser

import fiftyone as fo
from utils.coco_xxii_dataset import coco_xxii_to_fiftyone


if __name__ == "__main__":

    parser = ArgumentParser(
        "Script to load a COCO XXII JSON dataset to fiftyone"
    )
    parser.add_argument(
        "--images",
        "-i",
        type=Path,
        help="Path to the root directory containing the dataset's images",
        required=True
    )
    parser.add_argument(
        "--coco_json",
        "-a",
        type=Path,
        help="Path to COCO XXII JSON file containing the dataset's annotations",
        required=True
    )
    parser.add_argument(
        "--name",
        "-n",
        type=str,
        help="Name of the dataset in fiftyone. If not specified, the script will use the COCO XXII JSON file name",
        default=""
    )

    args = parser.parse_args()

    # if no dataset name is specified in the args, we use the COCO XXII JSON's filename
    if not args.name:
        args.name = args.coco_json.stem

    # get available dataset names in fiftyone
    available_datasets = fo.list_datasets()

    # if the dataset's name does not exist in FiftyOne we load the dataset
    if args.name not in available_datasets:
        print(f"Loading the dataset {args.name} into FiftyOne...")
        dataset = coco_xxii_to_fiftyone(args.name, args.coco_json, args.images)
        dataset.persistent = True
        print(f"Successfully loaded the dataset {args.name} into FiftyOne")
    # if the dataset's name exists in FiftyOne we print an error message
    else:
        print(f"ERROR: The dataset's name that you provided ({args.name}) already exists in FiftyOne. Here's the "
              f"list of the datasets that exist in your FiftyOne database:\n {available_datasets}")

