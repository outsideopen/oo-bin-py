import click
from oo_bin.dnsme import Dnsme


@click.command(help="DNS Information")
@click.argument("domain")
def dnsme(domain):
    dnsme = Dnsme(domain)
    print(dnsme)
