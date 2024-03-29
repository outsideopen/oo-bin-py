import os
import shutil
import sys
from pathlib import Path
from subprocess import DEVNULL, Popen

import colorama
from xdg import BaseDirectory

from oo_bin.config import tunnels_config
from oo_bin.errors import (
    DependencyNotMetError,
    PortUnavailableError,
    SystemNotSupportedError,
)
from oo_bin.tunnels.tunnel import Tunnel
from oo_bin.utils import is_autossh_running, is_linux, is_mac, is_wsl


class Rdp(Tunnel):
    def __init__(self, name, host):
        super().__init__(name)

        hosts_config = tunnels_config().get(name, {}).get("rdp", {}).get("hosts", [])
        hosts_config = [x for x in hosts_config if x.get("name", None) == host]

        if len(hosts_config) > 0:
            host_config = hosts_config[0]
            self.__host = host_config.get("host", "")
            self.__port = host_config.get("port", "3389")
        else:
            host_config = {}
            host_val = host.split(":", 1)
            self.__host = host_val[0]
            self.__port = host_val[1] if len(host_val) > 1 else "3389"

        self.__rdp_pid = None

        config_port = host_config.get("local_port", None)
        self.__local_port = config_port if config_port else self.open_port()

        self._pickle_file = Path(
            os.path.join(
                BaseDirectory.save_data_path("oo_bin"),
                f"{self.name}_{self.local_port}_rdp.pkl",
            )
        )

    @property
    def host(self):
        return self.__host

    @property
    def port(self):
        return self.__port

    @property
    def local_host(self):
        return self._config.get("local_host") or "127.0.0.1"

    @property
    def local_port(self):
        return self.__local_port

    @property
    def rdp_pid(self):
        return self.__rdp_pid

    @rdp_pid.setter
    def rdp_pid(self, value):
        self.__rdp_pid = value

    @property
    def _cmd(self):
        return [
            self._autossh_bin,
            "-N",
            "-M",
            "0",
            "-L",
            f"{self.local_port}:{self.host}:{self.port}",
            "-o",
            "ServerAliveInterval=3",
            "-o",
            "ServerAliveCountMax=30",
            "-F",
            f"{self._ssh_config}",
            f"{self.jump_host}",
        ]

    @property
    def __rdp_cmd(self):
        url = f"rdp://{self.local_host}:{self.local_port}"
        print(f"RDP url: {url}")

        if is_wsl():
            mstsc = shutil.which("mstsc.exe", path="/mnt/c/Windows/system32")

            if not mstsc:
                raise DependencyNotMetError(
                    "You need mstsc.exe installed. See: https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/mstsc"
                )
            return [
                mstsc,
                f"/v:{self.local_host}:{self.local_port}",
            ]
        elif is_mac():
            # url = f"rdp://{self.local_host}:{self.local_port}"

            # For now we only open the Microsoft RDP client.
            # If things improve with the Microsoft RDP client, maybe we can open the correct url
            return ["open", "-b", "com.microsoft.rdc.macos"]

        elif is_linux():
            print("\nAutomatically launching RDP client on linux is not supported")

            return ["true"]

        SystemNotSupportedError("Your system is not supported")

    def stop(self):
        super().stop()

        if not is_wsl() and self.is_running(self.rdp_pid):
            self.__kill_rdp()

    def start(self):
        if is_autossh_running(self.local_port):
            raise PortUnavailableError(
                f"Autossh is already running on port {self.local_port}. You need to stop this process before running tunnels."
            )

        super().start()

        self.__launch_rdp()

    def __launch_rdp(self):
        try:
            cmd = self.__rdp_cmd

            with open(self._cache_file, "a") as f:
                pid = Popen(cmd, stdout=DEVNULL, stderr=f).pid

                self.rdp_pid = pid
                self.save()

        except FileNotFoundError:
            print(
                colorama.Fore.RED + "Error: Could not find RDP executable",
                file=sys.stderr,
            )
            sys.exit(1)

    def __kill_rdp(self):
        with open(self._cache_file, "a") as f:
            Popen(["kill", str(self.rdp_pid)], stdout=DEVNULL, stderr=f)

        return True
