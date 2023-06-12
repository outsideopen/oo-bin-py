import shutil
import sys
import time
from subprocess import DEVNULL, Popen

import colorama
from progress.bar import IncrementalBar

from oo_bin.config import rdp_config
from oo_bin.errors import (
    ConfigNotFoundError,
    DependencyNotMetError,
    ProcessFailedError,
    SystemNotSupportedError,
)
from oo_bin.tunnels.tunnel import Tunnel
from oo_bin.tunnels.tunnel_type import TunnelType
from oo_bin.utils import is_linux, is_mac, is_wsl


class Rdp(Tunnel):
    def __init__(self, state):
        super().__init__(state)

        self.state = state

        self.state.type = TunnelType.RDP.value

        self.local_port = self.open_port()

    @property
    def config(self):
        config = rdp_config()

        section = config.get(self.state.name, {})

        if not section:
            raise ConfigNotFoundError(
                f"{self.state.name} could not be found in your configuration file"
            )

        return {
            "jump_host": section.get("jump_host", None),
            "user": section.get("user", None),
            "host": section.get("host", None),
            "port": section.get("port", "3389"),
            "width": section.get("width", "1920"),
            "height": section.get("height", "1080"),
            "local_host": "127.0.0.1",
            "local_port": section.get("local_port", self.local_port),
        }

    def __rdp_cmd__(self):
        if is_wsl():
            mstsc = shutil.which("mstsc.exe", path="/mnt/c/Windows/system32")
            return [
                mstsc,
                f"/w:{self.config['width']}",
                f"/h:{self.config['height']}",
                f"/v:{self.config['local_host']}:{self.config['local_port']}",
            ]
        elif is_mac():
            url = f"rdp://{self.config['local_host']:{self.config['local_port']}}"

            return ["open", url]

        elif is_linux():
            url = f"rdp://{self.config['local_host']}:{self.config['local_port']}"

            print("Automatically launching RDP client on linux is not supported")
            print(f"You can manually launch your client at {url}")

            return ["true"]

        SystemNotSupportedError("Your system is not supported")

    def stop(self):
        Popen(["kill", str(self.state.pid)], stdout=DEVNULL)

        if not is_wsl():
            self.__kill_rdp__()

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
            # self.state.forward_port = self.config["forward_port"]

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

        self.__launch_rdp__()
        print("Launching rdp")

    def __launch_rdp__(self):
        try:
            cmd = self.__rdp_cmd__()

            with open(self.__cache_file__, "a") as f:
                pid = Popen(cmd, stdout=DEVNULL, stderr=f).pid

                self.state.rdp_pid = pid

        except FileNotFoundError:
            print(
                colorama.Fore.RED + "Error: Could not find RDP executable",
                file=sys.stderr,
            )
            sys.exit(1)

    def __kill_rdp__(self):
        with open(self.__cache_file__, "a") as f:
            Popen(["kill", str(self.state.rdp_pid)], stdout=DEVNULL, stderr=f)

        return True

    def runtime_dependencies_met(self):
        if not self.__autossh_bin__:
            raise DependencyNotMetError(
                "autossh is not installed, or is not in the path"
            )

    def run(self):
        self.start()
