import sys
import os
import click
import re
import datetime
import importlib.metadata
from typing import NamedTuple
from pathlib import Path
from pprint import pprint as pp  # noqa: F401
import mutagen
from rich import print  # noqa: F401
from .slugify import SlugifyString  # noqa: F401


__version__ = importlib.metadata.version("otr")


class FileParts(NamedTuple):
    show_title: str
    episode_title: str
    broadcast_date: datetime.datetime
    episode_number: int
    file_type: str = "mp3"


def parse(file_path: Path) -> FileParts:
    """Parse a filename and extract metadata."""

    # fname = re.sub(r"[_]", " ", file_path.stem)
    fname = file_path.stem.replace("_", " ")

    date_re = None
    date_regexes: list[tuple[str, str]] = [
        (r"(\d\d-\d\d-\d\d)", "%Y-%m-%d"),
        (r"(\d\d-\d\d)-xx", "%Y-%m"),
        (r"(\d\d)-xx-xx", "%Y"),
    ]
    broadcast_date = datetime.datetime.strptime("1000-01-01", "%Y-%m-%d")
    for date_regex in date_regexes:
        if re.search(date_regex[0], fname):
            datestr = re.findall(date_regex[0], fname)[0]
            if len(datestr.split("-")[0]) == 2:
                datestr = "19" + datestr
            print(datestr)
            broadcast_date = datetime.datetime.strptime(datestr, date_regex[1])
            date_re = date_regex[0]
            break

    print("A", broadcast_date)

    # episode_re = r"e\d+"
    episode_regexes: list[str] = [
        r"[eE](\d+)",
        r"[eE][pP](\d+)",
    ]
    episode_number = 0
    episode_re = ""
    for episode_regex in episode_regexes:
        if re.search(episode_regex, fname):
            episode_number = int(re.findall(episode_regex, fname)[0])
            episode_re = episode_regex
            break

    print("episode_number", episode_number)
    # exit()
    # episode_number = re.findall(episode_re, fname)[0]

    split_re = f"{date_re}|{episode_re}"
    parts = re.split(split_re, fname)
    parts = [i.strip() for i in parts if i]

    series_name = parts[0]

    episode_title = parts[-1]

    file_parts = FileParts(
        show_title=series_name,
        episode_title=episode_title,
        broadcast_date=broadcast_date,
        episode_number=int(episode_number),
        file_type=file_path.suffix[1:],
    )
    return file_parts


# fmt: off
CONTEXT_SETTINGS = {
    "help_option_names": ["-h", "--help"],
    "token_normalize_func": lambda x: x.lower(),
}
@click.argument("files", nargs=-1, type=click.Path(exists=True, path_type=Path))
@click.option('--edit/--view', '-e/-v', default=False,
    help="Make edits to the files.")
@click.command(context_settings=CONTEXT_SETTINGS)
@click.version_option()
# fmt: on
def otr(files: list[Path], edit: bool) -> None:
    """Rename and set ID3 tags for old time radio shows."""

    sep = "---"
    template = "{show_title}{sep}{broadcast_date:%Y-%m-%d}{sep}e{episode_number:0{padding}}{sep}{episode_title}.{file_type}"
    padding = len(str(len(files)))
    print(padding)

    for otr_file in files:
        # click.secho(otr_file, fg="green", underline=False)
        print(f'[blue]{otr_file}')

        file_parts = parse(otr_file)
        print(file_parts)
        name = template.format(
            # **file_parts._asdict(),
            show_title=file_parts.show_title.replace(" ", "-"),
            broadcast_date=file_parts.broadcast_date,
            episode_number=file_parts.episode_number,
            episode_title=file_parts.episode_title.replace(" ", "-"),
            file_type=file_parts.file_type,
            padding=padding,
            sep=sep,
        )
        # print(name)
        # slugger = SlugifyString()
        # slugger.keep_dashes = True
        # slugger.strict = True
        # name = slugger.convert(name)
        # name = re.sub(r"-{3,}", "--", name)

        print(f"[green]{name}")
        # exit()

        # info = mutagen.File(otr_file)
        # pp(info)
        # pp(info["TIT2"])
        print()

    # for file in files:

    # get show name
    # get episode name
    # get date
    # get episode number
