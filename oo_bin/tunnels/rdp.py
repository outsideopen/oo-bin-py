import os
import shutil
import sys
from subprocess import DEVNULL, Popen

import colorama
from click.shell_completion import CompletionItem
from xdg import BaseDirectory

from oo_bin.config import rdp_config
from oo_bin.errors import (
    ConfigNotFoundException,
    DependencyNotMetException,
    SystemNotSupportedException,
)
from oo_bin.tunnels.tunnel import Tunnel
from oo_bin.utils import is_linux, is_mac, is_wsl, update_tunnels_config


class Rdp(Tunnel):
    def __init__(self, profile):
        super().__init__(profile)

        data_path = BaseDirectory.save_data_path("oo_bin")
        self.__pid_file__ = os.path.join(data_path, "rdp_autossh_pid")
        self.__rdp_pid_file__ = os.path.join(data_path, "rdp_pid")

    @property
    def config(self):
        config = rdp_config()

        section = config.get(self.profile, {})

        if not section:
            raise ConfigNotFoundException(
                f"{self.profile} could not be found in your configuration file"
            )

        return {
            "jump_host": section.get("jump_host", None),
            "user": section.get("user", None),
            "host": section.get("host", None),
            "port": section.get("port", None),
            "width": section.get("width", "1920"),
            "height": section.get("height", "1080"),
            "forward_host": section.get("forward_host", "127.0.0.1"),
            "forward_port": section.get("forward_port", "33389"),
        }

    def __rdp_cmd__(self):
        if is_wsl():
            mstsc = shutil.which("mstsc.exe", path="/mnt/c/Windows/system32")
            return [
                mstsc,
                f"/w:{self.config['width']}",
                f"/h:{self.config['height']}",
                f"/v:{self.config['forward_host']}:{self.config['forward_port']}",
            ]
        elif is_mac():
            url = f"rdp://{self.config['forward_host']:{self.config['forward_port']}}"

            return ["open", url]

        elif is_linux():
            url = f"rdp://{self.config['forward_host']}:{self.config['forward_port']}"

            print("Automatically launching RDP client on linux is not supported")
            print(f"You can manually launch your client at {url}")

            return ["true"]

        SystemNotSupportedException("Your system is not supported")

    def stop(self):
        super().stop()

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
            f"{self.config['forward_host']}:{self.config['forward_port']}:{self.config['host']}:{self.config['port']}",
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

        self.__launch_rdp__()
        print("Launching rdp")

    def __launch_rdp__(self):
        try:
            cmd = self.__rdp_cmd__()

            with open(self.__cache_file__, "a") as f1:
                pid = Popen(cmd, stdout=DEVNULL, stderr=f1).pid

                with open(self.__rdp_pid_file__, "w") as f2:
                    f2.write(f"{pid}")

        except TypeError:
            print(
                colorama.Fore.RED + f"Error: Could not find RDP executable",
                file=sys.stderr,
            )
            sys.exit(1)

    def __kill_rdp__(self):
        try:
            with open(self.__rdp_pid_file__, "r") as f1:
                pid = f1.read()

                with open(self.__cache_file__, "a") as f2:
                    Popen(["kill", pid], stdout=DEVNULL, stderr=f2)
                os.remove(self.__rdp_pid_file__)

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
        config = rdp_config()
        tunnels_list = list(config.keys())

        completions = [
            CompletionItem(k, help="rdp")
            for k in tunnels_list
            if k.startswith(incomplete)
        ]
        extras = [
            CompletionItem(e["name"], help=e["help"])
            for e in [
                {"name": "status", "help": "Tunnel status"},
                {"name": "stop", "help": "Stop tunnel"},
            ]
            if e["name"].startswith(incomplete)
        ]

        return completions + extras
