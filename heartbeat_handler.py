import socket
import logging
import struct
import configparser
import time
import hashlib
import threading

from packet_filter import PacketFilter

class HeartbeatHandler:
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    __logger = logging.getLogger("HeartbeatHandler")
    
    config_parser = configparser.ConfigParser()
    config_parser.read('config/app.ini')
    
    heartbeat_info = {}
    heartbeat_info_lock = threading.Lock()
    # {IPv6: (Flag, Timestamp)}
    
    heartbeat_interval = config_parser.get('HeartBeat', 'Interval') # in seconds
    
    def __init__(self, packet_filter: PacketFilter) -> None:
        self.ipv4 = self.config_parser.get('Interface', 'IPv4_Address')
        self.server_socket.bind((self.ipv4, 3740))
        self.packet_filter = packet_filter

    def listen(self):
        while True:
            packet = self.server_socket.recvfrom(1024)
            self.onRecev(packet)
            
    def tick(self):
        '''
        Do I need to consider concurrency here?
        '''
        while True:
            for i in self.heartbeat_info:
                if self.heartbeat_info[i][0] == False and time.time() - self.heartbeat_info[i][1] > 120:
                    self.__logger.info(f"Tunnel {i} is offline.")
                    self.heartbeat_info.update({i: (False, time.time())})
            
            time.sleep(30)
        
    def onRecev(self, packet):
        '''
        When receiving a heartbeat packet. 
        '''
        
        # if not packet.startswith('HEARTBEAT TUNNEL'):
        #     raise MalformedMsgException("Unexpected message format: " + packet)

        try:
            unpacked_packet = struct.unpack('!9s6s16scq32s', packet) # heartbeat.c line 227
        except Exception as e:
            self.__logger.error(f"Error when unpack heartbeat msg: {e}")
            return
        
        client_ipv6 = unpacked_packet[2]
        client_ipv4 = unpacked_packet[3]
        client_timestamp = unpacked_packet[4]
        client_md5 = unpacked_packet[5]
        
        if unpacked_packet[0] != 'HEARTBEAT' or unpacked_packet[1] != 'TUNNEL':
            self.__logger.error(f"Unexpected message format: {packet}")
        
        try:
            self.packet_filter.lookup_endpoint(client_ipv6)
        except Exception as e:
            self.__logger.error(f"Error when finding endpoint: {e}")
            return
                
        if time.time() - client_timestamp > 60:
            self.__logger.info("Received heartbeat from " + client_ipv6 + " but it's too old")
            return
        
        if self.verify_md5(client_ipv6, packet):
            self.__logger.info("Received heartbeat from " + client_ipv6)
            
        #update endpoint with heartbeat information
        self.packet_filter.endpoint_update(client_ipv6, client_ipv4)
        
    def verify_md5(self, client_ipv6, packet):
        '''
        TODO: Complete this function with TIC.
        '''
        
        return True
    
        
class MalformedMsgException(Exception):
    pass

if __name__ == '__main__':
    a = {'a': 1, 'b': 2}
    for i in a:
        print(i)