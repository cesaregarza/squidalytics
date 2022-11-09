import os
import time
from typing import Callable, ParamSpec, TypeVar

import cmd2
import pandas as pd
import visidata
from colorama import Fore, Style, just_fix_windows_console
from typing_extensions import Self

from squidalytics.cli.argparsers import (
    load_argparser,
    summary_argparser,
    to_clipboard_argparser,
    view_argparser,
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
        + "Please enter a command to get started or type "
        + Fore.YELLOW
        + BOLD
        + "help"
        + Style.RESET_ALL
        + " for a list of commands."
    )
    prompt = "[" + Fore.RED + BOLD + "UNLOADED" + Style.RESET_ALL + "]> "
    battle_schema = None

    def postloop(self) -> None:
        self.poutput("Thank you for using " + SQUID_TEXT + "!")

    @staticmethod
    def loaded_method(func: Callable[P, T]) -> Callable[P, T]:
        @cmd2.with_category("Battle Data")
        def wrapper(self: Self, *args: P.args, **kwargs: P.kwargs) -> T:
            if not self.battle_schema:
                self.print_error(
                    'No battle schema loaded. Use the "load" command to load'
                    + "a battle schema."
                )
                return
            return func(self, *args, **kwargs)

        # This allows passing the function's docstring to the auto-generated
        # help message even though we're wrapping it.
        wrapper.__doc__ = func.__doc__
        return wrapper

    def print_error(self, msg: str) -> None:
        self.poutput(BOLD + Fore.RED + "ERROR: " + Style.RESET_ALL + msg)

    def viz_dataframe(self, df: pd.DataFrame) -> None:
        self.poutput(
            "Opening data in VisiData in 3 seconds. Press "
            + Fore.YELLOW
            + BOLD
            + "Q"
            + Style.RESET_ALL
            + " to quit."
        )
        for i in range(3):
            self.poutput(
                " " + Fore.YELLOW + BOLD + str(3 - i) + Style.RESET_ALL,
                end="\r",
            )
            time.sleep(1)
        self.show_viz(df)

    def show_viz(self, df: pd.DataFrame) -> None:
        """A convenience method to run the VisiData visualization.

        Args:
            df (pd.DataFrame): The dataframe to visualize.
        """
        visidata.run(visidata.PandasSheet("pandas", source=df))

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
        self.prompt = (
            "[" + Fore.GREEN + BOLD + " LOADED " + Style.RESET_ALL + "]> "
        )

    @cmd2.with_argparser(to_clipboard_argparser)
    @loaded_method
    def do_to_clipboard(self, opts) -> None:
        """Copies the battle schema to the clipboard."""
        self.battle_schema.to_pandas(opts.all).to_clipboard(sep=opts.delimiter)
        self.poutput("Battle schema copied to clipboard.")

    @cmd2.with_argparser(view_argparser)
    @loaded_method
    def do_view(self, opts) -> None:
        """Converts the battle schema to a viewable dataframe."""
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
            df: pd.DataFrame = df.squidalytics.format_for_cli()
            self.viz_dataframe(df)
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
