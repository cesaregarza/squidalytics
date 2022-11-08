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

to_clipboard_argparser = Cmd2ArgumentParser()
to_clipboard_argparser.add_argument(
    "-a",
    "--all",
    action="store_true",
    help="Include detailed information about each battle.",
)
to_clipboard_argparser.add_argument(
    "-d",
    "--delimiter",
    default="\t",
    help="The delimiter to use when copying to the clipboard.",
)

to_pandas_argparser = Cmd2ArgumentParser()
to_pandas_argparser.add_argument(
    "-a",
    "--all",
    action="store_true",
    help="Include detailed information about each battle.",
)
to_pandas_argparser.add_argument(
    "-i",
    "--include",
    nargs="+",
    help=(
        "Weapons and weapon classes to exclusively include by which to filter "
        + "the data."
    ),
)
to_pandas_argparser.add_argument(
    "-x",
    "--exclude",
    nargs="+",
    help="Weapons and weapon classes by which to filter the data.",
)
to_pandas_argparser.add_argument(
    "-l",
    "--last",
    type=int,
    default=0,
    help="The number of battles to show.",
)
to_pandas_argparser.add_argument(
    "-o",
    "--output",
    default="stdout",
    help=(
        'The output method to use. If "stdout", the data will be printed to '
        + 'the console. If "clipboard", the data will be copied to the '
        + "clipboard. Otherwise, the argument will be treated as a file path."
    ),
)
to_pandas_argparser.add_argument(
    "-d",
    "--delimiter",
    default="\t",
    help=(
        "The delimiter to use when copying to the clipboard or writing to a "
        + "file."
    ),
)
to_pandas_argparser.add_argument(
    "-f",
    "--force",
    action="store_true",
    help="Force overwrite of the output file if it already exists.",
)
