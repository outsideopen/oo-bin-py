import ssl

import pytest
import trustme

from oo_bin.cert.Client import Client


@pytest.fixture(scope="session")
def httpserver_listen_address():
    return ("localhost", 8888)


@pytest.fixture(scope="session")
def ssl_cert():
    ca = trustme.CA()
    cert = ca.issue_server_cert(
        '*.example.com',
        'www.example.com',
        common_name='example.com'
    )

    return {'ca': ca, 'cert': cert}


@pytest.fixture(scope="session")
def httpserver_ssl_context(ssl_cert):
    clientContext = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    serverContext = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)

    ssl_cert['ca'].configure_trust(clientContext)
    ssl_cert['cert'].configure_cert(serverContext)

    # ca.configure_trust(clientContext)
    # serverCert.configure_cert(serverContext)

    def default_context():
        return clientContext

    ssl._create_default_https_context = default_context

    return serverContext


class TestClient:
    # def test_make_(self, mocker):
    # pass

    def test_with_only_host(self, httpserver, ssl_cert):
        client = Client('localhost', 8888)
        cert, conn = client.scan()

        assert cert.altNames == ['*.example.com', 'www.example.com']
        assert cert.commonNames == 'example.com'
