import sys

import click
import colorama

from oo_bin import __version__
from oo_bin.errors import OOBinException
from oo_bin.tunnels import Rdp, Socks5, Vnc
from oo_bin.utils import auto_update

colorama.init(autoreset=True)


class SkipArg(click.Group):
    def parse_args(self, ctx, args):
        if len(args) > 0 and args[0] in self.commands:
            if len(args) == 1 or args[1] not in self.commands:
                # This condition needs updating for multiple positional arguments
                args.insert(0, "")
        super(SkipArg, self).parse_args(ctx, args)


@click.group()
@click.version_option(__version__)
def cli():
    pass


@cli.group(cls=SkipArg, invoke_without_command=True)
@click.pass_context
@click.option("-S", "--stop", is_flag=True, help="Stop all running socks5 tunnels")
@click.option("-s", "--status", is_flag=True, help="Socks5 tunnels status")
@click.option(
    "-u", "--update", is_flag=True, help="Update tunnels configuration from remote"
)
@click.argument("profile", shell_complete=Socks5.shell_complete, required=False)
# @click.argument("host", required=False)
def tunnels(ctx, status, stop, update, profile):
    if not profile and not update:
        click.echo(ctx.get_help())
        return None

    if ctx.invoked_subcommand is None:
        socks5 = Socks5(profile)
        socks5.runtime_dependencies_met()
        return socks5.run(
            {
                "stop": stop,
                "status": status,
                "update": update,
            }
        )


@tunnels.command()
@click.option("-S", "--stop", is_flag=True, help="Stop all running rdp tunnels")
@click.option("-s", "--status", is_flag=True, help="Rdp tunnels status")
@click.option(
    "-u", "--update", is_flag=True, help="Update tunnels configuration from remote"
)
@click.argument("profile", shell_complete=Rdp.shell_complete, required=False)
# @click.argument("host", required=True)
def rdp(status, stop, update, profile):
    if not profile and not update:
        click.echo(click.get_current_context().get_help())
        return None

    rdp = Rdp(profile)
    rdp.runtime_dependencies_met()
    return rdp.run({"status": status, "stop": stop, "update": update})


@tunnels.command()
@click.option("-S", "--stop", is_flag=True, help="Stop running vnc tunnels")
@click.option("-s", "--status", is_flag=True, help="Vnc tunnels status")
@click.option(
    "-u", "--update", is_flag=True, help="Update tunnels configuration from remote"
)
@click.argument("profile", shell_complete=Vnc.shell_complete, required=False)
# @click.argument("host", required=True)
def vnc(status, stop, update, profile):
    if not profile and not update:
        click.echo(click.get_current_context().get_help())
        return None

    vnc = Vnc(profile)
    vnc.runtime_dependencies_met()
    return vnc.run({"status": status, "stop": stop, "update": update})


def main():
    auto_update()

    try:
        cli()
    except OOBinException as e:
        print(colorama.Fore.RED + f"Error: {e}", file=sys.stderr)
        sys.exit(1)
