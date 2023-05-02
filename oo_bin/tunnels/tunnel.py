import os
import shutil
import socket
import sys
from pathlib import Path

import tabulate as t
from colorama import Fore, Style
from xdg import BaseDirectory

from oo_bin.config import main_config, ssh_config_path
from oo_bin.errors import DependencyNotMetError, TunnelAlreadyStartedError
from oo_bin.script import Script
from oo_bin.tunnels.tunnel_process import TunnelProcess
from oo_bin.tunnels.tunnel_type import TunnelType

t.PRESERVE_WHITESPACE = True


class Tunnel(Script):
    def __init__(self, profile):
        self.profile = profile
        self.forward_port = self.open_port()
        self.tunnel_processes = self.__tunnel_processes__()

        self.__cache_file__ = os.path.join(
            BaseDirectory.save_cache_path("oo_bin"), "tunnels.log"
        )
        # Clear logfile... we only save errors for the current session
        open(self.__cache_file__, "w").close()

        self.__autossh_bin__ = "autossh" if shutil.which("autossh") else None

        self.__ssh_config__ = (
            main_config().get("tunnels", {}).get("ssh_config", ssh_config_path)
        )

    def __tunnel_processes__(self, type=None):
        data_path = BaseDirectory.save_data_path("oo_bin")

        processes = []
        if not type or type == TunnelType.SOCKS:
            processes += [
                TunnelProcess(TunnelType.SOCKS, x)
                for x in sorted(Path(data_path).glob("*_Socks_*"), key=os.path.getmtime)
            ]

        if not type or type == TunnelType.RDP:
            processes += [
                TunnelProcess(TunnelType.RDP, x)
                for x in sorted(Path(data_path).glob("*_Rdp_*"), key=os.path.getmtime)
            ]

        if not type or type == TunnelType.VNC:
            processes += [
                TunnelProcess(TunnelType.VNC, x)
                for x in sorted(Path(data_path).glob("*_Vnc_*"), key=os.path.getmtime)
            ]
        return processes

    def __tunnel_process__(self, profile):
        tunnel_processes = [
            x for x in self.__tunnel_processes__() if profile == x.profile
        ]
        return tunnel_processes[0] if tunnel_processes else None

    def status(self):
        headers = ["Profile", "Jump Host", "Type", "PID"]

        table = []
        keys = [e for e in TunnelType]

        for key in keys:
            tunnel_processes = [x for x in self.tunnel_processes if key == x.type]
            for tunnel_process in tunnel_processes:
                if tunnel_process.pid:
                    table.append(
                        [
                            tunnel_process.profile,
                            tunnel_process.jump_host,
                            tunnel_process.type.value,
                            tunnel_process.pid,
                        ]
                    )

        if table:
            print(t.tabulate(table, headers, tablefmt="grid"))
        else:
            print(f"\n{Style.BRIGHT}No tunnels running!")

    def stop(self, type=None, profile=None):
        headers = ["Profile", "Jump Host", "Type", "PID"]
        table = []

        processes = []
        if type:
            processes = self.__tunnel_processes__(type=type)
        elif profile:
            process = self.__tunnel_process__(profile)
            processes = [process] if process else []
        else:
            processes = self.__tunnel_processes__(type=type)

        for process in processes:
            try:
                process.stop()
                table.append(
                    [
                        process.profile,
                        process.jump_host,
                        process.type.value,
                        process.pid,
                    ]
                )

            except FileNotFoundError:
                print(f"{Fore.YELLOW}autossh is not running", file=sys.stderr)

        if len(processes) > 0:
            print(f"{Style.BRIGHT}The following processes were stopped")
            print(t.tabulate(table, headers, tablefmt="grid"))
        else:
            print(f"{Style.BRIGHT}No processes were stopped")

    def start(self):
        tunnel_process = self.__tunnel_process__(self.profile)

        if tunnel_process:
            raise TunnelAlreadyStartedError(
                f"Tunnel for profile {self.profile} already running!"
            )

    def runtime_dependencies_met(self):
        if not self.__autossh_bin__:
            raise DependencyNotMetError(
                "autossh is not installed, or is not in the path"
            )

    def open_port(self):
        sock = socket.socket()
        sock.bind(("", 0))
        return sock.getsockname()[1]
