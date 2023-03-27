from abc import ABC, abstractmethod


class Script(ABC):
    def __init__(self):
        pass

    @staticmethod
    @abstractmethod
    def shell_complete(ctx, param, incomplete):
        raise NotImplementedError()

    @staticmethod
    @abstractmethod
    def runtime_dependencies_met():
        raise NotImplementedError()

    @staticmethod
    @abstractmethod
    def run(args):
        raise NotImplementedError()
