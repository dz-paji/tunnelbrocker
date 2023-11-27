import socket
import configparser

class TicServer():
    '''
    Mock class for TicServer
    '''
    
    configparser = configparser.ConfigParser()
    configparser.read('config/app.ini')
    
    def __init__(self):
        # a socket listen for tcp bind to 3874
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((configparser.get("Server_Address"), 3874))
        