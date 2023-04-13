import re

import click

from oo_bin.macme import Macme


class MacType(click.ParamType):
    name = "mac"

    def convert(self, value, param, ctx):
        # strip unwanted characters, simpler validation
        mac = re.sub('[^0-9a-f]', '', value, flags=re.IGNORECASE)
        if re.match('^[0-9a-fA-F]{12}$', mac):
            # normalize to : with all upper
            return ":".join([f'{mac[i:i+2]}' for i in range(0, 12, 2)]).upper()
        else:
            self.fail(f"{value!r} is not a valid mac address", param, ctx)


@click.command(help="MAC Information")
@click.argument("mac_address", type=MacType())
def macme(mac_address):
    macme = Macme(mac_address)
    print(macme)
