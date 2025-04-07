import json
import re
from pathlib import Path
from pprint import pprint as pp
import jaro  # type: ignore
from rich.prompt import Prompt
from rich.console import Console  # noqa: F401
from typing import Any
import math
from .chooser import choose


console = Console(highlight=False)

ID_DB = Path("/home/sm/projects/otr/data/data.json")
SHOWS_DB = Path("/home/sm/projects/otr/data/json-data")


def find_match(title: str, target_ratio: float, files: list[Path]) -> None:

    show_id = get_show_title_id(title, target_ratio)

    # read the json file in `shows_db` using the show_id to match the json file
    show_json_file = SHOWS_DB / f"{show_id}.json"
    console.print(f"[green]Found JSON file:[/green] {show_json_file}", style="bold")
    show_data = json.load(open(show_json_file))

    show_title = show_data["titles"][0]
    if len(show_data["titles"]) > 1:
        print()
        titles: list[tuple[str]] = [(i["title"],) for i in show_data["titles"]]
        template = "[bold]{}[/bold]"
        title = choose(titles, template, "[green]Multiple titles found, choose one")[0]

    console.print(f"title: [bold]{title}[/bold]")

    episodes_data = show_data["episodes"]
    for episode in files:
        episode_regex = "ex_(.*$)"
        episode_data = find_episode_match(episode.stem, episode_regex, episodes_data)


def find_episode_match(
    file_episode: str, episode_regex: str, episodes: list[dict[str, Any]]
) -> dict[str, Any]:
    titles = [{"id": i["epnum"], "title": i["titles"]} for i in episodes if i["titles"]]
    matches = []
    for episode in titles:
        for title in episode["title"]:
            match = re.search(episode_regex, file_episode)
            match_to = ""
            if match:
                match_to = match.groups()[0]
            matched_ratio = jaro.jaro_winkler_metric(title["title"], match_to)
            # matches.append((title["title"], matched_ratio, episode["id"]))
            matches.append([matched_ratio, {"episode": episode}])
    matches.sort(key=lambda x: x[0], reverse=True)  # sort by confidence
    pp(matches)
    match = matches[0]
    # pp(matches)
    console.print(f"[b]{matches[0][0]}[/b] - {file_episode}")
    return match["episode"]


def get_show_title_id(title: str, target_ratio: float) -> int:
    """Get the show title id from the ids_file based on the title and target_ratio."""
    ids_file = json.load(open(ID_DB))

    # matches = []
    # results_count = math.inf
    # try searching until there are less than 20 results.
    # while results_count > 20:
    #     matches = search_ids_file(ids_file, target_ratio, title)
    #     if len(matches) <= 20:
    #         break
    #     results_count = len(matches)
    #     target_ratio = target_ratio + 0.01
    #     console.print(
    #         f"[blue]Found {results_count} matches, trying ratio {target_ratio:.2f}..."
    #     )

    matches = search_ids_file(ids_file, target_ratio, title)
    matches.sort(key=lambda x: x[1], reverse=True)  # sort by confidence
    matches = matches[:20]
    # convert the confidence value to a percent
    matches_p = [(f"{j*100:.0f}%", i, k) for i, j, k in matches]
    column_template = "[blue]{}[/blue]  [bold]{}[/bold]"
    show = choose(
        matches_p, column_template, "[green]Multiple titles found, choose one"
    )
    show_id = int(show[2])
    return show_id


def choose_title_from_many(matches: list[str]) -> str:
    for i, match in enumerate(matches):
        counter = i + 1
        console.print(f"[green]{counter:>2})[/green] [bold]{match}")
    chosen = Prompt.ask("[green]Multiple titles found, choose one")
    try:
        return matches[int(chosen) - 1]
    except IndexError:
        console.print("[red]Invalid selection, please try again.")
        return choose_title_from_many(matches)
    except ValueError:
        console.print("[red]Invalid selection, please try again.")
        return choose_title_from_many(matches)


def print_titles(matches: list[tuple[str, float, int]]) -> int:
    """print the list of matches for the user to choose from."""
    matches.sort(key=lambda x: x[1], reverse=True)
    for i, match in enumerate(matches):
        confidence = int(match[1] * 100)
        counter = i + 1
        console.print(
            f"[green]{counter:>2})[/green] [blue]{confidence}%[/blue]  [bold]{match[0]}"
        )
    show_id = choose_title(matches)
    return show_id


def choose_title(matches: list[tuple[str, float, int]]) -> int:
    chosen = Prompt.ask("[green]Choose a title")
    try:
        index = int(chosen) - 1
        show_id = matches[int(index)][2]
    except IndexError:
        console.print("[red]Invalid selection, please try again.")
        return choose_title(matches)
    except ValueError:
        console.print("[red]Invalid selection, please try again.")
        return choose_title(matches)
    return show_id


def search_ids_file(
    ids_file: dict[str, Any], target_ratio: float, title: str
) -> list[tuple[str, float, int]]:
    """Search the ids_file for matches against the title using Jaro-Winkler metric"""
    matches: list[tuple[str, float, int]] = []
    for show in ids_file:
        ptitle = show["ptitle"]
        matched_ratio = jaro.jaro_winkler_metric(ptitle, title)
        if matched_ratio > target_ratio:  # 6
            matches.append((ptitle, matched_ratio, int(show["idp"])))
    return matches
