import os
from typing import Callable, ParamSpec, TypeVar

import cmd2
import pandas as pd
import tabulate
from colorama import Fore, Style, just_fix_windows_console
from typing_extensions import Self

from squidalytics.cli.argparsers import (
    load_argparser,
    summary_argparser,
    to_clipboard_argparser,
    to_pandas_argparser,
)
from squidalytics.schemas import battleSchema

just_fix_windows_console()

BOLD = "\033[1m"
UNDERLINE = "\033[4m"
SQUID_TEXT = Fore.GREEN + BOLD + "Squidalytics" + Style.RESET_ALL

T = TypeVar("T")
P = ParamSpec("P")


class MainShell(cmd2.Cmd):
    """The main shell for the squidalytics CLI."""

    intro = (
        "Welcome to "
        + SQUID_TEXT
        + ", a tool for analyzing "
        + Fore.BLUE
        + BOLD
        + "Splatoon 3"
        + Style.RESET_ALL
        + " battle data!\n"
        + "Please enter a command to get"
        + " started or type "
        + Fore.YELLOW
        + BOLD
        + "help"
        + Style.RESET_ALL
        + " for a list "
        + "of commands."
    )
    prompt = ">"
    battle_schema = None

    def postloop(self) -> None:
        self.poutput("Thank you for using " + SQUID_TEXT + "!")

    @staticmethod
    def loaded_method(func: Callable[P, T]) -> Callable[P, T]:
        @cmd2.with_category("Battle Data")
        def wrapper(self: Self, *args: P.args, **kwargs: P.kwargs) -> T:
            if not self.battle_schema:
                self.print_error("No battle schema loaded.")
                return
            return func(self, *args, **kwargs)

        # This allows passing the function's docstring to the auto-generated
        # help message even though we're wrapping it.
        wrapper.__doc__ = func.__doc__
        return wrapper

    def print_error(self, msg: str) -> None:
        self.poutput(BOLD + Fore.RED + "ERROR: " + Style.RESET_ALL + msg)

    def print_dataframe(self, df, **kwargs) -> None:
        width = os.get_terminal_size().columns
        pd.set_option("display.width", width)
        pd.set_option("display.max_colwidth", 20)
        table = tabulate.tabulate(
            df,
            df.columns,
            showindex=False,
            tablefmt="pretty",
        )
        self.poutput(table)

    @staticmethod
    def format_dataframe_for_terminal(df: pd.DataFrame) -> pd.DataFrame:
        """Formats a dataframe for printing in the terminal."""
        df = df.copy()
        # Format datetimes for printing.
        dt_cols = df.select_dtypes(include="datetime64[ns, UTC]").columns
        df.loc[:, dt_cols] = df.loc[:, dt_cols].applymap(
            lambda dt: dt.strftime("%Y-%m-%d %H:%M:%S")
        )
        # Format timedeltas for printing.
        td_cols = df.select_dtypes(include="timedelta64[ns]").columns

        def format_timedelta(td: pd.Timedelta) -> str:
            minutes, seconds = divmod(td.seconds, 60)
            return f"{minutes}m:{seconds:02}s"

        df.loc[:, td_cols] = df.loc[:, td_cols].applymap(format_timedelta)

        # Truncate long strings.
        str_cols = df.select_dtypes(include="string").columns
        df.loc[:, str_cols] = df.loc[:, str_cols].applymap(
            lambda s: s[:20] + "..." if len(s) > 20 else s
        )
        # apply max precision to floats
        float_cols = df.select_dtypes(include="float").columns
        df.loc[:, float_cols] = df.loc[:, float_cols].round(2)
        return df

    @cmd2.with_category("Battle Data")
    @cmd2.with_argparser(load_argparser)
    def do_load(self, opts) -> None:
        """Loads a battle schema from a file."""
        files = opts.files
        if len(files) == 0:
            self.poutput("Please specify a file to load.")
            return
        if opts.directory:
            schemas = []
            for file in files:
                schemas.append(
                    battleSchema.load_all_from_dir(file, opts.recursive)
                )
            self.battle_schema = battleSchema.concatenate(*schemas)
        else:
            self.battle_schema = battleSchema.load(files)
        self.poutput(
            "Loaded "
            + Fore.YELLOW
            + BOLD
            + str(len(self.battle_schema))
            + Style.RESET_ALL
            + f" battle{'s' if len(self.battle_schema) > 1 else ''} from "
            + Fore.YELLOW
            + BOLD
            + str(len(files))
            + Style.RESET_ALL
            + f" file{'s' if len(files) > 1 else ''}."
        )

    @cmd2.with_argparser(to_clipboard_argparser)
    @loaded_method
    def do_to_clipboard(self, opts) -> None:
        """Copies the battle schema to the clipboard."""
        self.battle_schema.to_pandas(opts.all).to_clipboard(sep=opts.delimiter)
        self.poutput("Battle schema copied to clipboard.")

    @cmd2.with_argparser(to_pandas_argparser)
    @loaded_method
    def do_to_pandas(self, opts) -> None:
        """Converts the battle schema to a pandas dataframe."""
        df = self.battle_schema.to_pandas(opts.all)
        if (opts.include is not None) and (len(opts.include) > 0):
            df, _, _ = battleSchema.filter_weapons(df, opts.include)
        if (opts.exclude is not None) and (len(opts.exclude) > 0):
            df, _, _ = battleSchema.filter_weapons(
                df, opts.exclude, include=False
            )

        if opts.last < 0:
            self.print_error("Last must be non-negative.")
            return
        if opts.last > 0:
            df = df.tail(opts.last)

        if opts.output == "stdout":
            df = self.format_dataframe_for_terminal(df)
            self.print_dataframe(df)
            return
        elif opts.output == "clipboard":
            df.to_clipboard(sep=opts.delimiter)
            self.poutput("Battle schema copied to clipboard.")
            return

        # Check if output is a filepath or directory path
        if os.path.isdir(opts.output):
            if opts.output[-1] != os.path.sep:
                opts.output += os.path.sep
            opts.output += "battle_schema.csv"
        elif os.path.isfile(opts.output) and not opts.force:
            self.print_error(
                "File already exists, please either specify a different path, "
                + "delete the existing file and try again, use another output "
                + "method, or use the --force flag to overwrite the existing "
                + "file."
            )
            return
        elif os.path.isfile(opts.output) and opts.force:
            os.remove(opts.output)

        df.to_csv(opts.output, sep=opts.delimiter)
        self.poutput("Battle schema saved to " + opts.output + ".")
