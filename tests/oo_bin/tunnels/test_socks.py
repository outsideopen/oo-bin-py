import os
from pathlib import Path

import pytest

from oo_bin.tunnels import Socks


class TestSocks:
    def test_cmd(self, mocker):
        mocker.patch(
            "oo_bin.config.main_config_path",
            os.path.join(
                Path(__file__).parent.parent.parent, "test_config", "config.toml"
            ),
        )
        mocker.patch(
            "oo_bin.config.tunnels_config_path",
            os.path.join(
                Path(__file__).parent.parent.parent, "test_config", "tunnels.toml"
            ),
        )
        socks = Socks("foo")
        print(socks._cmd)

        assert socks._cmd == [
            "autossh",
            "-N",
            "-M",
            "0",
            "-D",
            "2080",
            "-o",
            "ServerAliveInterval=3",
            "-o",
            "ServerAliveCountMax=30",
            "-F",
            "/my/ssh/config/path",
            "foo.example.com",
        ]
