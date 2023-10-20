import importlib
import socket
import typing
from typing import Union

import OpenSSL.SSL
from OpenSSL import SSL

from oo_bin.cert.Model.Certificate import Certificate
from oo_bin.cert.Model.Connection import Connection

T = typing.TypeVar("T", bound="Client")


class Client:
    MAP = {
        "25": "Smtp",
        "587": "Smtp",
        "smtp": "Smtp",
        "lmtp": "Smtp",
        "110": "Pop3",
        "pop3": "Pop3",
        "143": "Imap",
        "imap": "Imap",
        "119": "Nntp",
        "433": "Nntp",
        "nntp": "Nntp",
        # 389: "Ldap",
        # 21: "Ftp",
        # XMPP/XMPP_SERVER
        # IRC
        # MYSQL
        # postgres
        # SIEVE
    }

    def __init__(self, host: str, port: int = 443):
        self.host = host
        self.port = port
        self.connection = None
        self.certificate = None

    @staticmethod
    def make(host: str, port: int | None, starttls: Union[str, bool] = "auto") -> T:
        """Detects whether a STARTTLS client should be used instead of the basic client.

        :param host: The client host. This may be a host:port combination, which will override the port param
        :param port: The client port.
        :param starttls: When set to `auto` (the default) it will detect based on known ports. `no` may be set to
                         turn off auto-detection, or the protocol to use may also be set.

        :return: Client
        """
        if ":" in host:
            (host, port) = host.split(":")

        name = None
        if type(starttls) == bool or "auto" == starttls or not starttls:
            name = Client.MAP[port] if port in Client.MAP else None
        else:
            starttls = str(starttls).lower()
            name = Client.MAP[starttls] if starttls in Client.MAP else None

        module = None
        if name:
            try:
                module = importlib.import_module(f".{name}", __name__)
            except Exception:
                pass

        kls = getattr(module, name) if module and name else Client

        return kls(host, port)

    def scan(self) -> (Certificate, Connection):
        """Retrieves the SSL Certificate, and connection information"""
        connection = None
        certificate = None

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(5)
            sock.connect((self.host, int(self.port)))

            # if the Client has this filled out it'll be used
            self.starttls(sock)

            # Initiate the OpenSSL context to get the rest of the information
            ctx = SSL.Context(SSL.TLS_CLIENT_METHOD)
            ssl = SSL.Connection(ctx, socket=sock)

            ssl.setblocking(1)
            ssl.set_tlsext_host_name(self.host.encode("utf-8"))
            ssl.set_connect_state()
            ssl.do_handshake()

            (ip, port) = sock.getpeername()
            connection = Connection.parse(self.host, ip, ssl)
            certificate = Certificate.parse(self.host, ssl.get_peer_certificate())

        return certificate, connection

    def starttls(self, sock: socket) -> None:
        """Handle the STARTTLS negotiation before handing to OpenSSL"""
        pass
