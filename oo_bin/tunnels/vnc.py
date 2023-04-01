import os
from subprocess import DEVNULL, Popen

from click.shell_completion import CompletionItem
from xdg import BaseDirectory

from oo_bin.config import vnc_config
from oo_bin.errors import (
    ConfigNotFoundException,
    DependencyNotMetException,
    TunnelAlreadyStartedException,
)
from oo_bin.tunnels.tunnel import Tunnel
from oo_bin.utils import update_tunnels_config


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
            "forward_port": section.get("forward_port", "33389"),
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
        pid = Popen(cmd, stdout=DEVNULL, stderr=DEVNULL).pid

        with open(self.__pid_file__, "w") as f:
            f.write(f"{pid}")

        self.__launch_vnc__()
        print("Launching vnc")

    def __launch_vnc__(self):
        config = vnc_config()
        forward_host = config.get("forward_host", "localhost")
        forward_port = config.get("forward_port", "5900")

        cmd = ["rdesktop", f"{forward_host}:{forward_port}"]
        pid = Popen(cmd).pid

        with open(self.__vnc_pid_file__, "w") as f:
            f.write(f"{pid}")

    def __kill_vnc__(self):
        try:
            with open(self.__vnc_pid_file__, "r") as f:
                pid = f.read()
                Popen(["kill", pid], stdout=DEVNULL, stderr=DEVNULL)
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