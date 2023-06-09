import click
from colorama import Style

from oo_bin.tunnels import Completions, TunnelManager
from oo_bin.tunnels.rdp import Rdp


class SkipArg(click.Group):
    def parse_args(self, ctx, args):
        if len(args) > 0 and args[0] in self.commands:
            if len(args) == 1 or args[1] not in self.commands:
                # This condition needs updating for multiple positional arguments
                args.insert(0, "")
                args.insert(1, "")
        super(SkipArg, self).parse_args(ctx, args)


@click.group(cls=SkipArg, invoke_without_command=True, help="Manage Rdp Tunnels")
@click.pass_context
@click.argument(
    "profile", shell_complete=Completions.rdp_profile_complete, required=False
)
@click.argument("host", shell_complete=Completions.rdp_host_complete, required=False)
def rdp(ctx, profile, host):
    if (not profile or not host) and not ctx.invoked_subcommand:
        click.echo(click.get_current_context().get_help())
        return

    if ctx.invoked_subcommand is None:
        rdp = TunnelManager().add(Rdp(profile, host))
        rdp.runtime_dependencies_met()
        rdp.start()


@rdp.command("stop", help="Stop tunnels")
@click.pass_context
@click.argument("profile", shell_complete=Completions.stop_complete, required=False)
def stop(ctx, profile):
    if profile:
        tunnel = TunnelManager().tunnel(profile)
        if tunnel:
            tunnel.stop()
            print(f"{Style.BRIGHT}{tunnel.name} has been stopped")
        else:
            print(f"{Style.BRIGHT}No process was stopped")

    else:
        tunnel_manager = TunnelManager()
        tunnel_manager.stop_all()


@rdp.command(help="Tunnels status")
def status():
    tunnel_manager = TunnelManager()
    tunnel_manager.status()
