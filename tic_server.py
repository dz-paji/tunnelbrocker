import socket
import configparser
import time
import threading
import logging

class TicServer():
    '''Tunnel and Information server.
    '''
    
    def __init__(self):
        self.__configparser = configparser.ConfigParser()
        self.__configparser.read('config/tic.ini')
        self.__clientStates = {} # {addr: state(joined, clear|md5, authed)}
        
        # logging
        self.logger = logging.getLogger("TIC")
        self.logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
        handler.setLevel(logging.INFO)
        self.logger.addHandler(handler)
    
        # bind port 3874 for TIC.
        self.__server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        if (self.__configparser.has_option("Address", "Server_Address")):
            self.__server_socket.bind((self.__configparser.get("Address", "Server_Address"), 3874))
        else:
            #　bind to localhost by default.
            self.__server_socket.bind("localhost", 3874)
            
    def run(self):
        self.__server_socket.listen()
        
        self.logger.info("TIC server started.")
        while True:
            conn, addr = self.__server_socket.accept()
            
            self.logger.info("Connected from %s" % addr)
            threading.Thread(target=self.threadHandler, args=(conn, addr)).start()
            
            
    def threadHandler(self, conn: socket.socket, addr: str):
        '''Handle the connection in a new thread.
        '''
        # set timeout
        conn.settimeout(10)
        username = "" # for authentication
        
        try:
            # Send welcome message. What really useful is the first char.
            # remeber to add \n at the end of the message...
            welcome_msg = "200 TIC on %s ready (%s) \n" % (self.__configparser.get("Address", "Server_Name"), self.__configparser.get("Contact", "Website"))
            conn.send(welcome_msg.encode("utf-8"))
            
            data = conn.recv(1024)
            # here the client will sendback its version and runtime. could be useful for statistics.
            
            conn.send(b"200 OK\n")
            self.__clientStates.update({addr: "joined"})
            
            data = conn.recv(1024) # here the client should request timestamp.
            if data == b"get unixtime\n":
                timestamp = self.getTimestamp() + "\n"
                conn.send(timestamp.encode("utf-8"))
            else:
                conn.send(b"400 Bad Request\n")
                conn.close()
                return
            
            while True:
                data = conn.recv(1024)
                self.logger.debug("TLS status: " + type(self.__configparser.get("TLS", "Enable")))
                if self.__configparser.get("TLS", "Enable") and data.startswith(b"starttls"):
                    # TODO: Make it compatible with GnuTLS
                    pass
                else:
                    pass

                if data.startswith(b"get unixtime"):
                    timestamp = self.getTimestamp() + "\n"
                    conn.send(timestamp.encode("utf-8"))
                elif data.startswith(b"username"):
                    username = data.split(b" ")[1].decode("utf-8")
                    conn.send(b"200 OK\n")
                elif data.startswith(b"challenge"):
                    # should support clear, cookie and md5.
                    challenge_method = data.split(b" ")[1].decode("utf-8")
                    match challenge_method:
                        case "clear":
                            conn.send(b"200 OK\n")
                            self.__clientStates.update({addr: "clear"})
                            break
                        case "cookie":
                            conn.send(b"200 OK\n")
                            self.__clientStates.update({addr: "cookie"})
                            break
                        case "md5":
                            conn.send(b"200 OK\n")
                            self.__clientStates.update({addr: "md5"})
                            break
                        case _:
                            conn.send(b"400 Bad Request\n")
                elif data.startswith("authenticate"):
                    if username == "":
                        conn.send(b"400 Please identify yourself\n")
                        continue
                    elif self.__clientStates[addr] == "joined":
                        conn.send(b"400 Please challenge first\n")
                        continue
                    else:
                        passwd = data.split(b" ")[2].decode("utf-8")
                        auth_flag = 
                
        except socket.timeout:
            self.logger.error("Connection timeout.")
            conn.close()
            return
    
    def getTimestamp(self) -> str:
        '''Get current timestamp
        '''
        return str(time.time())
    
    def authMe(self) -> bool:
        '''Authenticate the client.
        '''
        pass

if __name__ == "__main__":
    tic_server = TicServer()
    tic_server.run()

        