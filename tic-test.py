import socket

if __name__ == "__main__":
    socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket.connect(("localhost", 3874))
    socket.send(b"Hello World!")