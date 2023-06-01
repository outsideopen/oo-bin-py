import click

from oo_bin.tunnels import Completions, Rdp, Socks, Vnc, Tunnel

from oo_bin.tunnels import TunnelType
from oo_bin.tunnels import TunnelState

from oo_bin.tunnels.browser_profile import BrowserProfile
from oo_bin.tunnels import TunnelManager

from colorama import Style


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
@click.argument("profile", shell_complete=Completions.socks_complete, required=False)
def tunnels(ctx, update, profile):
    if not profile and not update and not ctx.invoked_subcommand:
        click.echo(ctx.get_help())
        return None

    if ctx.invoked_subcommand is None:
        socks = Socks(TunnelState(profile))
        socks.runtime_dependencies_met()
        return socks.run({"update": update})


@tunnels.command("stop", help="Stop tunnels")
@click.pass_context
@click.argument("profile", shell_complete=Completions.stop_complete, required=False)
def stop(ctx, profile):
    if profile:
        tunnel = TunnelManager().tunnel(profile)
        if tunnel:
            tunnel.stop()
        else:
            print(f"{Style.BRIGHT}No process was stopped")

    else:
        tunnel_manager = TunnelManager()
        tunnel_manager.stop_all()


@tunnels.command(help="Tunnels status")
def status():
    tunnel_manager = TunnelManager()
    tunnel_manager.status()


@tunnels.command(help="Manage rdp tunnels")
@click.argument("profile", shell_complete=Completions.rdp_complete, required=False)
def rdp(profile):
    if not profile:
        click.echo(click.get_current_context().get_help())
    else:
        rdp = Rdp(profile)
        rdp.runtime_dependencies_met()
        rdp.run()


@tunnels.command(help="Manage vnc tunnels")
@click.argument("profile", shell_complete=Completions.vnc_complete, required=False)
def vnc(profile):
    if not profile:
        click.echo(click.get_current_context().get_help())
    else:
        vnc = Vnc(profile)
        vnc.runtime_dependencies_met()
        vnc.run()


@tunnels.group()
# @tunnels.command(help="Manage browser profiles")
def bp():
    pass


@bp.command(help="Create a new browser profile")
@click.argument("parent", shell_complete=Completions.browser_profiles, required=False)
def new(parent):
    bp = BrowserProfile(parent)


@bp.command(help="List browser profiles")
def ls():
    pass


@bp.command(help="Delete browser profile")
def rm(name):
    bp = BrowserProfile(name)
    bp.destroy()


bp.add_command(new)
bp.add_command(ls)
bp.add_command(rm)
