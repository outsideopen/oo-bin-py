__version__ = "0.0.1"

# PYTHON_ARGCOMPLETE_OK
import argparse
import sys
from collections.abc import Sequence

import argcomplete

from oo_bin.errors import OOBinException
from oo_bin.tunnels import Tunnels


def main(argv: Sequence[str] | None = None):
    parser = argparse.ArgumentParser()
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

    # NB! This line should be before `parse_args` but after adding any subparsers!
    argcomplete.autocomplete(parser)
    args = parser.parse_args(argv)

    try:
        if args.command == "tunnels":
            Tunnels.runtime_dependencies_met()
            return Tunnels.run(args)
        else:
            raise NotImplementedError(
                f"Command {args.command} does not exist.",
            )
    except OOBinException as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    raise SystemExit(main())
