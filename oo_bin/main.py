import sys

import click
import colorama

from oo_bin import __version__
from oo_bin.commands.dnsme import dnsme
from oo_bin.commands.tunnels import tunnels
from oo_bin.errors import OOBinError
from oo_bin.utils import auto_update

colorama.init(autoreset=True)


@click.group()
@click.version_option(__version__)
def cli():
    pass


cli.add_command(dnsme)
cli.add_command(tunnels)


def main():
    auto_update()

    try:
        cli()
    except OOBinError as e:
        print(colorama.Fore.RED + f"Error: {e}", file=sys.stderr)
        sys.exit(1)
