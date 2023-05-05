import pytest
import os
from oo_bin.ssh import Ssh
from pathlib import Path


class TestSsh:
    def test_connect(self, mocker):
        mocker.patch(
            "oo_bin.config.tunnels_config_path",
            os.path.join(
                Path(__file__).parent.parent.parent, "test_config", "tunnels.toml"
            ),
        )
        mocker.patch("os.spawnvpe", return_value=True)
        ssh = Ssh()
        command = ssh.connect("foo")

        assert command == ["ssh", "foo.example.com"]
