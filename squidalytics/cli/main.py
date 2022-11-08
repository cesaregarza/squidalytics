from typing import Callable, ParamSpec, TypeVar

import cmd2
from colorama import Fore, Style, just_fix_windows_console
from typing_extensions import Self

from squidalytics.cli.argparsers import load_argparser
from squidalytics.schemas import battleSchema

just_fix_windows_console()

BOLD = "\033[1m"
UNDERLINE = "\033[4m"

T = TypeVar("T")
P = ParamSpec("P")


class MainShell(cmd2.Cmd):
    intro = (
        "Welcome to "
        + Fore.GREEN
        + BOLD
        + "Squidalytics"
        + Style.RESET_ALL
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

    @staticmethod
    def loaded_method(func: Callable[P, T]) -> Callable[P, T]:
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

    @loaded_method
    def do_to_pandas(self, _):
        """Converts the battle schema to a pandas dataframe."""
        self.poutput(self.battle_schema.to_pandas())
