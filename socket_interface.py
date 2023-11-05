import socket
import struct
import configparser
import logging
import time

class SocketInterface:
    __protocols = []
    __config = configparser.ConfigParser()
    __logger = logging.getLogger("sniffer")
    
    def __init__(self):
        logging.basicConfig(level=logging.NOTSET)

        # create a raw socket
        self.raw_socket = socket.socket(socket.PF_PACKET, socket.SOCK_RAW, socket.htons(0x0800))
        # self.raw_socket.bind(('enp0s3', 0))
        self.add_protocol()

    def listen(self):
        while True:
            packet = self.raw_socket.recvfrom(65535)
            raw_header = packet[0][14:34]
            header = struct.unpack('!BBHHHBBH4s4s', raw_header)
            hlv = header[0]
            version = hlv >> 4
            protocol = header[6]
            if version == 4:
                if self.__protocols.__contains__(protocol):
                    print("IPv4 packet with protocol " + str(protocol) + " received from " + socket.inet_ntoa(header[9]) + " at " + time.strftime("%H:%M:%S", time.localtime()))
                
    def add_protocol(self):
        i = 0
        self.__config.read('config/app.ini')
        if self.__config['6in4']['Enabled'] == "True":
                self.__protocols.append(41)
                i + 1
                self.__logger.debug("proto-41 protocol added")
                
        # for testing purposes
        # self.__protocols.append(6)
        
        self.__logger.info("protocols added: %s", self.__protocols)
        return i
        
    def inject(self, packet):        
        self.raw_socket.send(packet)
                


if __name__ == '__main__':
    sniffer = PacketSniffer()
    sniffer.listen()