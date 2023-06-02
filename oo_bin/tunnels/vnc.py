import os
import shutil
import time
from subprocess import DEVNULL, Popen

from progress.bar import IncrementalBar
from xdg import BaseDirectory

from oo_bin.config import vnc_config
from oo_bin.errors import (
    ConfigNotFoundError,
    DependencyNotMetError,
    ProcessFailedError,
    SystemNotSupportedError,
)
from oo_bin.tunnels.tunnel import Tunnel
from oo_bin.tunnels.tunnel_type import TunnelType
from oo_bin.utils import is_linux, is_mac, is_wsl

# from oo_bin.tunnels.tunnel_state_manager import TunnelStateManager


class Vnc(Tunnel):
    def __init__(self, profile=None):
        super().__init__(profile)
        # state_manager = TunnelStateManager()
        # self.state = state_manager.state(self.profile)

        # self.state.type = TunnelType.VNC.value

        self.local_port = self.open_port()

        data_path = BaseDirectory.save_data_path("oo_bin")
        # self.__pid_file__ = os.path.join(
        #     data_path, f"{self.profile}_{TunnelType.VNC.value}_autossh_pid"
        # )

        self.__vnc_pid_file__ = os.path.join(data_path, "vnc_pid")

    @property
    def config(self):
        config = vnc_config()

        section = config.get(self.profile, {})

        if not section:
            raise ConfigNotFoundError(
                f"{self.profile} could not be found in your configuration file"
            )

        return {
            "jump_host": section.get("jump_host", None),
            "host": section.get("host", None),
            "port": section.get("port", "5900"),
            "local_host": "127.0.0.1",
            "local_port": section.get("local_port", self.local_port),
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

            with open(self.__pid_file__, "w") as f2:
                f2.write(f"{pid}")

            bar = IncrementalBar(
                f"Starting {self.profile}", max=10, suffix="%(percent)d%%"
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
        cmd = self.__vnc_cmd__()

        with open(self.__cache_file__, "a") as f1:
            pid = Popen(cmd, stdout=DEVNULL, stderr=f1).pid

            with open(self.__vnc_pid_file__, "w") as f2:
                f2.write(f"{pid}")

    def __kill_vnc__(self):
        try:
            with open(self.__vnc_pid_file__, "r") as f1:
                pid = f1.read()

                with open(self.__cache_file__, "a") as f2:
                    Popen(["kill", pid], stdout=DEVNULL, stderr=f2)
                    os.remove(self.__vnc_pid_file__)

        except FileNotFoundError:
            return False

        return True

    def runtime_dependencies_met(self):
        if not self.__autossh_bin__:
            raise DependencyNotMetError(
                "autossh is not installed, or is not in the path"
            )

    def run(self):
        self.start()
