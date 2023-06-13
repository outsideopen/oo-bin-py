import sys

import click
import colorama

from oo_bin import __version__
from oo_bin.dnsme.command import dnsme
from oo_bin.errors import OOBinError
from oo_bin.hexme.command import hexme
from oo_bin.macme.command import macme
from oo_bin.ssh.command import ssh
from oo_bin.tunnels.command import tunnels
from oo_bin.utils import auto_update, update_package

colorama.init(autoreset=True)


@click.group(invoke_without_command=True)
@click.version_option(__version__)
@click.option("-u", "--update", is_flag=True, help="Update tunnels package")
@click.pass_context
def cli(ctx, update):
    if update:
        return update_package()

    if not ctx.invoked_subcommand:
        click.echo(ctx.get_help())
        return None


cli.add_command(dnsme)
cli.add_command(hexme)
cli.add_command(macme)
cli.add_command(ssh)
cli.add_command(tunnels)


def main():
    auto_update()

    try:
        cli()
    except OOBinError as e:
        print(colorama.Fore.RED + f"Error: {e}", file=sys.stderr)
        sys.exit(1)
