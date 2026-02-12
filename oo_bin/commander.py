import importlib
import importlib.util
from pathlib import Path


class Commander:
    """Not quite Cobra, but it snakes it's way through paths to find the common command format"""

    def __init__(self, path):
        self.commands = {}
        self.aliases = {}
        self.load_from_path(path)

    def find_in_path(self, path):
        shim = "shims" in path
        cmds = {}
        p = Path(path)

        def filename(file):
            return (
                str(file).replace(f"{path}/", "").replace(".py", "").replace("/", ".")
            )

        for cmd_file in p.glob("*/command/*.py"):
            module_name = filename(cmd_file)
            if "__init__" not in module_name:
                cmds[module_name] = (
                    module_name.split(".")[-1],
                    str(cmd_file) if shim else None,
                )

        for cmd_file in p.glob("*/command.py"):
            module_name = filename(cmd_file)
            cmds[module_name] = (
                module_name.split(".", 1)[0],
                str(cmd_file) if shim else None,
            )

        return cmds

    def load_from_path(self, path):
        cmds = self.find_in_path(path)
        for module_name in cmds:
            cmd_name, file = cmds[module_name]
            if file:
                spec = importlib.util.spec_from_file_location(
                    f"shim.{module_name}", file
                )
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
            else:
                module = importlib.import_module(f".{module_name}", "oo_bin")

            if hasattr(module, "replaces"):
                replaces = getattr(module, "replaces")
                for name in replaces:
                    if hasattr(module, replaces[name]):
                        self.commands[name] = getattr(module, replaces[name])
                    else:
                        raise Exception(
                            f"ERROR: could not load `{replaces[name]}` from `{module_name}`"
                        )

            if hasattr(module, cmd_name):
                if hasattr(module, "ALIAS"):
                    self.aliases[module_name] = getattr(module, "ALIAS")

                self.commands[module_name] = getattr(module, cmd_name)

    def register(self, cli):
        for cmd in self.commands:
            cli.add_command(self.commands[cmd])
            cli.add_command(self.commands[cmd], name=self.aliases[cmd]) if cmd in self.aliases else None

    def load_from_paths(self, *paths):
        # these paths are assumed to be shims as the canonical commands are registered above
        for path in paths:
            self.load_from_path(path)
