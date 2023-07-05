import os
from subprocess import PIPE, Popen

from oo_bin.utils import is_linux, is_mac, is_wsl

from . import is_valid


def start_tunnel(profile):
    cmd = ["oo", "tunnels", profile]
    process = Popen(cmd, stdout=PIPE)
    output = process.communicate()
    return output


def stop_tunnel(profile=None):
    cmd = ["oo", "tunnels", "stop"]

    if profile:
        cmd.append(profile)

    process = Popen(cmd, stdout=PIPE)
    output = process.communicate()
    return output


class TestEnvironment:
    def test_browser(self):
        stop_tunnel()

        start_tunnel("oo_ssh")

        if is_mac():
            env = "Mac"
        elif is_wsl():
            env = "WSL"
        else:
            env = "Linux"

        print()
        print(f"Environment: {env}")
        print()
        assert is_valid("Did Firefox start? [y/N] ")

        print()
        assert is_valid("Did the tabs load without errors? [y/N] ")

        print()
        print("Open a new tab at about:config (accept risks)")
        print('Type "socks" in the filter bar')
        print()
        print("Check the following values:")
        print("network.proxy.socks             = 127.0.0.1")
        print("network.proxy.socks_port        = 2080")
        print("network.proxy.socks_remote_dns  = true")
        print("network.proxy.socks_version     = 5")

        print()
        assert is_valid("Are these values correct? [y/N] ")
