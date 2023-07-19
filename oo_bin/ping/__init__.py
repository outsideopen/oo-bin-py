import os

from click.shell_completion import CompletionItem

from oo_bin.config import tunnels_config
from oo_bin.utils import is_linux, is_mac, is_wsl


class Ping:
    def ping(self, profile):
        config = tunnels_config()
        section = config.get(profile, {})
        jump_host = section.get("jump_host", None)

        cmd = ["ping"]
        if is_linux() or is_wsl():
            cmd.append("-OO")
        elif is_mac():
            cmd.append("-v")

        cmd.append(jump_host)

        os.spawnvpe(os.P_WAIT, "ping", cmd, os.environ)

    @staticmethod
    def shell_complete(ctx, param, incomplete):
        config = tunnels_config()
        tunnels_list = list(config.keys())
        completions = [
            CompletionItem(k, help="Ping")
            for k in tunnels_list
            if k.startswith(incomplete)
        ]

        return completions
