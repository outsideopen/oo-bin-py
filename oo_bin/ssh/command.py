import click

from oo_bin.ssh import Ssh


@click.command(help="Ssh to the profile's jump host")
@click.argument("profile", shell_complete=Ssh.profile_complete)
@click.argument("host", shell_complete=Ssh.host_complete, required=False)
def ssh(profile, host):
    ssh = Ssh()
    ssh.connect(profile, host)
