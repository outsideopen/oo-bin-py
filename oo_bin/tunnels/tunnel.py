import os
import shutil
import sys
from subprocess import DEVNULL, PIPE, Popen

from colorama import Fore
from xdg import BaseDirectory

from oo_bin.config import main_config
from oo_bin.errors import DependencyNotMetException, TunnelAlreadyStartedException
from oo_bin.script import Script


class Tunnel(Script):
    def __init__(self, profile):
        self.profile = profile
        self.__cache_file__ = os.path.join(
            BaseDirectory.save_cache_path("oo_bin"), "tunnels.log"
        )
        # Clear logfile... we only save errors for the current session
        open(self.__cache_file__, "w").close()

        self.__autossh_bin__ = "autossh" if shutil.which("autossh") else None

        self.__ssh_config__ = os.path.expanduser(
            main_config()
            .get("tunnels", {})
            .get("ssh_config", os.path.expanduser("~/.ssh/config"))
        )

    def jump_host(self):
        try:
            with open(self.__pid_file__, "r") as f:
                pid = f.read()
                output = Popen(["ps", "-f", "-p", pid], stdout=PIPE).communicate()
                if len(output[0]) > 0:
                    output = output[0].decode("utf-8")
                else:
                    return None

                if len(output.split("\n")) > 1:
                    output = output.split("\n")[1]
                else:
                    return None
                if len(output) > 0:
                    return output.split()[-1].strip()

                return None

        except FileNotFoundError:
            return None

    def status(self):
        jump_host = self.jump_host()

        if jump_host:
            print("SSH tunnel running to " + Fore.GREEN + f"{jump_host}")
        else:
            print(Fore.YELLOW + "No SSH tunnel is running")

    def stop(self):
        try:
            with open(self.__pid_file__, "r") as f1:
                print("Stopping tunnel to " + Fore.GREEN + f"{self.jump_host()}")
                pid = f1.read()

                with open(self.__cache_file__, "w+") as f2:
                    Popen(["kill", pid], stdout=DEVNULL, stderr=f2)
                    os.remove(self.__pid_file__)

        except FileNotFoundError:
            print(Fore.YELLOW + "autossh is not running", file=sys.stderr)

    def start(self):
        running_jump_host = self.jump_host()

        if running_jump_host:
            raise TunnelAlreadyStartedException(
                f"SSH tunnel already running to {running_jump_host}"
            )

    def runtime_dependencies_met(self):
        if not self.__autossh_bin__:
            raise DependencyNotMetException(
                "autossh is not installed, or is not in the path"
            )
