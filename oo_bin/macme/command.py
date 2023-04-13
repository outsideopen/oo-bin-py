import re

import click

from oo_bin.macme import Macme


class MacType(click.ParamType):
    name = "mac"

    def convert(self, value, param, ctx):
        regex = r"^([0-9a-fA-F]{2}[-|:|\.]){5}[0-9a-fA-F]{2}|[0-9a-fA-F]{12}|([0-9a-fA-F]{4}[\.]){2}[0-9a-fA-F]{4}$"
        p = re.compile(regex)
        if re.match(p, value):
            return value
        else:
            self.fail(f"{value!r} is not a valid mac address", param, ctx)


@click.command(help="MAC Information")
@click.argument("mac_address", type=MacType())
def macme(mac_address):
    macme = Macme(mac_address)
    print(macme)
