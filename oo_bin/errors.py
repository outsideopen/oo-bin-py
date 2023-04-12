class OOBinError(Exception):
    pass


class ProcessFailedError(OOBinError):
    pass


class TunnelAlreadyStartedError(OOBinError):
    pass


class DependencyNotMetError(OOBinError):
    pass


class ConfigNotFoundError(OOBinError):
    pass


class SystemNotSupportedError(OOBinError):
    pass


class DomainNotExistError(OOBinError):
    pass
