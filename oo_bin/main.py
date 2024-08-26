import os
import sys
import traceback
from pathlib import Path
from time import time

import click
import colorama
import sentry_sdk
from xdg import BaseDirectory

from oo_bin import __version__
from oo_bin.cert.command import cert
from oo_bin.config import main_config
from oo_bin.dnsme.command import dnsme
from oo_bin.errors import OOBinError
from oo_bin.hexme.command import hexme
from oo_bin.macme.command import macme
from oo_bin.ping.command import ping
from oo_bin.ssh.command import ssh
from oo_bin.tunnels.command import rdp, tunnels, vnc
from oo_bin.utils import auto_update, update_package, update_tunnels_config

dsn = main_config().get("sentry", {}).get("dsn", None)

sentry_sdk.init(
    dsn=dsn,
    traces_sample_rate=0.1,
)

colorama.init(autoreset=True)


@click.group(invoke_without_command=True)
@click.version_option(__version__)
@click.option("-u", "--update", is_flag=True, help="Update")
@click.option("-t", "--update-tag", help="Update to a specific release", default="")
@click.pass_context
def cli(ctx, update, update_tag):
    if update or update_tag != "":
        update_tunnels_config()
        update_package(update_tag)
        return

    if not ctx.invoked_subcommand:
        click.echo(ctx.get_help())
        return None


cli.add_command(cert)
cli.add_command(dnsme)
cli.add_command(hexme)
cli.add_command(macme)
cli.add_command(ping)
cli.add_command(rdp)
cli.add_command(ssh)
cli.add_command(tunnels)
cli.add_command(vnc)


def main():
    try:
        auto_update()
        cli()
    except OOBinError as e:
        # Handled errors, these errors should not be uploaded to sentry
        print(colorama.Fore.RED + f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        # Unhandled errors, log to file, or upload to sentry
        if dsn:
            sentry_sdk.capture_exception(e)
        else:
            error_path = Path(
                os.path.join(
                    BaseDirectory.save_data_path("oo_bin"), f"error_{int(time())}"
                )
            )
            with open(error_path, "w") as f:
                e_type, e_val, e_tb = sys.exc_info()
                traceback.print_exception(e_type, e_val, e_tb, file=f)

            report_error = f"""Report this error by sending a Slack message to the OO #dev channel.
Attach the file: {error_path}"""

        print(colorama.Fore.RED + f"Error: {e}", file=sys.stderr)

        if report_error:
            print(f"\n{report_error}")
        sys.exit(1)
