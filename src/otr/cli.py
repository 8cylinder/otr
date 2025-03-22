import sys
import os
import click
import re
import datetime
import importlib.metadata
from typing import NamedTuple
from types import SimpleNamespace
from pathlib import Path
from pprint import pprint as pp  # noqa: F401
import mutagen
from rich import print  # noqa: F401
from .slugify import SlugifyString  # noqa: F401
from dataclasses import dataclass
import shlex


__version__ = importlib.metadata.version("otr")


class Regexes(NamedTuple):
    show: str
    episode: str
    date: str
    number: str


@dataclass
class FileParts:
    show_title: str
    episode_title: str
    broadcast_date: datetime.datetime
    episode_number: int
    file_type: str = "mp3"


def get_parts(file_path: Path, regs: dict[str, str], custom: str) -> SimpleNamespace:
    parts = {}
    filename = file_path.stem
    if custom:
        filename = re.sub(custom, "", filename)
        print(">>>", filename)
    for field, regex in regs.items():
        match = re.findall(regex, filename)[0]
        if field == "date":
            match = parse_date(match)
        parts[field] = match

    return SimpleNamespace(**parts)


def parse_date(date_str: str) -> datetime.datetime:
    date_regexes: list[tuple[str, str]] = [
        (r"(\d\d-\d\d-\d\d)", "%Y-%m-%d"),
        (r"(\d\d-\d\d)-xx", "%Y-%m"),
        (r"(\d\d)-xx-xx", "%Y"),
        ("(xx-xx-xx)", ""),
    ]
    broadcast_date = datetime.datetime.strptime("1000-01-01", "%Y-%m-%d")
    for date_regex in date_regexes:
        if date_str == "xx-xx-xx":
            return broadcast_date
        elif re.search(date_regex[0], date_str):
            datestr = re.findall(date_regex[0], date_str)[0]
            if len(datestr.split("-")[0]) == 2:
                datestr = "19" + datestr
            broadcast_date = datetime.datetime.strptime(datestr, date_regex[1])
            break
    return broadcast_date


def slug(string: str) -> str:
    string = string.replace(" ", "-").replace("_", "-").lower()
    string = re.sub(r"[-_]+", "-", string)
    return string


# fmt: off
CONTEXT_SETTINGS = {
    "help_option_names": ["-h", "--help"],
    "token_normalize_func": lambda x: x.lower(),
}
@click.command(context_settings=CONTEXT_SETTINGS)
@click.argument("files", nargs=-1, type=click.Path(exists=True, path_type=Path))

@click.option('--show', '-s', default=r'^(.*)[-_]\d\d-\d\d-\d\d')
@click.option('--episode', '-p', default=r'e\d\d[_-](.*)')
@click.option('--date', '-d', default=r'(\d\d-\d\d-\d\d)')
@click.option('--number', '-n', default=r'e(\d+)')

@click.option('--custom', '-c', help='Custom regex to delete')
@click.option('--edit/--view', '-e/-v', default=False,
    help="Make edits to the files.")
@click.version_option()
# fmt: on
def otr(
    files: list[Path],
    edit: bool,
    # ---------------------------
    show: str,
    episode: str,
    date: str,
    number: str,
    custom: str,
) -> None:
    """Rename and set ID3 tags for old time radio shows."""

    cmd = shlex.join(sys.argv[:])

    regexes = {
        "show": show,
        "episode": episode,
        "date": date,
        "number": number,
    }

    sep = "--"
    template = (
        "{show}{sep}{date:%Y-%m-%d}{sep}e{number:0{padding}}{sep}{episode}{file_type}"
    )
    padding = len(str(len(files)))
    print(padding)

    for otr_file in files:

        print(f"[blue]{otr_file}")

        # file_parts = parse(otr_file)
        file_parts = get_parts(otr_file, regexes, custom)
        # print(file_parts)

        name = template.format(
            show=slug(file_parts.show),
            date=file_parts.date,
            number=file_parts.number,
            episode=slug(file_parts.episode),
            file_type=otr_file.suffix,
            padding=padding,
            sep=sep,
        )
        print(f"[green]{name}")

        print()

    # print(__name__, cmd)
    cmd_log_file = Path("otr-cmd.log")
    with open(cmd_log_file, "w") as f:
        f.write(f"[{datetime.datetime.now()}] otr {cmd}\n")
        # for file in files:
        #     f.write(f"{file}\n")
        # f.write("\n")
