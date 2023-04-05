import os
import shutil
from subprocess import DEVNULL, Popen

from click.shell_completion import CompletionItem
from xdg import BaseDirectory

from oo_bin.config import vnc_config
from oo_bin.errors import (
    ConfigNotFoundException,
    DependencyNotMetException,
    SystemNotSupportedException,
    TunnelAlreadyStartedException,
)
from oo_bin.tunnels.tunnel import Tunnel
from oo_bin.utils import is_linux, is_mac, is_wsl, update_tunnels_config


class Vnc(Tunnel):
    def __init__(self, profile):
        super().__init__(profile)

        data_path = BaseDirectory.save_data_path("oo_bin")
        self.__pid_file__ = os.path.join(data_path, "vnc_autossh_pid")
        self.__vnc_pid_file__ = os.path.join(data_path, "vnc_pid")

    @property
    def config(self):
        config = vnc_config()

        section = config.get(self.profile, {})

        if not section:
            raise ConfigNotFoundException(
                f"{self.profile} could not be found in your configuration file"
            )

        return {
            "jump_host": section.get("jump_host", None),
            "host": section.get("host", None),
            "port": section.get("port", None),
            "forward_host": section.get("forward_host", "127.0.0.1"),
            "forward_port": section.get("forward_port", "5900"),
        }

    def stop(self):
        super().stop()

    def start(self):
        running_jump_host = self.jump_host()

        if running_jump_host:
            raise TunnelAlreadyStartedException(
                f"SSH tunnel already running to {running_jump_host}"
            )

        cmd = [
            self.__autossh_bin__,
            "-N",
            "-M",
            "0",
            "-L",
            f"{self.config['forward_host']}:{self.config['forward_port']}:{self.config['host']}:\
{self.config['port']}",
            "-o",
            "ServerAliveInterval=3",
            "-o",
            "ServerAliveCountMax=30",
            "-F",
            f"{self.__ssh_config__}",
            f"{self.config['jump_host']}",
        ]

        with open(self.__cache_file__, "a") as f1:
            pid = Popen(cmd, stdout=DEVNULL, stderr=f1).pid

            with open(self.__pid_file__, "w") as f2:
                f2.write(f"{pid}")

        self.__launch_vnc__()

    def __vnc_cmd__(self):
        if is_wsl():
            viewer = shutil.which(
                "vncviewer.exe", path="/mnt/c/Program Files/RealVNC/VNC Viewer"
            )
            return [
                viewer,
                "-useaddressbook",
                f"{self.config['forward_host']}::{self.config['forward_port']}",
            ]
        elif is_mac():
            url = f"vnc://{self.config['forward_host']:{self.config['forward_port']}}"
            return ["open", url]

        elif is_linux():
            url = f"vnc://{self.config['forward_host']}:{self.config['forward_port']}"
            print("Automatically launching VNC client on linux is not supported")
            print(f"You can manually launch your client at {url}")

            return ["true"]

        SystemNotSupportedException("Your system is not supported")

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
            raise DependencyNotMetException(
                "autossh is not installed, or is not in the path"
            )

    def run(self, args):
        if args["status"] or self.profile == "status":
            self.status()
        elif args["stop"] or self.profile == "stop":
            self.stop()
        elif args["update"]:
            update_tunnels_config()
        else:
            self.start()

    @staticmethod
    def shell_complete(ctx, param, incomplete):
        config = vnc_config()
        tunnels_list = list(config.keys())
        return [
            CompletionItem(k, help="vnc")
            for k in tunnels_list
            if k.startswith(incomplete)
        ] + [
            CompletionItem("status", help="Tunnel status"),
            CompletionItem("stop", help="Stop tunnel"),
        ]
