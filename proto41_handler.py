import struct
import socket
import logging
import ipaddress
import configparser

class Proto41Handler:
    __endpoints = []
    handler_type = "proto41"
    handle_protocol = 41
    __config = configparser.ConfigParser()
    def __init__(self):
        self.__config.read('config/app.ini')
    
    def register(self, ip):
        self.__endpoints.append(ip)
        
    def validate(self, packet):
        header = struct.unpack('!BBHHHBBH4s4s', packet[:20])
        checksum = header[7]
        src = header[8]
        if self.__endpoints.__contains__(src):
            return True
        
        return False
    
    def decapsulate(self, packet):
        header = struct.unpack('!BBHHHBBH4s4s', packet[:20])
        src = header[8]
        dst = header[9]
        
        ipv6_packet = packet[20:]
        ipv6_header = struct.unpack('!IHBB16s16s', ipv6_packet[:40])
        next_header = ipv6_header[3]
        payload_length = ipv6_header[1] #　for reassembling fragmented packets
        src_ipv6 = ipv6_header[4]
        dst_ipv6 = ipv6_header[5]
            
        # discard the packet if the source address is invalid
        invalid_addresses = ["FF00::/8", "::1", "::FFFF:0:0/96"]
        rfc3513_addresses = "::/96"
        for address in invalid_addresses:
            if ipaddress.ip_address(src_ipv6).subnet_of(ipaddress.ip_network(address)):
                logging.error("Discard the packet as it has an invalid source address")
                return None        
        
        if ipaddress.ip_address(src_ipv6).subnet_of(ipaddress.ip_network(rfc3513_addresses)):
            if not ipaddress.ip_address(src_ipv6).subnet_of(ipaddress.ip_network("::/128")):
                logging.error("Discard the packet as its src address is a RFC3513 address")
                
        # handles next header

        
        ipv6_header[4] = self.__config['Interface']['IPv6_Address']
        
        # need to use a soft state table to keeping track of the packets
        
            
        # recalculating length as IPv4 header might be padded
        new_payload_length = len(ipv6_packet) + 40 
        ipv6_header[1] = new_payload_length
        ipv6_header_raw = struct.pack('!IHBB16s16s', ipv6_header[0], ipv6_header[1], ipv6_header[2], ipv6_header[3], ipv6_header[4], ipv6_header[5])
        
        packet = ipv6_header_raw + ipv6_packet
        return packet
        
if __name__ == '__main__':
    print(128 * '1')
