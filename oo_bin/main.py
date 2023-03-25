# PYTHON_ARGCOMPLETE_OK
import argparse
import sys
import argcomplete

from oo_bin.errors import OOBinException
from oo_bin.tunnels import Tunnels
from oo_bin import __version__
from oo_bin.utils import auto_update
from colorama import Fore, init

init(autoreset=True)


def main():
    auto_update()

    parser = argparse.ArgumentParser()
    parser.add_argument("--version", action="version", version=f"{__version__}")

    subparsers = parser.add_subparsers(dest="command")

    tunnels_parser = subparsers.add_parser("tunnels", help="SSH reverse tunnels")
    tunnels_parser.add_argument(
        "name",
        nargs="?",
        help="Tunnel name",
        default="",
    ).completer = Tunnels.completion

    tunnels_parser.add_argument(
        "-s", "--status", action="store_true", help="Tunnels status"
    )
    tunnels_parser.add_argument(
        "-S", "--stop", action="store_true", help="Stop all running tunnels"
    )
    tunnels_parser.add_argument(
        "-u",
        "--update",
        action="store_true",
        help="Update tunnels configuration from remote",
    )

    # NB! This line should be before `parse_args` but after adding any subparsers!
    argcomplete.autocomplete(parser)
    args = parser.parse_args()

    try:
        if args.command == "tunnels":
            Tunnels.runtime_dependencies_met()
            return Tunnels.run(args)
        else:
            raise OOBinException(
                f"Command {args.command} does not exist.",
            )
    except OOBinException as e:
        print(Fore.RED + f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    raise SystemExit(main())
