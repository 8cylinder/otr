import json
from pathlib import Path
from pprint import pprint as pp

import jaro
from rich.prompt import Prompt

from src.otr.cli import console


def find_matches(files: list[Path], target_ratio: float) -> None:
    id_db = Path("/home/sm/projects/otr/data/data.json")
    shows_db = Path("/home/sm/projects/otr/data/json-data")
    ids = json.load(open(id_db))
    title = files[0].stem
    matches: list[tuple[str, float, int]] = []
    for show in ids:
        ptitle = show["ptitle"]
        matched_ratio = jaro.jaro_winkler_metric(ptitle, title)
        if matched_ratio > target_ratio:  # 6
            matches.append((ptitle, matched_ratio, int(show["idp"])))
            # print('Matched:', ptitle, title, f'ratio: {matched_ratio:.2f}', f'id: {show["idp"]}')
    matches.sort(key=lambda x: x[1], reverse=True)
    for i, match in enumerate(matches):
        console.print(f"[green]{i:>2})[/green] [bold]{match[0]}")
    index = Prompt.ask("Chose a title")
    show_id = matches[int(index)][2]
    # read the json file in `shows_db` using the show_id to match the json file
    show_json_file = shows_db / f"{show_id}.json"
    console.print(f"[green]Found JSON file:[/green] {show_json_file}", style="bold")
    show_data = json.load(open(show_json_file))
    pp(show_data["titles"])
