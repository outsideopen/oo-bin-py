import click

from oo_bin.tunnels import Completions

from oo_bin.tunnels import TunnelType

from oo_bin.tunnels.browser_profile import BrowserProfile
from oo_bin.tunnels import TunnelManager

from xdg import BaseDirectory
from colorama import Style
import os

import time
import math
import tabulate as t

from pathlib import Path
from datetime import datetime
import re
import shutil
import configparser
import namegenerator


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
        socks = TunnelManager().add(profile, TunnelType.SOCKS)
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
        rdp = TunnelManager().add(profile, TunnelType.RDP)
        rdp.runtime_dependencies_met()
        rdp.run()


@tunnels.command(help="Manage vnc tunnels")
@click.argument("profile", shell_complete=Completions.vnc_complete, required=False)
def vnc(profile):
    if not profile:
        click.echo(click.get_current_context().get_help())
    else:
        vnc = TunnelManager().add(profile, TunnelType.VNC)
        vnc.runtime_dependencies_met()
        vnc.run()


@tunnels.group()
# @click.argument("profile", shell_complete=Completions.browser_profile, required=True)
def profile():
    pass


@profile.command(help="Clone an existing browser profile")
@click.argument(
    "parent", shell_complete=Completions.clone_browser_profile, required=False
)
def clone(parent):
    config = configparser.ConfigParser()
    config.read(os.path.join(BrowserProfile.primary_profile_path(), "profiles.ini"))

    for key in config:
        if config[key].get("Name", None) == parent:
            primary_profile_path = os.path.join(
                BrowserProfile.primary_profile_path(), config[key].get("Path")
            )

    profile_path = os.path.join(
        BaseDirectory.save_data_path("oo_bin"), "profiles", f"{namegenerator.gen()}"
    )
    cloned = BrowserProfile.clone(
        primary_profile_path=primary_profile_path, profile_path=profile_path
    )

    profile = BrowserProfile(cloned.profile)

    with open(Path(os.path.join(profile.normalized_path, "created_at")), "w") as f:
        f.write(f"{datetime.now()}")

    print(
        f"Profile cloned from:    {primary_profile_path}\nCreated new profile at: {profile.normalized_path}"
    )


@profile.command(help="Create a new browser profile")
def new():
    profile_path = os.path.join(
        BaseDirectory.save_data_path("oo_bin"), "profiles", f"{namegenerator.gen()}"
    )
    profile = BrowserProfile(profile_path)
    print(f"Profile created at: {profile.normalized_path}")


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
