import struct
import socket
import logging
import configparser

from shared import ipv6_tools
from packet_filter import PacketFilter

class Proto41Handler:
    __endpoints_v4 = [] # check if the source address is valid
    handler_type = "proto41"
    handle_protocol = 41
    __config = configparser.ConfigParser()
    packet_filter = PacketFilter()
    logger = logging.getLogger("proto41_handler")
    
    # depracated. use packet_filter.lookup_endpoint().
    # prefix and mask of client's ipv6, endpoint as clients ipv4
    # tunnel_map = {('prefix', 'mask'): 'endpoint'} 
    
    def __init__(self):
        self.__config.read('config/app.ini')
        logging.basicConfig(level=logging.NOTSET)
    
    def register(self, ip):
        '''
        Register the given ip address as authenticated endpoint
        '''
        self.__endpoints_v4.append(ip)
        
    def validate_endpoint(self, src_v4):        
        if self.__endpoints_v4.__contains__(src_v4):
            return True
        
        return False
    
    def decapsulate(self, packet):
        header_v4 = struct.unpack('!BBHHHBBH4s4s', packet[:20])
        src_v4 = header_v4[8]
        dst_v4 = header_v4[9]
        
        ipv6_packet = packet[20:]
        ipv6_header = struct.unpack('!IHBB16s16s', ipv6_packet[:40])
        payload_length_v6 = ipv6_header[1] #　for reassembling fragmented packets
        src_ipv6 = ipv6_header[4]
        dst_ipv6 = ipv6_header[5]
        
        if self.__endpoints_v4.__contains__(src_v4) == False:
            return None
        
        try:
            self.validate_endpoint(src_v4) # check if the endpoint is registered
        except Exception as e:
            self.logger.error(e)
            return None
        
        # TODO: handles next header
                
        # need to use a soft state table to keeping track of the packets
        # client_prefix_v6, client_netmask_v6 = ipv6_tools.calculate_subnet(src_ipv6)
        # self.tunnel_map.update({(client_prefix_v6, client_netmask_v6): src_v4})
            
        # recalculating length as IPv4 header might be padded
        new_payload_length_v6 = len(ipv6_packet) + 40 
        ipv6_header[1] = new_payload_length_v6
        ipv6_header_raw = struct.pack('!IHBB16s16s', ipv6_header[0], ipv6_header[1], ipv6_header[2], ipv6_header[3], ipv6_header[4], ipv6_header[5])
        
        new_packet = ipv6_header_raw + ipv6_packet
        return new_packet
    
    def encapsulate(self, packet):
        ipv6_header = struct.unpack('!IHBB16s16s', packet[:40])
        src_ipv6 = ipv6_header[4]
        dst_ipv6 = ipv6_header[5]
        
        try:
            endpoint_v4 = self.packet_filter.lookup_endpoint(dst_ipv6)
        except Exception as e:
            self.logger.error(e)
            return None
        
        # TODO: fragmentation
        id = 0
        flags = 0
        fragment_offset = 0
        ttl = 64

        src_ip_v4 = self.__config.get('Interface', 'IPv4_Address')
        dst_ip_v4 = endpoint_v4
        total_length_v4 = 5 * 4 + len(packet)
        src_ip_v4 = socket.inet_aton(src_ip_v4)
        dst_ip_v4 = socket.inet_aton(dst_ip_v4)

        ipv4_header = struct.pack('!BBHHHBBH4s4s', (4 << 4) + 5, 0, total_length_v4, id, flags << 13 + fragment_offset, ttl, 41, 0, src_ip_v4, dst_ip_v4)

        return ipv4_header + packet
        
if __name__ == '__main__':
    try:
        print(128 ** 2)
        a = 1
    except:
        print("error")
        
    print(a)