import os
from pathlib import Path

from oo_bin.tunnels import Vnc


class TestVnc:
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
        rdp1 = Vnc("foo", "first_vnc")
        assert rdp1._cmd == [
            "autossh",
            "-N",
            "-M",
            "0",
            "-L",
            "60011:192.168.2.1:5900",
            "-o",
            "ServerAliveInterval=3",
            "-o",
            "ServerAliveCountMax=30",
            "-F",
            "/my/ssh/config/path",
            "foo.example.com",
        ]

        rdp2 = Vnc("foo", "second_vnc")
        assert rdp2._cmd == [
            "autossh",
            "-N",
            "-M",
            "0",
            "-L",
            "60012:192.168.2.2:5900",
            "-o",
            "ServerAliveInterval=3",
            "-o",
            "ServerAliveCountMax=30",
            "-F",
            "/my/ssh/config/path",
            "foo.example.com",
        ]
