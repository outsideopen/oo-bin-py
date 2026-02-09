from . import Client


class Smtp(Client):
    """Handles the SMTP STARTTLS connection with the server"""

    def starttls(self, socket):
        """SMTP STARTTLS"""
        # connected
        reply = socket.recv(2048).decode("utf8")
        if "\n" not in reply:
            raise Exception(f"expecting newline, got {reply}")

        # speak
        hostname = "mail.example.com"
        socket.sendall(f"EHLO {hostname}\n".encode())
        reply = socket.recv(2048).decode("utf8")
        if "STARTTLS" not in reply:
            raise Exception("Expecting STARTTLS server capability")

        socket.sendall("STARTTLS\n".encode())
        reply = socket.recv(2048).decode("utf8")
        if "\n" not in reply:
            raise Exception(f"Expecting `\\n`, got {reply}")
