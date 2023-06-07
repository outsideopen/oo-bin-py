from click.shell_completion import CompletionItem

from oo_bin.config import rdp_config, vnc_config, socks_config
from oo_bin.tunnels.tunnel_manager import TunnelManager

from xdg import BaseDirectory
from pathlib import Path
import os
from oo_bin.tunnels.browser_profile import BrowserProfile
import configparser


class Completions:
    @staticmethod
    def rdp_complete(ctx, param, incomplete):
        config = rdp_config()
        tunnels_list = list(config.keys())

        completions = [
            CompletionItem(k, help="rdp")
            for k in tunnels_list
            if k.startswith(incomplete)
        ]

        return completions

    @staticmethod
    def socks_complete(ctx, param, incomplete):
        config = socks_config()
        tunnels_list = list(config.keys())
        completions = [
            CompletionItem(k, help="socks")
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
                {"name": "profile", "help": "Manage browser profiles"},
            ]
            if e["name"].startswith(incomplete)
        ]

        return completions + extras

    @staticmethod
    def vnc_complete(ctx, param, incomplete):
        config = vnc_config()
        tunnels_list = list(config.keys())

        completions = [
            CompletionItem(k, help="vnc")
            for k in tunnels_list
            if k.startswith(incomplete)
        ]

        return completions

    @staticmethod
    def stop_complete(ctx, param, incomplete):
        tunnels = TunnelManager().tunnels()
        completions = [
            CompletionItem(k.state.name, help=k.state.type)
            for k in tunnels
            if k.state.name.startswith(incomplete)
        ]
        return completions

    @staticmethod
    def browser_profile(ctx, param, incomplete):
        pass

    @staticmethod
    def clone_browser_profile(ctx, param, incomplete):
        primary_profile_path = BrowserProfile.primary_profile_path()

        config = configparser.ConfigParser()
        config.read(os.path.join(primary_profile_path, "profiles.ini"))

        print(config)

        profiles = []

        for key in config:
            if config[key].get("Name", None):
                profiles.append(config[key]["Name"])

        completions = [CompletionItem(k) for k in profiles if k.startswith(incomplete)]
        return completions

    @staticmethod
    def remove_browser_profile(ctx, param, incomplete):
        profiles_dir = Path(
            os.path.join(BaseDirectory.save_data_path("oo_bin"), "profiles")
        )
        profiles = sorted(profiles_dir.glob("*"), key=os.path.getmtime)

        completions = [
            CompletionItem(os.path.basename(k))
            for k in profiles
            if os.path.basename(k).startswith(incomplete)
        ]
        return completions
