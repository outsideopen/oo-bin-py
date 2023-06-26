import shutil
import sys
from subprocess import DEVNULL, Popen

import colorama

from oo_bin.errors import DependencyNotMetError, SystemNotSupportedError
from oo_bin.tunnels.tunnel import Tunnel
from oo_bin.utils import is_linux, is_mac, is_wsl


class Vnc(Tunnel):
    def __init__(self):
        super().__init__()

        self.local_port = self.open_port()

    # @property
    # def config(self):
    #     config = tunnels_config(profile=self.name)

    #     if not config:
    #         raise ConfigNotFoundError(
    #             f"{self.name} could not be found in your configuration file"
    #         )

    #     return {
    #         "jump_host": config.get("jump_host", None),
    #         "host": config.get("host", None),
    #         "port": config.get("port", "5900"),
    #         "local_host": "127.0.0.1",
    #         "local_port": config.get("local_port", self.local_port),
    #     }

    @property
    def _cmd(self):
        return [
            self._autossh_bin,
            "-N",
            "-M",
            "0",
            "-L",
            f"{self.config['local_port']}:{self.config['host']}:{self.config['port']}",
            "-o",
            "ServerAliveInterval=3",
            "-o",
            "ServerAliveCountMax=30",
            "-F",
            f"{self._ssh_config}",
            f"{self.config['jump_host']}",
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
                f"{self.config['local_host']}::{self.config['local_port']}",
            ]
        elif is_mac():
            url = f"vnc://{self.config['local_host']:{self.config['local_port']}}"
            return ["open", url]

        elif is_linux():
            url = f"vnc://{self.config['local_host']}:{self.config['local_port']}"
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

    def runtime_dependencies_met(self):
        if not self._autossh_bin:
            raise DependencyNotMetError(
                "autossh is not installed, or is not in the path"
            )
