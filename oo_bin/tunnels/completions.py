import configparser
import os
from pathlib import Path

from click.shell_completion import CompletionItem
from xdg import BaseDirectory

from oo_bin.config import tunnels_config
from oo_bin.tunnels.browser_profile import BrowserProfile
from oo_bin.tunnels.tunnel_manager import TunnelManager


class Completions:
    @staticmethod
    def rdp_profile_complete(ctx, param, incomplete):
        config = tunnels_config()
        tunnels_list = list(config.keys())

        completions = [
            CompletionItem(k, help="Rdp")
            for k in tunnels_list
            if k.startswith(incomplete)
        ]

        return completions

    @staticmethod
    def rdp_host_complete(ctx, param, incomplete):
        hosts_config = (
            tunnels_config()
            .get(ctx.params["profile"], {})
            .get("rdp", {})
            .get("hosts", [])
        )

        hosts_list = [x for x in hosts_config if x.get("name", False)]

        completions = [
            CompletionItem(k.get("name"), help=f"{k.get('host')}:{k.get('port')}")
            for k in hosts_list
            if k.get("name").startswith(incomplete)
        ]

        return completions

    @staticmethod
    def socks_complete(ctx, param, incomplete):
        config = tunnels_config()
        tunnels_list = list(config.keys())
        completions = [
            CompletionItem(k, help="Socks")
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
    def vnc_profile_complete(ctx, param, incomplete):
        config = tunnels_config()
        tunnels_list = list(config.keys())

        completions = [
            CompletionItem(k, help="Vnc")
            for k in tunnels_list
            if k.startswith(incomplete)
        ]

        return completions

    @staticmethod
    def vnc_host_complete(ctx, param, incomplete):
        hosts_config = (
            tunnels_config()
            .get(ctx.params["profile"], {})
            .get("vnc", {})
            .get("hosts", [])
        )

        hosts_list = [x for x in hosts_config if x.get("name", False)]

        completions = [
            CompletionItem(k.get("name"), help=f"{k.get('host')}:{k.get('port')}")
            for k in hosts_list
            if k.get("name").startswith(incomplete)
        ]

        return completions

    @staticmethod
    def stop_complete(ctx, param, incomplete):
        tunnels = TunnelManager().tunnels()
        completions = [
            CompletionItem(k.name, help=type(k))
            for k in tunnels
            if k.name.startswith(incomplete)
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
