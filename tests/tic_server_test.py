import unittest
import socket
from tic_server import TicServer

class TestTICMethods(unittest.TestCase):
    def setUp(self) -> None:
        self.tic = TicServer()
        self.tic.run()
        
        self.client_socks = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socks.connect(("localhost", 3874))

if __name__ == '__main__':
    unittest.main()