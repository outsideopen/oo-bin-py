import shutil
import sys
import time
from subprocess import DEVNULL, Popen

import colorama
from progress.bar import IncrementalBar

from oo_bin.config import tunnels_config
from oo_bin.errors import (
    ConfigNotFoundError,
    DependencyNotMetError,
    ProcessFailedError,
    SystemNotSupportedError,
)
from oo_bin.tunnels.tunnel import Tunnel
from oo_bin.tunnels.tunnel_type import TunnelType
from oo_bin.utils import is_linux, is_mac, is_wsl


class Vnc(Tunnel):
    def __init__(self, state):
        super().__init__(state)

        self.state = state

        self.state.type = TunnelType.VNC.value

        self.local_port = self.open_port()

    @property
    def config(self):
        config = tunnels_config(profile=self.state.name)

        if not config:
            raise ConfigNotFoundError(
                f"{self.state.name} could not be found in your configuration file"
            )

        return {
            "jump_host": config.get("jump_host", None),
            "host": config.get("host", None),
            "port": config.get("port", "5900"),
            "local_host": "127.0.0.1",
            "local_port": config.get("local_port", self.local_port),
        }

    def stop(self):
        Popen(["kill", str(self.state.pid)], stdout=DEVNULL)

    def start(self):
        super().start()

        cmd = [
            self.__autossh_bin__,
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
            f"{self.__ssh_config__}",
            f"{self.config['jump_host']}",
        ]

        with open(self.__cache_file__, "a") as f1:
            process = Popen(cmd, stdout=DEVNULL, stderr=f1)
            pid = process.pid

            self.state.pid = pid
            self.state.jump_host = self.config["jump_host"]

            bar = IncrementalBar(
                f"Starting {self.state.name}", max=10, suffix="%(percent)d%%"
            )
            for i in range(0, 20):
                time.sleep(0.15)
                bar.next()
                if process.poll():
                    msg = f"autossh failed after {i * 0.15}s.\
You can view the logs at {self.__cache_file__}"

                    raise ProcessFailedError(msg)
            bar.finish()

        self.__launch_vnc__()

    def __vnc_cmd__(self):
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

    def __launch_vnc__(self):
        try:
            cmd = self.__vnc_cmd__()

            with open(self.__cache_file__, "a") as f:
                pid = Popen(cmd, stdout=DEVNULL, stderr=f).pid

                self.state.vnc_pid = pid

        except FileNotFoundError:
            print(
                colorama.Fore.RED + "Error: Could not find VNC executable",
                file=sys.stderr,
            )
            sys.exit(1)

    def __kill_vnc__(self):
        with open(self.__cache_file__, "a") as f:
            Popen(["kill", str(self.state._vnc_pid)], stdout=DEVNULL, stderr=f)

        return True

    def runtime_dependencies_met(self):
        if not self.__autossh_bin__:
            raise DependencyNotMetError(
                "autossh is not installed, or is not in the path"
            )

    def run(self):
        self.start()
