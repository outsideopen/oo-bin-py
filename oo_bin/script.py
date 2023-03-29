from abc import ABC, abstractmethod


class Script(ABC):
    def __init__(self):
        self.runtime_dependencies_met()

    @staticmethod
    @abstractmethod
    def shell_complete(ctx, param, incomplete):
        raise NotImplementedError()

    @abstractmethod
    def runtime_dependencies_met():
        raise NotImplementedError()

    @abstractmethod
    def run(args):
        raise NotImplementedError()
