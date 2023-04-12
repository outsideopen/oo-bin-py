import os
import shutil
import time
from subprocess import DEVNULL, Popen

from click.shell_completion import CompletionItem
from colorama import Fore
from progress.bar import IncrementalBar
from xdg import BaseDirectory

from oo_bin.config import main_config, socks5_config
from oo_bin.errors import (
    ConfigNotFoundError,
    DependencyNotMetError,
    ProcessFailedError,
    SystemNotSupportedError,
    TunnelAlreadyStartedError,
)
from oo_bin.tunnels.tunnel import Tunnel
from oo_bin.utils import is_linux, is_mac, is_wsl, update_tunnels_config


class Socks5(Tunnel):
    def __init__(self, profile):
        super().__init__(profile)

        self.__browser_bin__ = self.__browser_bin__()
        self.__browser_profile__ = (
            main_config().get("tunnels", {}).get("browser_profile", "Tunnels")
        )

        data_path = BaseDirectory.save_data_path("oo_bin")
        self.__pid_file__ = os.path.join(data_path, "socks5_autossh_pid")
        self.__firefox_pid_file__ = os.path.join(data_path, "firefox_pid")

    @property
    def config(self):
        config = socks5_config()

        section = config.get(self.profile, {})

        if not section:
            raise ConfigNotFoundError(
                f"{self.profile} could not be found in your configuration file"
            )

        return {
            "jump_host": section.get("jump_host", None),
            "forward_port": section.get("forward_port", "2080"),
            "urls": section.get("urls", None),
        }

    def __browser_bin__(self):
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
        SystemNotSupportedError("Your system is not supported")

    def stop(self):
        super().stop()

        if not is_wsl():
            self.__kill_browser__()

    def start(self):
        running_jump_host = self.jump_host()

        if running_jump_host:
            raise TunnelAlreadyStartedError(
                f"SSH tunnel already running to {running_jump_host}"
            )

        cmd = [
            self.__autossh_bin__,
            "-N",
            "-M",
            "0",
            "-D",
            f"{self.config['forward_port']}",
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
            for i in range(0, 10):
                time.sleep(0.1)
                bar.next()
                if process.poll():
                    msg = f"autossh failed after {i * 0.1}s.\
You can view the logs at {self.__cache_file__}"

                    raise ProcessFailedError(msg)
            bar.finish()

        urls = self.config["urls"]
        if urls:
            self.__launch_browser__(urls)
            print(f"Launching Firefox with tabs: {', '.join(urls)}")
        else:
            print(
                Fore.YELLOW
                + "The tunnel has been started, but you have no urls configured"
            )

    def __launch_browser__(self, urls):
        cmd = [self.__browser_bin__, "-P", self.__browser_profile__] + urls

        with open(self.__cache_file__, "a") as f1:
            pid = Popen(cmd, stdout=DEVNULL, stderr=f1).pid

            with open(self.__firefox_pid_file__, "w") as f2:
                f2.write(f"{pid}")

    def __kill_browser__(self):
        try:
            with open(self.__firefox_pid_file__, "r") as f1:
                pid = f1.read()
                with open(self.__cache_file__, "a") as f2:
                    Popen(["kill", "-9", pid], stdout=DEVNULL, stderr=f2)
                os.remove(self.__firefox_pid_file__)

        except FileNotFoundError:
            return False

        return True

    def runtime_dependencies_met(self):
        if not self.__autossh_bin__:
            raise DependencyNotMetError(
                "autossh is not installed, or is not in the path"
            )

        if not self.__browser_bin__:
            raise DependencyNotMetError(
                "firefox is not installed, or is not in the path"
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
        config = socks5_config()
        tunnels_list = list(config.keys())
        completions = [
            CompletionItem(k, help="socks5")
            for k in tunnels_list
            if k.startswith(incomplete)
        ]
        extras = [
            CompletionItem(e["name"], help=e["help"])
            for e in [
                {"name": "status", "help": "Tunnel status"},
                {"name": "stop", "help": "Stop tunnel"},
                {"name": "rdp", "help": "Manage rdp tunnels"},
                {"name": "vnc", "help": "Manage vnc tunnels"},
            ]
            if e["name"].startswith(incomplete)
        ]

        return completions + extras
