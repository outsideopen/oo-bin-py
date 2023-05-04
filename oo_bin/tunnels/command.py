import click

from oo_bin.tunnels import Rdp, Socks, Vnc
from oo_bin.tunnels.tunnel_type import TunnelType


class SkipArg(click.Group):
    def parse_args(self, ctx, args):
        if len(args) > 0 and args[0] in self.commands:
            if len(args) == 1 or args[1] not in self.commands:
                # This condition needs updating for multiple positional arguments
                args.insert(0, "")
        super(SkipArg, self).parse_args(ctx, args)


@click.group(cls=SkipArg, invoke_without_command=True, help="Manage tunnels")
@click.pass_context
@click.option(
    "-u", "--update", is_flag=True, help="Update tunnels configuration from remote"
)
@click.argument("profile", shell_complete=Socks.shell_complete, required=False)
def tunnels(ctx, update, profile):
    if not profile and not update and not ctx.invoked_subcommand:
        click.echo(ctx.get_help())
        return None

    if ctx.invoked_subcommand is None:
        socks = Socks(profile)
        socks.runtime_dependencies_met()
        return socks.run({"update": update})


@tunnels.command("stop", help="Stop Socks tunnels")
@click.pass_context
@click.argument("profile", shell_complete=Socks.stop_complete, required=False)
def stop(ctx, profile):
    if not profile:
        socks = Socks(None)
        socks.stop()
    else:
        socks = Socks(profile)
        socks.stop(profile=profile)


# @click.group(cls=SkipArg, invoke_without_command=True, help="Manage RDP tunnels")
@tunnels.command(help="Manage rdp tunnels")
@click.argument("profile", shell_complete=Rdp.shell_complete, required=False)
def rdp(profile):
    if not profile:
        click.echo(click.get_current_context().get_help())
    else:
        rdp = Rdp(profile)
        rdp.runtime_dependencies_met()
        rdp.run()


@tunnels.command(help="Stop all tunnels")
def stopall():
    socks = Socks(None)
    socks.stop()


@tunnels.command(help="Tunnels status")
def status():
    socks = Socks(None)
    socks.status()


@tunnels.command(help="Manage vnc tunnels")
@click.argument("profile", shell_complete=Vnc.shell_complete, required=False)
def vnc(profile):
    if not profile:
        click.echo(click.get_current_context().get_help())
    else:
        vnc = Vnc(profile)
        vnc.runtime_dependencies_met()
        vnc.run()
