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

view_argparser = Cmd2ArgumentParser()
view_argparser.add_argument(
    "-a",
    "--all",
    action="store_true",
    help="Include detailed information about each battle.",
)
view_argparser.add_argument(
    "-i",
    "--include",
    nargs="+",
    help=(
        "Weapons and weapon classes to exclusively include by which to filter "
        + "the data."
    ),
)
view_argparser.add_argument(
    "-x",
    "--exclude",
    nargs="+",
    help="Weapons and weapon classes by which to filter the data.",
)
view_argparser.add_argument(
    "-l",
    "--last",
    type=int,
    default=0,
    help="The number of battles to show.",
)
view_argparser.add_argument(
    "-o",
    "--output",
    default="stdout",
    help=(
        'The output method to use. If "stdout", the data will be printed to '
        + 'the console. If "clipboard", the data will be copied to the '
        + "clipboard. Otherwise, the argument will be treated as a file path."
    ),
)
view_argparser.add_argument(
    "-d",
    "--delimiter",
    default="\t",
    help=(
        "The delimiter to use when copying to the clipboard or writing to a "
        + "file."
    ),
)
view_argparser.add_argument(
    "-f",
    "--force",
    action="store_true",
    help="Force overwrite of the output file if it already exists.",
)

summary_argparser = Cmd2ArgumentParser()
summary_argparser.add_argument(
    "-a",
    "--all",
    action="store_true",
    help="Include detailed information about each battle.",
)
summary_argparser.add_argument(
    "-i",
    "--include",
    nargs="+",
    help=(
        "Weapons and weapon classes to exclusively include by which to filter "
        + "the data."
    ),
)
summary_argparser.add_argument(
    "-x",
    "--exclude",
    nargs="+",
    help="Weapons and weapon classes by which to filter the data.",
)
summary_argparser.add_argument(
    "-l",
    "--last",
    type=int,
    default=0,
    help="The number of battles to show.",
)
summary_argparser.add_argument(
    "-o",
    "--output",
    default="stdout",
    help=(
        'The output method to use. If "stdout", the data will be printed to '
        + 'the console. If "clipboard", the data will be copied to the '
        + "clipboard. Otherwise, the argument will be treated as a file path."
    ),
)
summary_argparser.add_argument(
    "-d",
    "--delimiter",
    default="\t",
    help=(
        "The delimiter to use when copying to the clipboard or writing to a "
        + "file."
    ),
)
summary_argparser.add_argument(
    "-f",
    "--force",
    action="store_true",
    help="Force overwrite of the output file if it already exists.",
)
summary_argparser.add_argument(
    "-s",
    "--stage",
    nargs="+",
    help="The stages to include in the summary. Currently not implemented.",
)
summary_argparser.add_argument(
    "-m",
    "--mode",
    nargs="+",
    help="The modes to include in the summary. Currently not implemented.",
)
