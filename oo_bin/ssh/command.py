import click

from oo_bin.ssh import Ssh


@click.command(help="Ssh to the profile's jump host")
@click.argument("profile", shell_complete=Ssh.shell_complete)
def ssh(profile):
    ssh = Ssh()
    ssh.connect(profile)
