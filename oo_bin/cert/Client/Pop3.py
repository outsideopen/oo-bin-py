from oo_bin.cert.Client import Client


class Pop3(Client):
    """Handles the POP3 STARTTLS connection with the server"""

    def starttls(self, socket):
        """POP3 STARTTLS"""
        # connected
        reply = socket.recv(2048).decode("utf8")
        if "\n" not in reply:
            raise Exception(f"expecting newline, got {reply}")

        # speak
        socket.sendall(f"STLS\n".encode())
        reply = socket.recv(2048).decode("utf8")
        if "\n" not in reply:
            raise Exception(f"Expecting `\\n`, got {reply}")
