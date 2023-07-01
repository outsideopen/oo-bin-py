import os
from pathlib import Path

from oo_bin.tunnels import Rdp


class TestRdp:
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
        rdp1 = Rdp("foo", "first_rdp")
        assert rdp1._cmd == [
            "autossh",
            "-N",
            "-M",
            "0",
            "-L",
            "60001:192.168.1.1:3389",
            "-o",
            "ServerAliveInterval=3",
            "-o",
            "ServerAliveCountMax=30",
            "-F",
            "/my/ssh/config/path",
            "foo.example.com",
        ]

        rdp2 = Rdp("foo", "second_rdp")
        assert rdp2._cmd == [
            "autossh",
            "-N",
            "-M",
            "0",
            "-L",
            "60002:192.168.1.2:3389",
            "-o",
            "ServerAliveInterval=3",
            "-o",
            "ServerAliveCountMax=30",
            "-F",
            "/my/ssh/config/path",
            "foo.example.com",
        ]
