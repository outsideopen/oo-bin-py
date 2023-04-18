import click

from oo_bin.hexme import Hexme


@click.command(help="Generate a random hex")
@click.option("--chars", default=32, help="Number of characters to generate")
def hexme(chars):
    hexme = Hexme(chars)
    print(hexme)
