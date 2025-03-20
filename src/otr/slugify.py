#!/usr/bin/env bin-python.bash

import re
import click
from pathlib import Path
from pprint import pprint as pp
import string


class SlugifyString:
    spaces_only = False
    underscores_to_dashes = True
    custom = ""
    custom_sep = ","
    strict = False
    keep_dashes = False
    strict_chars = string.ascii_letters + string.digits + "._-"

    def convert(self, value: str) -> str:
        # remove custom characters
        if self.custom:
            value = self.replace_custom(value)
        # spaces only
        if not self.spaces_only:
            value = value.lower()
        # spaces -> dashes
        value = value.replace(" ", "-")
        # underscores -> dashes
        if self.underscores_to_dashes:
            value = value.replace("_", "-")
        # strict mode
        if self.strict:
            value = "".join(c for c in value if c in self.strict_chars)
        # remove duplicate dashes
        if not self.keep_dashes:
            value = re.sub("-+", "-", value)
        # remove duplicate spaces
        value = re.sub(" +", " ", value)

        return value

    def replace_custom(self, value: str) -> str:
        custom = self.custom.split(self.custom_sep)
        for c in custom:
            try:
                value = value.replace(c[0], c[1])
            except IndexError:
                value = value.replace(c[0], "")
        return value


class SlugifyFile(SlugifyString):
    for_real = False

    def process(self, filename: str) -> str:
        f = Path(filename)
        if not f.exists():
            raise FileNotFoundError('"{}" does not exist'.format(f.name))
        new_name = self.convert(f.name)
        if self.for_real:
            f.rename(new_name)
        return new_name


# def validate_custom(ctx, param, value):
#     pp(ctx.params)
#     return
#
#     sep = ctx.params["custom_sep"]
#     if not value:
#         return
#     for custom in value.split(sep):
#         if len(custom) == 0 or len(custom) > 2:
#             raise click.BadParameter("The characters are incorrect.")


# A custom type to only allow 1 character
class SingleChar(click.ParamType):
    name = "single_char"

    def convert(self, value, param, ctx) -> str:
        if len(value) != 1:
            self.fail("{} must be one character.".format(value))
        else:
            return value


SINGLE_CHAR = SingleChar()


# fmt: off
CONTEXT_SETTINGS = {
    'help_option_names': ['-h', '--help'],
    'token_normalize_func': lambda x: x.lower(),
}
@click.command(context_settings=CONTEXT_SETTINGS)
@click.argument('files', required=True, type=click.Path(exists=True), nargs=-1)
@click.option('-r', '--for-real', is_flag=True, default=False,
              help='Change the filename for real.')
@click.option('-s', '--spaces-only', is_flag=True,
              help='Remove spaces only.')
@click.option('-u', '--underscores-to-dashes', is_flag=True,
              help='Convert underscores to dashes.')
@click.option('--custom',
              help='A list of characters and their replacements.')
@click.option('--custom-sep', type=SINGLE_CHAR, default=',',
              help='The character used for separating the custom list.')
@click.option('-t', '--strict', is_flag=True,
              help='Remove non alpha-numeric characters.')
@click.option('-c', '--compact', is_flag=True,
              help='Horizontal output instead of vertical.')
@click.option('-d', '--dots', type=SINGLE_CHAR,
              help='Convert dots to character.')
# fmt: on
def main(
    files: str,
    for_real: bool,
    spaces_only: bool,
    underscores_to_dashes: bool,
    custom: str,
    custom_sep: str,
    compact: bool,
    strict: bool,
    dots: str,
) -> None:
    """Lowercase filenames and change spaces to dashes.

    Using the custom option:

    The --custom option is a list of one or two characters seperated
    by the --custom-sep character (default is a comma).  The first
    character will be replaced with the second character.  If it is a
    single character it will be deleted.

    \b
    custom examples:
      --custom='1X,2Y'  # "abcd1efg2.txt" becomes: "abcdXefgY.txt"
      --custom='1X-2Y' --custom-sep='-'  # does the same as above
      --custom='bB,),('  # "budget (nov 3).csv" becomes: "Budget nov 3.csv"
    """
    # validate_custom
    if custom:
        for c in custom.split(custom_sep):
            if len(c) == 0 or len(c) > 2:
                raise click.BadParameter("The --custom format is incorrect.")

    counter = 0
    for filename in files:
        counter += 1
        slug = SlugifyFile()
        slug.for_real = for_real
        slug.spaces_only = spaces_only
        slug.underscores_to_dashes = underscores_to_dashes
        slug.custom = custom
        slug.strict = strict
        slug.custom_sep = custom_sep

        try:
            new_name = slug.process(filename)
        except FileNotFoundError:
            click.echo('"{}" does not exist'.format(filename))
            continue

        old_color = "blue"
        new_color = "yellow" if filename == new_name else "green"

        if compact:
            click.echo(
                "{} --> {}".format(
                    click.style(filename, fg=old_color),
                    click.style(new_name, fg=new_color),
                )
            )
        else:
            click.echo("{:>2}. {}".format(counter, click.style(filename, fg=old_color)))
            click.echo("{:>2}  {}".format(" ", click.style(new_name, fg=new_color)))
            click.echo()


if __name__ == "__main__":
    main()
