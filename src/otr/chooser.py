from rich.console import Console  # noqa: F401
from rich.prompt import Prompt, IntPrompt
from pprint import pprint as pp
from typing import Any
from typing import Generic, Type, TypeVar

console = Console(highlight=False)
T = TypeVar("T")


def choose(items: list[tuple[T, T, T]], template: str, question: str) -> tuple[T, T, T]:
    """Select an item from a list.

    The list must be a list of tuples.
    The template is a string that will be used to format each the tuple in the list.
      eg, "[bold]{}[/bold] {}"
    """
    pad = len(str(len(items)))
    for i, item in enumerate(items):
        counter = i + 1
        # console.print(f"[green]{counter:>{pad}})[/green] [bold]{item[0]}[/bold] {item}")
        console.print(f"[green]{counter:>{pad}})[/green]", template.format(*item))
    choices = [str(i) for i in range(1, len(items) + 1)]
    index = IntPrompt.ask(question, choices=choices, show_choices=False)
    return items[index - 1]
