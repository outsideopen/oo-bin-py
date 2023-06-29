import click

from oo_bin.ping import Ping


@click.command(help="Ping the jump host")
@click.argument("profile", shell_complete=Ping.shell_complete)
def ping(profile):
    ping = Ping()
    ping.ping(profile)
