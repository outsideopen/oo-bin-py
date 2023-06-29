from time import sleep

from click.shell_completion import CompletionItem
from colorama import Style
from icmplib import ping

from oo_bin.config import tunnels_config


class Ping:
    def ping(self, profile):
        config = tunnels_config()
        section = config.get(profile, {})
        jump_host = section.get("jump_host", None)

        print(f"Pinging {Style.BRIGHT}{jump_host}\n")
        for i in range(0, 10):
            sleep(0.5)
            result = ping(jump_host, count=1, timeout=1, privileged=False)
            if result.is_alive:
                print(
                    f"{Style.BRIGHT}{result.address} {Style.RESET_ALL}seq={i + 1} time={round(result.min_rtt, 1)} ms"
                )
            else:
                print(
                    f"{Style.BRIGHT}{result.address} {Style.RESET_ALL}Request Timeout from seq={i + 1}"
                )

    @staticmethod
    def shell_complete(ctx, param, incomplete):
        config = tunnels_config()
        tunnels_list = list(config.keys())
        completions = [
            CompletionItem(k, help="Ping")
            for k in tunnels_list
            if k.startswith(incomplete)
        ]

        return completions
