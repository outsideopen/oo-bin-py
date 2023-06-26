import shutil
import sys
from subprocess import DEVNULL, Popen

import colorama

from oo_bin.errors import SystemNotSupportedError
from oo_bin.tunnels.tunnel import Tunnel
from oo_bin.utils import is_linux, is_mac, is_wsl
from oo_bin.config import tunnels_config


class Vnc(Tunnel):
    def __init__(self, name, host):
        super().__init__(name)

        hosts_config = tunnels_config().get(name, {}).get("vnc", {}).get("hosts", [])
        hosts_config = [x for x in hosts_config if x.get('name', False)]

        if len(hosts_config) > 0:
            host_config = hosts_config[0]
            self.__host = host_config.get("host", "")
            self.__port = host_config.get("port", "5900")
        else:
            host_val = host.split(":", 1)
            self.__host = host_val[0]
            self.__port = host_val[1] or "5900"
        
        self.__local_port = self.open_port()

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
        return self._config.get("local_port") or self.__local_port

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
    def __vnc_cmd(self):
        if is_wsl():
            viewer = shutil.which(
                "vncviewer.exe", path="/mnt/c/Program Files/RealVNC/VNC Viewer"
            )
            return [
                viewer,
                "-useaddressbook",
                f"{self.local_host}::{self.local_port}",
            ]
        elif is_mac():
            url = f"vnc://{self.local_host:{self.local_port}}"
            return ["open", url]

        elif is_linux():
            url = f"vnc://{self.local_host}:{self.local_port}"
            print("Automatically launching VNC client on linux is not supported")
            print(f"You can manually launch your client at {url}")

            return ["true"]

        SystemNotSupportedError("Your system is not supported")

    def stop(self):
        super().stop()

        # self.__kill_vnc()

    def start(self):
        super().start()

        self.__launch_vnc()

    def __launch_vnc(self):
        try:
            cmd = self.__vnc_cmd

            with open(self._cache_file, "a") as f:
                pid = Popen(cmd, stdout=DEVNULL, stderr=f).pid

                self.__vnc_pid = pid

        except FileNotFoundError:
            print(
                colorama.Fore.RED + "Error: Could not find VNC executable",
                file=sys.stderr,
            )
            sys.exit(1)

    def __kill_vnc(self):
        with open(self._cache_file, "a") as f:
            Popen(["kill", str(self.vnc_pid)], stdout=DEVNULL, stderr=f)

        return True
