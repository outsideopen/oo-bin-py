class OOBinError(Exception):
    pass


class TunnelAlreadyStartedError(OOBinError):
    pass


class DependencyNotMetError(OOBinError):
    pass


class ConfigNotFoundError(OOBinError):
    pass


class SystemNotSupportedError(OOBinError):
    pass
