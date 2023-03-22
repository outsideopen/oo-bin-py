class OOBinException(Exception):
    pass


class TunnelAlreadyStartedException(OOBinException):
    pass


class DependencyNotMetException(OOBinException):
    pass


class ConfigNotFoundException(OOBinException):
    pass


class SystemNotSupportedException(OOBinException):
    pass
