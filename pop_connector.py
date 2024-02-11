import socket
import logging
import shared.PopOperationException as PopOperationException
from sql_connector import TunnelEntity

class PopConnector():
    def __init__(self, host):
        if "." in host:
            # This is an IPv4 host
            self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            # This is an IPv6 host
            self.conn = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        self.host = host
        
        logging.basicConfig(level=logging.DEBUG)
        self.logger = logging.getLogger("PopConnector")
        
    def connect(self):
        self.conn.connect((self.host, 42003))
        welcome = self.conn.recv(1024).decode("utf-8")
        self.logger.debug(welcome)
        
    def disconnect(self):
        self.conn.close()
        
    def addTunnel(self, tunnel: TunnelEntity) -> TunnelEntity:
        """Add a tunnel to the POP.
        <tid> <tunnel-id> <tunnel_them|ayiya|heartbeat> <up|disabled> <mtu> [<password>]
        """
        self.connect()
        self.logger.debug("~# tunnel")
        self.conn.send("tunnel \n".encode("utf-8"))
        resp = self.conn.recv(1024).decode("utf-8")
        self.logger.debug(resp)
        self.logger.debug("~/tunnel# set")
        self.conn.send("set \n".encode("utf-8"))
        resp = self.conn.recv(1024).decode("utf-8")
        self.logger.debug(resp)

        if tunnel.type == "ayiya" or tunnel.type == "heartbeat":
            configString = f"config {tunnel.id} {tunnel.tid} {tunnel.type} UP {tunnel.mtu} {tunnel.password} \n"
            self.conn.send(configString.encode("utf-8"))
        else:
            # Should set the client's endpoint as the 3rd argument.
            configString = f"config {tunnel.id} {tunnel.tid} {tunnel.type} UP {tunnel.mtu} \n"
            self.conn.send(configString.encode("utf-8"))
            
        # Check the result.
        resp = self.conn.recv(1024)
        resp = resp.decode("utf-8")
        self.logger.debug(resp)

        if resp[0] == "2":
            # Success. Fetch endpoint info.
            self.conn.send(".. \n".encode("utf-8"))
            resp = self.conn.recv(1024).decode("utf-8")
            self.conn.send(f"show {tunnel.tid}\n".encode("utf-8"))
            resp = self.conn.recv(1024).decode("utf-8")
            records = resp.split("\n")
            for i in records:
                # fill-out the fields. need check with sixxsd output.
                if i.startswith("Outer Them"):
                    tunnel.endpoint_v4 = i.split(":")[1].strip()
                elif i.startswith("Inner Them"):
                    ipv6 = i.split(":")[1:]
                    ipv6 = ":".join(ipv6)
                    tunnel.endpoint_v6 = ipv6.strip()
            
            self.disconnect()
            return tunnel
                    
        else:
            # Fail. Raise exception.
            self.disconnect()
            raise PopOperationException(resp)
        
    def setRemote(self, tid: str, remote: str) -> bool:
        """Set the remote endpoint of a tunnel. More useful for 6in4.
        """
        self.connect()
        self.conn.send("tunnel \n".encode("utf-8"))
        self.conn.recv(1024)
        self.conn.send("set \n".encode("utf-8"))
        self.conn.recv(1024)
        configString = f"remote {tid} {remote} \n"
        self.conn.send(configString.encode("utf-8"))
        resp = self.conn.recv(1024)
        resp = resp.decode("utf-8").strip()
        if resp[0] == 2:
            # Success. 
            self.disconnect()
            return True
        else:
            # Fail. Raise exception.
            raise PopOperationException(resp)
        