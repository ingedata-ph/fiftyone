import fiftyone as fo
from argparse import ArgumentParser


if __name__ == "__main__":

    parser = ArgumentParser(
        "Script to launch fiftyone's web application on a specific port"
        " and fiftyone"
    )
    parser.add_argument(
        "--port",
        "-p",
        type=int,
        help="Port to use to launch fiftyone's web application",
        default=5151,
    )
    args = parser.parse_args()

    # run fiftyone's web app
    session = fo.launch_app(port=args.port)
    session.wait()

