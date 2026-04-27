import configparser
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

import click
import tabulate as t
from colorama import Style
from xdg import BaseDirectory

from oo_bin.tunnels import Completions, TunnelManager
from oo_bin.tunnels.browser_profile import BrowserProfile
from oo_bin.tunnels.socks import Socks
from oo_bin.wordlists import generate_name


class SkipArg(click.Group):
    def parse_args(self, ctx, args):
        if len(args) > 0 and args[0] in self.commands:
            if len(args) == 1 or args[1] not in self.commands:
                # This condition needs updating for multiple positional arguments
                args.insert(0, "")
        super(SkipArg, self).parse_args(ctx, args)


@click.group(cls=SkipArg, invoke_without_command=True, help="Manage Socks Tunnels")
@click.pass_context
@click.argument("profile", shell_complete=Completions.socks_complete, required=False)
def tunnels(ctx, profile):
    if not profile and not ctx.invoked_subcommand:
        click.echo(ctx.get_help())
        return

    if ctx.invoked_subcommand is None:
        socks = TunnelManager().add(Socks(profile))
        socks.runtime_dependencies_met()
        return socks.start()


@tunnels.command("stop", help="Stop Socks tunnels")
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
        manager.stop_all(type=Socks)


@tunnels.command("stopall", help="Stop all tunnels")
def stopall():
    manager = TunnelManager()
    manager.stop_all()


@tunnels.command(help="Tunnels status")
def status():
    manager = TunnelManager()
    manager.status()


@tunnels.group()
# @click.argument("profile", shell_complete=Completions.browser_profile, required=True)
def profile():
    pass


@profile.command(help="Clone an existing browser profile")
@click.argument(
    "parent", shell_complete=Completions.clone_browser_profile, required=False
)
def clone(parent):
    profile_path = os.path.join(BrowserProfile.primary_profile_path(), "profiles.ini")
    if not os.path.exists(profile_path):
        click.secho(
            "ERROR: No profiles found, please use `oo tunnels profile new` first.",
            fg="red",
        )
        sys.exit(-1)

    config = configparser.ConfigParser()
    config.read(profile_path)

    primary_profile_path = None
    for key in config:
        if config[key].get("Name", None) == parent:
            primary_profile_path = os.path.join(
                BrowserProfile.primary_profile_path(), config[key].get("Path")
            )

    # if there is no primary profile we need to fail out again
    if not primary_profile_path:
        click.secho(
            f"ERROR: profile `{parent}` not found, please use `oo tunnels profile new` first.",
            fg="red",
        )
        sys.exit(-1)

    profile_path = os.path.join(
        BaseDirectory.save_data_path("oo_bin"), "profiles", f"{generate_name()}"
    )
    cloned = BrowserProfile.clone(
        primary_profile_path=primary_profile_path, profile_path=profile_path
    )

    profile = BrowserProfile(cloned.profile)

    with open(Path(os.path.join(profile.normalized_path, "created_at")), "w") as f:
        f.write(f"{datetime.now()}")

    click.secho(f"Profile cloned from:    {primary_profile_path}")
    click.secho(f"Created new profile at: {profile.normalized_path}")


@profile.command(help="Create a new browser profile")
def new():
    profile_path = os.path.join(
        BaseDirectory.save_data_path("oo_bin"), "profiles", f"{generate_name()}"
    )
    profile = BrowserProfile(profile_path)
    click.secho(f"Profile created at: {profile.normalized_path}")


@profile.command(help="List browser profiles")
def ls():
    profiles_dir = Path(
        os.path.join(BaseDirectory.save_data_path("oo_bin"), "profiles")
    )
    profiles = sorted(profiles_dir.glob("*"), key=os.path.getmtime)

    headers = ["Profile Name", "Profile Path"]

    table = []

    for profile in profiles:
        name = os.path.basename(profile)
        table.append(
            [
                name,
                profile,
            ]
        )

    if table:
        print(t.tabulate(table, headers, tablefmt="grid"))
    else:
        print(
            f"\nNo profiles found. Run:\n{Style.BRIGHT}oo tunnels profiles clone [parent_profile_name]"
        )


@profile.command(help="Delete browser profile")
@click.argument(
    "profile", shell_complete=Completions.remove_browser_profile, required=False
)
def rm(profile):
    dir = Path(
        os.path.join(BaseDirectory.save_data_path("oo_bin"), "profiles", profile)
    )
    shutil.rmtree(dir)

    print(f"Removed profile at {dir}")


profile.add_command(clone)
profile.add_command(ls)
profile.add_command(rm)
