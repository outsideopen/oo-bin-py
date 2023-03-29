import os
import shutil
import sys
import time
from subprocess import DEVNULL, PIPE, Popen

from colorama import Fore
from xdg import BaseDirectory

from oo_bin.config import tunnels_config
from oo_bin.errors import (
    ConfigNotFoundException,
    DependencyNotMetException,
    SystemNotSupportedException,
    TunnelAlreadyStartedException,
)
from oo_bin.script import Script
from oo_bin.utils import is_linux, is_mac, is_wsl, update_tunnels_config


def browser_bin():
    if is_wsl():
        return shutil.which(
            "firefox.exe",
            path="/mnt/c/Program Files/Mozilla Firefox:/mnt/c/Program Files (x86)/Mozilla Firefox",
        )
    elif is_mac():
        bin = shutil.which("firefox")
        return (
            bin
            if bin
            else shutil.which(
                "firefox", path="/Applications/Firefox.app/Contents/MacOS/firefox"
            )
        )

    elif is_linux():
        return shutil.which("firefox")
    SystemNotSupportedException("Your system is not supported")


class Tunnels(Script):
    ssh_bin = "ssh" if shutil.which("ssh") else None
    autossh_bin = "autossh" if shutil.which("autossh") else None
    browser_bin = browser_bin()
    browser_profile = "Tunnels"
    forwarding_port = "2080"
    config = tunnels_config()
    data_path = BaseDirectory.save_data_path("oo_bin")
    pid_file = os.path.join(data_path, "autossh_pid")
    firefox_pid_file = os.path.join(data_path, "firefox_pid")

    def find_tunnel_name(self):
        try:
            with open(Tunnels.pid_file, "r") as f:
                pid = f.read()
                output = Popen(["ps", "-f", "-p", pid], stdout=PIPE).communicate()

                return (
                    output[0].decode("utf-8").split()[-1]
                    if len(output[0]) > 0
                    else None
                )
        except FileNotFoundError:
            return None

    def status(self):
        tunnel = self.find_tunnel_name()

        if tunnel:
            print("SSH tunnel running to " + Fore.GREEN + f"{tunnel}")
        else:
            print(Fore.YELLOW + "No SSH tunnel is running")

    def stop(self):
        try:
            with open(Tunnels.pid_file, "r") as f:
                print("Stopping tunnel to " + Fore.GREEN + f"{self.find_tunnel_name()}")
                pid = f.read()
                Popen(["kill", "-9", pid])
                os.remove(Tunnels.pid_file)

        except FileNotFoundError:
            print(Fore.YELLOW + "autossh is not running", file=sys.stderr)

        if not is_wsl():
            self.kill_browser()

    def start(self, jump_host):
        tunnel = self.find_tunnel_name()

        if tunnel:
            raise TunnelAlreadyStartedException(
                f"SSH tunnel already running to {tunnel}"
            )

        cmd = [
            Tunnels.autossh_bin,
            "-N",
            "-M",
            "0",
            "-D",
            Tunnels.forwarding_port,
            "-o",
            "ServerAliveInterval=3",
            "-o",
            "ServerAliveCountMax=30",
            f"{jump_host}",
        ]
        pid = Popen(cmd, stdout=DEVNULL, stderr=DEVNULL).pid

        with open(Tunnels.pid_file, "w") as f:
            f.write(f"{pid}")

    def launch_browser(self, urls):
        cmd = [Tunnels.browser_bin, "-P", Tunnels.browser_profile] + urls
        pid = Popen(cmd, stdout=DEVNULL, stderr=DEVNULL).pid

        with open(Tunnels.firefox_pid_file, "w") as f:
            f.write(f"{pid}")

    def kill_browser(self):
        try:
            with open(Tunnels.firefox_pid_file, "r") as f:
                pid = f.read()
                Popen(["kill", "-9", pid])
                os.remove(Tunnels.firefox_pid_file)

        except FileNotFoundError:
            return False

        return True

    def main(self, name):
        config = Tunnels.config.get(name, {})

        jump_host = config.get("jump_host", None)
        urls = config.get("urls", None)
        if jump_host:
            self.start(jump_host)
        else:
            raise ConfigNotFoundException(
                f"{name} could not be found in your configuration file"
            )

        time.sleep(1)
        if urls:
            self.launch_browser(urls)
            print(f"Launching Firefox with tabs: {', '.join(urls)}")
        else:
            print(
                Fore.YELLOW
                + "The tunnel has been started, but you have no urls configured"
            )

    @staticmethod
    def shell_complete(ctx, param, incomplete):
        tunnels_list = list(Tunnels.config.keys())
        tunnels_list.sort()
        return [
            k for k in tunnels_list + ["status", "stop"] if k.startswith(incomplete)
        ]

    @staticmethod
    def runtime_dependencies_met():
        if not Tunnels.autossh_bin:
            raise DependencyNotMetException(
                "autossh is not installed, or is not in the path"
            )

        if not Tunnels.browser_bin:
            raise DependencyNotMetException(
                "firefox is not installed, or is not in the path"
            )

    @staticmethod
    def run(args):
        tunnels = Tunnels()

        if args["status"] or args["name"] == "status":
            tunnels.status()
        elif args["stop"] or args["name"] == "stop":
            tunnels.stop()
        elif args["update"]:
            update_tunnels_config()
        else:
            if args["name"] == "":
                raise ConfigNotFoundException("You need to specify a name")
            else:
                tunnels.main(args["name"])
