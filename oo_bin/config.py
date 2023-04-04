import os
from shutil import copyfile
from os.path import exists

from xdg import BaseDirectory

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

__package_name__ = "oo_bin"

main_config_path = os.path.join(
    BaseDirectory.save_config_path(__package_name__), "config.toml"
)
tunnels_config_path = os.path.join(
    BaseDirectory.save_config_path(__package_name__), "tunnels.toml"
)


def __get_config__(path):
    try:
        with open(path, "rb") as f:
            data = tomllib.load(f)
            return data
    except FileNotFoundError:
        return {}


def main_config():
    return __get_config__(main_config_path)


def backup_tunnels_config():
    if exists(tunnels_config_path):
        tunnels_bak = os.path.join(
            BaseDirectory.save_config_path(__package_name__), "tunnels.toml.bak"
        )
        copyfile(tunnels_config_path, tunnels_bak)


def tunnels_config():
    return __get_config__(tunnels_config_path)


def rdp_config():
    config = tunnels_config()
    rdp_config = {k: v for k, v in config.items() if v.get("type", "socks5") == "rdp"}
    return rdp_config


def socks5_config():
    config = tunnels_config()
    socks5_config = {
        k: v for k, v in config.items() if v.get("type", "socks5") == "socks5"
    }
    return socks5_config


def vnc_config():
    config = tunnels_config()
    vnc_config = {k: v for k, v in config.items() if v.get("type", "socks5") == "vnc"}
    return vnc_config
