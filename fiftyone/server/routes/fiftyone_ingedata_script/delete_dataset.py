from argparse import ArgumentParser

import fiftyone as fo


if __name__ == "__main__":

    parser = ArgumentParser(
        "Script to delete a dataset from FiftyOne"
    )
    parser.add_argument(
        "--name",
        "-n",
        type=str,
        help="Name of the dataset you want to delete from fiftyone",
    )

    args = parser.parse_args()
    # get available dataset names in fiftyone
    available_datasets = fo.list_datasets()
    # if the dataset's exists in fiftyone, delete it, else print an error message.
    if args.name in available_datasets:
        fo.load_dataset(args.name).delete()
        print(f"Successfully deleted the dataset {args.name} from FiftyOne")
    else:
        print(f"ERROR: The dataset's name that you provided ({args.name}) could not be found in FiftyOne. Here's the "
              f"list of the datasets that exist in your FiftyOne database:{available_datasets}")

