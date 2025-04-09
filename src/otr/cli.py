import sys
import click
import re
import datetime
import importlib.metadata
from typing import NamedTuple
from pathlib import Path
from pprint import pprint as pp  # noqa: F401
import mutagen
from rich.console import Console  # noqa: F401

from .fuzzy import find_match
from .slugify import SlugifyString  # noqa: F401
import shlex

console = Console(highlight=False)
__version__ = importlib.metadata.version("otr")


class Regexes(NamedTuple):
    show: str
    episode: str
    date: str
    number: str


def get_show(pat: str, fname: Path) -> str:
    match = re.search(pat, str(fname.stem))
    # print(pat, fname, match)
    if match:
        return match.groups()[0]
    return ""


def get_date(pat: str, fname: Path) -> str:
    match = re.search(pat, str(fname.stem))
    if match:
        d = list(match.groups())
        # print(">>>", d)
        if len(d) == 2:
            d[0] = f"19{d[0]}"
        return "-".join(d)
    return ""


def get_number(pat: str, fname: Path, count: int) -> str:
    match = re.search(pat, str(fname.stem))
    if match:
        number = match.groups()[0]
        return f"e{number:>0{count}}"
    return ""


def get_episode(pat: str, fname: Path) -> str:
    match = re.search(pat, str(fname.stem))
    if match:
        return match.groups()[0]
    return ""


# fmt: off
CONTEXT_SETTINGS = {
    "help_option_names": ["-h", "--help"],
    "token_normalize_func": lambda x: x.lower(),
}
@click.group(context_settings=CONTEXT_SETTINGS)
# fmt: on
def otr() -> None:
    """Manage OTR (Old Time Radio) shows."""


# fmt: off
@otr.command()
@click.argument("files", nargs=-1, type=click.Path(exists=True, path_type=Path))
@click.option('--show-name', '-s',
              help="String to use to search instead of the first file's stem.")
@click.option('--episode-re', '-e', default=r'e\d\d[_-](.*)',
              help='Regex to extract the episode name.')
@click.option('--ratio', '-r', 'target_ratio', type=float, default=0.55)
# fmt: on
def fuzzy(
    files: list[Path], show_name: str, episode_re: str, target_ratio: float
) -> None:
    """Fuzzy match the file with the db."""
    title = files[0].stem
    if show_name:
        title = show_name
    find_match(title, target_ratio, files, episode_re)


# fmt: off
@otr.command()
@click.argument("files", nargs=-1, type=click.Path(exists=True, path_type=Path))

@click.option('--show-re', '-s', default=r'^(.*)[-_]\d\d-\d\d-\d\d',
              help='Regex to extract the show name.')
@click.option('--episode-re', '-e', default=r'e\d\d[_-](.*)',
              help='Regex to extract the episode name.')
@click.option('--date-re', '-d', default=None,
              help='Regex to extract the date.')
@click.option('--number-re', '-n', default=None,
              help='Regex to extract the episode number.')

# @click.option('--custom-re', '-c', help='Custom regex to delete')
@click.option('--edit/--view', default=False,
    help="Make edits to the files.")
@click.version_option()
# fmt: on
def regex(
    files: list[Path],
    edit: bool,
    # ---------------------------
    show_re: str,
    episode_re: str,
    date_re: str,
    number_re: str,
    # ---------------------------
    # custom_re: str,
) -> None:
    """Rename and set ID3 tags for old time radio shows."""
    padding = len(str(len(files)))

    for otr_file in files:

        parts: list[str] = []
        # if custom_re:
        #     new = re.sub(custom_re, "", otr_file.stem)

        if show_re and (formated_show := get_show(show_re, otr_file)):
            # print("show:", formated_show)
            parts.append(formated_show)

        if date_re and (formated_date := get_date(date_re, otr_file)):
            # print("date:", formated_date)
            parts.append(formated_date)

        if number_re and (formated_number := get_number(number_re, otr_file, padding)):
            # print("number:", formated_number)
            parts.append(formated_number)

        if episode_re and (formated_episode := get_episode(episode_re, otr_file)):
            # print("episode:", formated_episode)
            parts.append(formated_episode)

        # print(parts)
        tags = mutagen.File(otr_file)
        for tag in tags:
            print(tag, tags[tag])
        # pp(tags)

        print(parts)
        parts = [re.sub(r"[-_ ]+", "-", i).lower() for i in parts]
        new = "--".join(parts) + otr_file.suffix
        console.print(f"[blue]{otr_file}")
        console.print(f"{new}", style="green")

        print()

    cmd = shlex.join(sys.argv[:])
    cmd_log_file = Path("otr-cmd.log")
    with open(cmd_log_file, "a") as f:
        f.write(f"[{datetime.datetime.now()}]  {cmd}\n")
