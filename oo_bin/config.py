import os
from shutil import copyfile

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
    with open(path, "rb") as f:
        data = tomllib.load(f)
        return data


def main_config():
    return __get_config__(main_config_path)


def backup_tunnels_config():
    tunnels_bak = os.path.join(
        BaseDirectory.save_config_path(__package_name__), "tunnels.toml.bak"
    )
    copyfile(tunnels_config_path, tunnels_bak)


def tunnels_config():
    return __get_config__(tunnels_config_path)
