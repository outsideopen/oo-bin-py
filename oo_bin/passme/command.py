import click

from oo_bin.passme import Passme


@click.command(help="Generate a secure password and copy it to the clipboard.")
def passme():
    passme = Passme()
    print(passme)
