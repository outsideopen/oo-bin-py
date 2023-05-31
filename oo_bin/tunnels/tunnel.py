import os
import shutil
import socket

import tabulate as t
from xdg import BaseDirectory

from oo_bin.config import main_config, ssh_config_path
from oo_bin.errors import DependencyNotMetError, TunnelAlreadyStartedError
from subprocess import PIPE, Popen

t.PRESERVE_WHITESPACE = True


class Tunnel:
    def __init__(self, state):
        self.state = state

        self.__cache_file__ = os.path.join(
            BaseDirectory.save_cache_path("oo_bin"), "tunnels.log"
        )
        # Clear logfile... we only save errors for the current session
        open(self.__cache_file__, "w").close()

        self.__autossh_bin__ = "autossh" if shutil.which("autossh") else None

        self.__ssh_config__ = (
            main_config().get("tunnels", {}).get("ssh_config", ssh_config_path)
        )

    def is_running(self):
        ps_output = Popen(
            ["ps", "-f", "-p", str(self.state.pid)], stdout=PIPE
        ).communicate()

        ps_utf8 = ps_output[0].decode("utf-8") if len(ps_output[0]) > 0 else ""

        return True if len(ps_utf8.split("\n")) > 2 else False

    def start(self):
        if self.state and self.state.is_running():
            raise TunnelAlreadyStartedError(
                f"Tunnel for profile {self.state.name} already running!"
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
