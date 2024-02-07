import socket
import configparser
import time
import threading
import logging
from sql_connector import SQLConnector, UserEntity
import hashlib

class TicServer():
    '''Tunnel and Information server.
    '''
    
    def __init__(self):
        self.__configparser = configparser.ConfigParser()
        self.__configparser.read('config/tic.ini')
        self.__clientStates = {} # {addr: state(joined, clear|md5, UserEntity)}
        
        # logging
        logging.basicConfig(level=logging.DEBUG)
        self.logger = logging.getLogger("TIC")
        handler = logging.StreamHandler()
        # handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
        # handler.setLevel(logging.INFO)
        # debug_handler = logging.StreamHandler()
        # debug_handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
        # debug_handler.setLevel(logging.DEBUG)
        # self.logger.addHandler(debug_handler)
        # self.logger.addHandler(handler)
    
        # bind port 3874 for TIC.
        self.__server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        if (self.__configparser.has_option("Address", "Server_Address")):
            self.__server_socket.bind((self.__configparser.get("Address", "Server_Address"), 3874))
        else:
            #　bind to localhost by default.
            self.__server_socket.bind("localhost", 3874)
            
        # connect to database
        try:
            self.__sql_connector = SQLConnector()
        except Exception as e:
            self.logger.error("Failed to connect to database.")
            self.logger.error(e)
            exit(0)
            
    def run(self):
        self.__server_socket.listen()
        
        self.logger.info("TIC server started.")
        while True:
            conn, addr = self.__server_socket.accept()
            
            self.logger.info("Connected from %s" % str(addr))
            threading.Thread(target=self.threadHandler, args=(conn, addr)).start()
            
            
    def threadHandler(self, conn: socket.socket, addr: str):
        '''Handle the connection in a new thread.
        '''
        # set timeout
        # conn.settimeout()
        username = "" # for authentication
        
        try:
            # Send welcome message. What really useful is the first char.
            # remeber to add \n at the end of the message...
            welcome_msg = "200 TIC on %s ready (%s) \n" % (self.__configparser.get("Address", "Server_Name"), self.__configparser.get("Contact", "Website"))
            conn.send(welcome_msg.encode("utf-8"))
            
            data = conn.recv(1024)
            # here the client will sendback its version and runtime. could be useful for statistics.
            self.logger.info("%s client version: %s" % (str(addr), data.decode("utf-8")))
            
            conn.send(b"200 OK\n")
            self.__clientStates.update({addr: "joined"})
            
            data = conn.recv(1024) 
            # here the client should request timestamp.
            if data == b"get unixtime\n":
                self.logger.info("Client %s requested timestamp." % str(addr))
                result = "200 " + self.getTimestamp() + "\n"
                conn.send(result.encode("utf-8"))
            else:
                conn.send(b"400 Bad Request\n")
                conn.close()
                return
            
            while True:
                data = conn.recv(1024)
                data = data.strip()
                self.logger.debug("Received: " + data.decode("utf-8"))
                self.logger.debug("TLS status: " + (self.__configparser.get("TLS", "Enable")))
                if self.__configparser.getboolean("TLS", "Enable") and data.startswith(b"starttls"):
                    # TODO: Make it's compatible with GnuTLS
                    pass
                else:
                    pass

                if data.startswith(b"get unixtime"):
                    # get timestamp
                    self.logger.info("Client %s requested timestamp." % str(addr))
                    timestamp = self.getTimestamp() + "\n"
                    conn.send(timestamp.encode("utf-8"))
                elif data.startswith(b"username"):
                    # here the client sends its username. check against the database.
                    username = data.split(b" ")[1].decode("utf-8")
                    username = username.strip()
                    self.logger.debug("Client on %s identified itself as %s" % (str(addr), username))
                    dbUser = self.__sql_connector.getUser(username)
                    self.logger.debug("User %s found in database." % dbUser)
                    
                    if dbUser == None:
                        conn.send(b"400 No such user\n")
                        conn.close()
                        return
                    else:
                        self.logger.info("We now have client %s on %s" % (username, str(addr)))
                        conn.send(b"200 OK\n")
                elif data.startswith(b"challenge"):
                    # should support clear, cookie and md5. However not sure how cookie and clear works.
                    challenge_method = data.split(b" ")[1].decode("utf-8")
                    challenge_method = challenge_method.strip()
                    self.logger.info("Client %s on %s suggested challenge: %s" % (username, str(addr), challenge_method))
                    
                    # check challenge method
                    match challenge_method:
                        case "clear":
                            conn.send(b"400 Not supported\n")
                            conn.close()
                            return
                        case "cookie":
                            conn.send(b"400 Not supported\n")
                            conn.close()
                            return
                        case "md5":
                            # This should be random
                            challenge = "60d11a81a26df3738026b1839644a1ae"
                            challeng_resp = "200 " + challenge + "\n"
                            conn.send(challeng_resp.encode("utf-8"))
                            self.__clientStates.update({addr: ("md5", challenge)})
                        case _:
                            conn.send(b"400 Bad Request\n")
                            conn.close()           
                elif data.startswith(b"authenticate"):
                    # client sends authentication string
                    self.logger.info("Client %s on %s wants authenticate." % (username, str(addr)))
                    # make sure the user identified itself and the challenge method.
                    if username == "":
                        conn.send(b"400 Please identify yourself\n")
                        continue
                    elif self.__clientStates[addr] == "joined":
                        conn.send(b"400 Please challenge first\n")
                        continue
                    else:
                        passwd = data.split(b" ")[2].decode("utf-8")
                        passwd = passwd.strip()
                        auth_flag = self.authMe(username, passwd, addr)
                        if auth_flag:
                            self.logger.info("Client %s on %s authenticated." % (username, str(addr)))
                            conn.send(b"200 OK\n")

                            # bind address with user
                            this_user = self.__sql_connector.getUser(username)
                            self.__clientStates.update({addr: this_user})
                        else:
                            self.logger.info("Login failed for client %s on %s." % (username, str(addr)))
                            conn.send(b"400 Failed\n")
                            conn.close()
                            return
                elif data.startswith(b"tunnel list"):
                    self.logger.info("Client %s requested tunnel list." % (username, ))
                    thisUser = self.__clientStates[addr]
                    
                    # check login
                    if type(thisUser) != UserEntity:
                        conn.send(b"400 Please authenticate first\n")
                        conn.close()
                        return
                    
                    # 201 /n
                    # tunnel_id, ipv6, ipv4, popid /n
                    # 202 /n
                    resp_msg = "201\n"
                    for i in self.__sql_connector.listTunnels(thisUser.uid):
                        resp_msg += "%s %s %s %s\n" % (i.tid, i.endpoint_v6, i.endpoint_v4, i.pop_id)
                    resp_msg += "202\n"
                    conn.send(resp_msg.encode("utf-8"))
                elif data.startswith(b"tunnel show"):
                    t_id = data.strip().split(b" ")[2].decode("utf-8")
                    self.logger.info("Client %s requested tunnel info %s." % (username, t_id))
                    i = self.__sql_connector.getTunnel(t_id)
                    resp_msg = "201\n"
                    
                    # TunnelID, Type, v6 endpoint, v6 pop, v6 prefix length, pop id, v4 endpoint, v4 pop, user state, admin state, heartbeat interval, mtu
                    # TODO: Figure out what to do with userstate and admin state
                    resp_msg += "%s %s %s %s %d %s %s %s %s %s %d %d\n" % (i.tid, i.type, i.endpoint_v6, i.v6_pop, i.endpoint_v6_prefix, i.pop_id, i.endpoint_v4, i.v4_pop, i.user.state, i.admin.state, i.heartbeat_interval, i.mtu)
                    resp_msg += "202\n"
                    conn.send(resp_msg.encode("utf-8"))
                
        except socket.timeout:
            self.logger.error("Connection timeout.")
            conn.close()
            return
        
        except ConnectionResetError:
            self.logger.error("Connection reset by peer.")
            conn.close()
            return
    
    def getTimestamp(self) -> str:
        '''Get current timestamp
        '''
        time_now_is = time.time()
        time_now_is = int(time_now_is)
        self.logger.debug("Timestamp: %d" % time_now_is)
        return str(time_now_is)
    
    def authMe(self, username: str, password: str, addr) -> bool:
        '''Authenticate the client.
        '''
        self.logger.debug("Authenticating %s, password: %s" % (username, password))
        user = self.__sql_connector.getUser(username)
        if user == None:
            return False
        else:
            # Get the challenge and method
            (method, challenge) = self.__clientStates[addr]
            self.logger.debug("Challenge method: %s, challenge: %s" % (method, challenge))
            match method:
                case "md5":
                    passwd_hasher = hashlib.md5()
                    passwd_hasher.update(user.password.encode("utf-8"))
                    passwd_md5 = passwd_hasher.hexdigest()
                    
                    # some wired person thought it's funny to use OOP for md5. And you can't reuse it.
                    signature = challenge + passwd_md5
                    signature_hasher = hashlib.md5()
                    signature_hasher.update(signature.encode("utf-8"))
                    signature_hash = signature_hasher.hexdigest()
                    self.logger.info("Client returned: %s" % signature_hash)
                    
                    return signature_hash == password

if __name__ == "__main__":
    tic_server = TicServer()
    tic_server.run()
