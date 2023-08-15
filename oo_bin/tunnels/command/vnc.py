import click
from colorama import Style

from oo_bin.tunnels import Completions, TunnelManager
from oo_bin.tunnels.vnc import Vnc


class SkipArg(click.Group):
    def parse_args(self, ctx, args):
        if len(args) > 0 and args[0] in self.commands:
            if len(args) == 1 or args[1] not in self.commands:
                # This condition needs updating for multiple positional arguments
                args.insert(0, "")
                args.insert(1, "")
        super(SkipArg, self).parse_args(ctx, args)


@click.group(cls=SkipArg, invoke_without_command=True, help="Manage Vnc Tunnels")
@click.pass_context
@click.argument(
    "profile", shell_complete=Completions.vnc_profile_complete, required=False
)
@click.argument("host", shell_complete=Completions.vnc_host_complete, required=False)
def vnc(ctx, profile, host):
    if (not profile or not host) and not ctx.invoked_subcommand:
        click.echo(click.get_current_context().get_help())
        return

    if ctx.invoked_subcommand is None:
        vnc = TunnelManager().add(Vnc(profile, host))
        vnc.runtime_dependencies_met()
        vnc.start()


@vnc.command("stop", help="Stop Vnc tunnels")
@click.argument("profile", shell_complete=Completions.stop_complete, required=False)
def stop(profile):
    manager = TunnelManager()
    if profile:
        tunnel = manager.tunnel(profile)
        if tunnel:
            manager.stop([tunnel])
        else:
            manager.stop([])
    else:
        manager.stop_all(type=Vnc)


@vnc.command("stopall", help="Stop all tunnels")
def stopall():
    manager = TunnelManager()
    manager.stop_all()


@vnc.command(help="Tunnels status")
def status():
    manager = TunnelManager()
    manager.status()
