import sys

import click
import colorama

from oo_bin import __version__
from oo_bin.errors import OOBinException
from oo_bin.tunnels import Tunnels
from oo_bin.utils import auto_update

colorama.init(autoreset=True)


@click.group()
@click.version_option(__version__)
def cli():
    pass


@cli.command()
@click.option("-s", "--status", is_flag=True, help="Tunnels status")
@click.option("-S", "--stop", is_flag=True, help="Stop all running tunnels")
@click.option(
    "-u", "--update", is_flag=True, help="Update tunnels configuration from remote"
)
@click.argument("name", shell_complete=Tunnels.shell_complete, required=False)
def tunnels(status, stop, update, name):
    Tunnels.runtime_dependencies_met()
    return Tunnels.run({"status": status, "stop": stop, "update": update, "name": name})


def main():
    auto_update()

    try:
        cli()
    except OOBinException as e:
        print(colorama.Fore.RED + f"Error: {e}", file=sys.stderr)
        sys.exit(1)
