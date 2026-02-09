from oo_bin.cert.Client import Client


class Imap(Client):
    """Handles the IMAP STARTTLS connection with the server"""

    def starttls(self, socket):
        """IMAP STARTTLS"""
        # connected
        reply = socket.recv(2048).decode("utf8")
        if "\n" not in reply:
            raise Exception(f"expecting newline, got {reply}")

        # speak
        socket.sendall(f"a1 CAPABILITY\r\n".encode())
        reply = socket.recv(2048).decode("utf8")
        if "STARTTLS" not in reply:
            raise Exception("Expecting STARTTLS server capability")

        socket.sendall("a2 STARTTLS\r\n".encode())
        reply = socket.recv(2048).decode("utf8")
        if "\n" not in reply:
            raise Exception(f"Expecting `\\n`, got {reply}")
