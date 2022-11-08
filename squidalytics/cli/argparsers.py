from cmd2 import Cmd2ArgumentParser

load_argparser = Cmd2ArgumentParser()
load_argparser.add_argument(
    "files", nargs="+", help="The files to load battle data from."
)
load_argparser.add_argument(
    "-r",
    "--recursive",
    action="store_true",
    help="Recursively search for files in the specified directories.",
)
load_argparser.add_argument(
    "-d",
    "--directory",
    action="store_true",
    help="Treat the specified files as directories.",
)
