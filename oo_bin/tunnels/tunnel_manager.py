from xdg import BaseDirectory
import os
from pathlib import Path
from oo_bin.tunnels.tunnel_state import TunnelState
import re

from singleton_decorator import singleton
from oo_bin.tunnels.tunnel import Tunnel
from oo_bin.tunnels.tunnel_type import TunnelType

from oo_bin.tunnels.rdp import Rdp
from oo_bin.tunnels.vnc import Vnc
from oo_bin.tunnels.socks import Socks
import tabulate as t
from colorama import Fore, Style
import sys


@singleton
class TunnelManager:
    def __init__(self, state_directory=None):
        state_directory = (
            state_directory
            if state_directory
            else Path(BaseDirectory.save_data_path("oo_bin"))
        )
        self.__tunnels = self.__init_tunnels(state_directory)

    def __init_tunnels(self, state_directory):
        tunnels = []
        for data_path in sorted(state_directory.glob("*.json"), key=os.path.getmtime):
            match = re.match("(.*)\.json", os.path.basename(data_path))
            profile = match[1]

            if profile:
                state = TunnelState(profile, state_file=data_path)
                if state.type == TunnelType.SOCKS.value:
                    tunnel = Socks(state)
                elif state.type == TunnelType.RDP.value:
                    tunnel = Rdp(state)
                elif state.type == TunnelType.VNC.value:
                    tunnel = Vnc(state)

                if tunnel.is_running():
                    tunnels.append(tunnel)
                else:
                    tunnel.state.delete()

        return tunnels

    def add(self, profile):
        tunnel_state = TunnelState(profile)
        tunnel = Tunnel(tunnel_state)
        self.__tunnels.append(tunnel)
        return tunnel

    def tunnel(self, profile):
        tunnels = [x for x in self.__tunnels if x.state.name == profile]

        return tunnels[0] if len(tunnels) > 0 else None

    def tunnels(self, type=None):
        if type:
            return [x for x in self.__tunnels if x.state.type == type.value]
        else:
            return [x for x in self.__tunnels]

    def status(self):
        headers = ["Profile", "Jump Host", "Type", "PID"]

        table = []
        keys = [e for e in TunnelType]

        for key in keys:
            tunnels = self.tunnels(type=key)
            for tunnel in tunnels:
                if tunnel.state.pid:
                    table.append(
                        [
                            tunnel.state.name,
                            tunnel.state.jump_host,
                            tunnel.state.type,
                            tunnel.state.pid,
                        ]
                    )

        if table:
            print(t.tabulate(table, headers, tablefmt="grid"))
        else:
            print(f"\n{Style.BRIGHT}No tunnels running!")

    def stop_all(self):
        self.stop([x.state.name for x in self.__tunnels])

    def stop(self, profiles):
        headers = ["Profile", "Jump Host", "Type", "PID"]
        table = []

        tunnels = []
        for profile in profiles:
            tunnels.append(self.tunnel(profile))

        for tunnel in tunnels:
            try:
                tunnel.stop()
                table.append(
                    [
                        tunnel.state.name,
                        tunnel.state.jump_host,
                        tunnel.state.type,
                        tunnel.state.pid,
                    ]
                )

            except FileNotFoundError:
                print(f"{Fore.YELLOW}autossh is not running", file=sys.stderr)

        if len(tunnels) > 0:
            print(f"{Style.BRIGHT}The following processes were stopped")
            print(t.tabulate(table, headers, tablefmt="grid"))
        else:
            print(f"{Style.BRIGHT}No processes were stopped")
