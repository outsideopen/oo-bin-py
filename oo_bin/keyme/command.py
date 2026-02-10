import click

from oo_bin.keyme import Keyme


@click.command(help="Copies public SSH key to the clipboard")
@click.option("--file", default="", help="Public SSH key file")
@click.option("--save", is_flag=True, help="Save path to ssh public key")
def keyme(file, save):
    keyme = Keyme(file, save)
    print(keyme)
