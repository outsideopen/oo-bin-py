import os
import shutil
import sys
from subprocess import DEVNULL, PIPE, Popen

from xdg import BaseDirectory

from oo_bin.errors import (
    ConfigNotFoundException,
    DependencyNotMetException,
    TunnelAlreadyStartedException,
)
from oo_bin.script import Script
from oo_bin.utils import is_wsl


def browser_bin():
    if is_wsl():
        return shutil.which(
            "firefox.exe",
            path="/mnt/c/Program Files/Mozilla Firefox:/mnt/c/Program Files (x86)/Mozilla Firefox",
        )
    else:
        return shutil.which("firefox")


class Tunnels(Script):
    tunnels_conf = os.path.join(
        BaseDirectory.load_first_config("oo_bin"), "tunnels.conf"
    )
    ssh_bin = shutil.which("ssh")
    autossh_bin = shutil.which("autossh")
    browser_bin = browser_bin()
    browser_profile = "Tunnels"

    def find_tunnel(self):
        p1 = Popen(["ps", "-ef"], stdout=PIPE)
        p2 = Popen(["grep", Tunnels.autossh_bin], stdin=p1.stdout, stdout=PIPE)
        p3 = Popen(["grep", "2080"], stdin=p2.stdout, stdout=PIPE)
        p4 = Popen(["grep", "-v", "grep"], stdin=p3.stdout, stdout=PIPE)
        output = p4.communicate()

        return output[0].decode("utf-8").split()[-1] if len(output[0]) > 0 else None

    def get_config(self, name):
        with open(Tunnels.tunnels_conf) as f:
            lines = f.readlines()

            for line in lines:
                (_name, jump_host, urls) = line.split(",", 3)
                if _name == name:
                    return (name, jump_host, urls)

        raise ConfigNotFoundException(
            f"{name} could not be found in your configuration file"
        )

    def status(self):
        tunnel = self.find_tunnel()

        if tunnel:
            print(f"Dynamic SSH tunnel running to {tunnel}...")
        else:
            print("No dynamic SSH tunnels running...")

    def stop(self):
        print("Stopping tunnels...")
        for cmd in [Tunnels.autossh_bin, Tunnels.ssh_bin]:
            p1 = Popen(["ps", "-ef"], stdout=PIPE)
            p2 = Popen(["grep", cmd], stdin=p1.stdout, stdout=PIPE)
            p3 = Popen(["grep", "2080"], stdin=p2.stdout, stdout=PIPE)
            p4 = Popen(["grep", "-v", "grep"], stdin=p3.stdout, stdout=PIPE)
            output = p4.communicate()

            pid = output[0].decode("utf-8").split()[1] if len(output[0]) > 0 else None

            if not pid:
                print(f"{cmd} is not running", file=sys.stderr)
            else:
                Popen(["kill", "-9", pid])

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
            print(
                f"{Tunnels.browser_bin} with profile {Tunnels.browser_profile} is not running",
                file=sys.stderr,
            )
        else:
            Popen(["kill", "-9", pid])

    def start(self, jump_host):
        tunnel = self.find_tunnel()

        if tunnel:
            raise TunnelAlreadyStartedException(
                f"SSH tunnel already running to {tunnel}..."
            )

        cmd = [
            Tunnels.autossh_bin,
            "-N",
            "-M",
            "0",
            "-D",
            "2080",
            "-o",
            "ServerAliveInterval=3",
            "-o",
            "ServerAliveCountMax=30",
            f"{jump_host}",
        ]
        Popen(cmd, stdout=DEVNULL, stderr=DEVNULL)

    def launch_browser(self, urls):
        cmd = [Tunnels.browser_bin, "-P", Tunnels.browser_profile] + urls.split()
        Popen(cmd, stdout=DEVNULL, stderr=DEVNULL)

    def main(self, name):
        (_name, jump_host, urls) = self.get_config(name)

        self.start(jump_host)
        self.launch_browser(urls)
        print(f"Launching Firefox... {urls}")

    @staticmethod
    def completion(prefix, parsed_args, **kwargs):
        return_list = []
        with open(Tunnels.tunnels_conf) as f:
            lines = f.readlines()

            for line in lines:
                vals = line.split(",", 1)
                return_list.append(vals[0])

        return tuple(return_list)

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

        if args.status:
            tunnels.status()
        elif args.stop:
            tunnels.stop()
        else:
            if args.name == "":
                raise ConfigNotFoundException("You need to specify a name")
            else:
                tunnels.main(args.name)
