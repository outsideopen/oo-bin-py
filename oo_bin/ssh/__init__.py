import os

from click.shell_completion import CompletionItem

from oo_bin.config import socks_config


class Ssh:
    def connect(self, profile):
        config = socks_config()
        section = config.get(profile, {})
        jump_host = section.get("jump_host", None)

        if jump_host:
            cmd = ["ssh", jump_host]
            os.spawnvpe(os.P_WAIT, "ssh", cmd, os.environ)

            return cmd

    @staticmethod
    def shell_complete(ctx, param, incomplete):
        config = socks_config()
        tunnels_list = list(config.keys())
        completions = [
            CompletionItem(k, help="socks")
            for k in tunnels_list
            if k.startswith(incomplete)
        ]

        return completions
