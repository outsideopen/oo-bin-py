from oo_bin.cert.Client import Client


class Nntp(Client):
    """Handles the NNTP STARTTLS connection with the server"""

    def scan(self) -> None:
        cert, conn = super.scan()
        conn.hostnameSupport = False

        return cert,conn
    def sni(self):
        return False

    def starttls(self, socket):
        """NNTP STARTTLS"""
        # connected
        reply = socket.recv(2048).decode("utf8")
        if "\n" not in reply:
            raise Exception(f"expecting newline, got {reply}")

        socket.sendall(f"CAPABILITIES\r\n".encode())
        reply = ""
        try:
            while True:
                reply += socket.recv(2048).decode("utf8")
        except Exception:
            pass
        if "STARTTLS" not in reply:
             raise Exception("Expecting STARTTLS server capability")

        # speak
        socket.sendall(f"STARTTLS\n".encode())
        reply = socket.recv(2048).decode("utf8")
        if "382" not in reply:
            raise Exception(f"Expecting `382`, got {reply}")
