import os

from click.shell_completion import CompletionItem

from oo_bin.config import tunnels_config, tunnels_config_path
from oo_bin.errors import OOBinError


class Ssh:
    def connect(self, profile, host=""):
        jump_host = tunnels_config().get(profile, {}).get("jump_host", None)
        hosts_config = tunnels_config().get(profile, {}).get("ssh", {}).get("hosts", [])
        hosts_config = [x for x in hosts_config if x.get("name", None) == host]

        ssh_host = ""
        ssh_port = "22"

        if len(hosts_config) > 0:
            host_config = hosts_config[0]
            ssh_host = host_config.get("host", "")
            ssh_port = host_config.get("port", "22")
        else:
            parsed_host = host.split(":", 1) if host else [""]

            ssh_host = parsed_host[0]

            if len(parsed_host) > 1:
                ssh_port = parsed_host[1]

        if not jump_host:
            raise OOBinError(
                f"Jump host not defined in configuration. Update {tunnels_config_path}"
            )

        ssh_config = main_config().get("tunnels", {}).get("ssh_config", ssh_config_path)
        
        if host:
            cmd = ["ssh", "-F", ssh_config, "-J", jump_host, "-p", ssh_port, ssh_host]
        else:
            cmd = ["ssh", "-F", ssh_config, jump_host]

        os.spawnvpe(os.P_WAIT, "ssh", cmd, os.environ)
        return cmd

    @staticmethod
    def profile_complete(ctx, param, incomplete):
        config = tunnels_config()
        tunnels_list = list(config.keys())
        completions = [
            CompletionItem(k, help="Ssh")
            for k in tunnels_list
            if k.startswith(incomplete)
        ]

        return completions

    @staticmethod
    def host_complete(ctx, param, incomplete):
        hosts_config = (
            tunnels_config()
            .get(ctx.params["profile"], {})
            .get("ssh", {})
            .get("hosts", [])
        )

        hosts_list = [x for x in hosts_config if x.get("name", False)]

        completions = [
            CompletionItem(k.get("name"), help=f"{k.get('host')}:{k.get('port', '22')}")
            for k in hosts_list
            if k.get("name").startswith(incomplete)
        ]

        return completions
