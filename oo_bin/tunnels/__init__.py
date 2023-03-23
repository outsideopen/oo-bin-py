import shutil
import sys
import time
from subprocess import DEVNULL, PIPE, Popen

from colorama import Fore

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

    def find_tunnel_process(self, cmd):
        p1 = Popen(["ps", "-ef"], stdout=PIPE)
        p2 = Popen(["grep", cmd], stdin=p1.stdout, stdout=PIPE)
        p3 = Popen(["grep", Tunnels.forwarding_port], stdin=p2.stdout, stdout=PIPE)
        p4 = Popen(["grep", "-v", "grep"], stdin=p3.stdout, stdout=PIPE)
        return p4.communicate()

    def find_tunnel_process_id(self, cmd):
        output = self.find_tunnel_process(cmd)
        return output[0].decode("utf-8").split()[1] if len(output[0]) > 0 else None

    def find_tunnel_name(self):
        output = self.find_tunnel_process(Tunnels.autossh_bin)
        return output[0].decode("utf-8").split()[-1] if len(output[0]) > 0 else None

    def status(self):
        tunnel = self.find_tunnel_name()

        if tunnel:
            print("Dynamic SSH tunnel running to " + Fore.GREEN + f"{tunnel}")
        else:
            print(Fore.YELLOW + "No dynamic SSH tunnels running")

    def stop(self):
        print("Stopping tunnels")
        for cmd in [Tunnels.autossh_bin, Tunnels.ssh_bin]:
            pid = self.find_tunnel_process_id(cmd)

            if not pid:
                print(Fore.YELLOW + f"{cmd} is not running", file=sys.stderr)
            else:
                Popen(["kill", "-9", pid])
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
        Popen(cmd, stdout=DEVNULL, stderr=DEVNULL)

    def launch_browser(self, urls):
        cmd = [Tunnels.browser_bin, "-P", Tunnels.browser_profile] + urls
        Popen(cmd, stdout=DEVNULL, stderr=DEVNULL)

    def kill_browser(self):
        p1 = Popen(["ps", "-ef"], stdout=PIPE)
        p2 = Popen(
            ["grep", "-i", Tunnels.browser_bin.split("/")[-1]],
            stdin=p1.stdout,
            stdout=PIPE,
        )
        p3 = Popen(
            ["grep", "-i", Tunnels.browser_profile], stdin=p2.stdout, stdout=PIPE
        )
        p4 = Popen(["grep", "-v", "grep"], stdin=p3.stdout, stdout=PIPE)
        output = p4.communicate()

        pid = output[0].decode("utf-8").split()[1] if len(output[0]) > 0 else None

        if not pid:
            return False
        else:
            Popen(["kill", "-9", pid])

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
    def completion(prefix, parsed_args, **kwargs):
        return tuple(Tunnels.config.keys())

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

        if args.status or args.name == "status":
            tunnels.status()
        elif args.stop or args.name == "stop":
            tunnels.stop()
        elif args.update:
            update_tunnels_config()
        else:
            if args.name == "":
                raise ConfigNotFoundException("You need to specify a name")
            else:
                tunnels.main(args.name)
