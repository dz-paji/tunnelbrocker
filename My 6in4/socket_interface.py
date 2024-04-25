import socket
import struct
import configparser
import logging
import time
import _thread
import traceback

from proto41_handler import Proto41Handler


class SocketInterface:
    __protocols = []
    __config = configparser.ConfigParser()
    __logger = logging.getLogger("Socket Interface")
    __handler = None

    def __init__(self):
        logging.basicConfig(level=logging.NOTSET)

        # create a raw socket
        # This is where we read eth frame for ipv4
        self.socket_pf4_raw = socket.socket(socket.PF_PACKET, socket.SOCK_RAW, socket.htons(0x0800))
        self.socket_pf4_raw.bind(('enp0s3', 0))  # TODO: read from config file
        # This is where we read eth frame for ipv6
        self.socket_pf6_raw = socket.socket(socket.PF_PACKET, socket.SOCK_RAW, socket.htons(0x86DD))
        self.socket_pf6_raw.setsockopt(socket.SOL_SOCKET, socket.SO_BINDTODEVICE, "enp0s8".encode())
        self.socket_pf6_raw.bind(('enp0s8', 0))  # TODO: read from config file
        # This is where we send out ipv4 packets
        self.socket_inet4_raw = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
        self.socket_inet4_raw.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
        self.socket_inet4_raw.bind(('10.0.2.4', 0))  # TODO: read from config file
        # This is where we send out ipv6 packets.
        self.socket_inet6_raw = socket.socket(socket.AF_INET6, socket.SOCK_RAW, socket.IPPROTO_RAW)
        self.socket_inet6_raw.bind(('fd00::a00:27ff:fe5c:2dca', 0))  # TODO: read from config file
        self.socket_inet6_raw.setsockopt(socket.SOL_SOCKET, socket.SO_BINDTODEVICE, "enp0s8".encode())

        # self.add_protocol() deprecated by add_handler()

    def listen_v4(self):
        if self.__handler is None:
            logging.error("No handler added")
            return -1

        while True:
            packet = self.socket_pf4_raw.recvfrom(65535)
            packet = packet[0][14:]
            # raw_header = packet[14:34]
            raw_header = packet[:20]
            header = struct.unpack('!BBHHHBBH4s4s', raw_header)
            hlv = header[0]
            version = hlv >> 4
            protocol = header[6]
            if version == 4:
                if self.__handler.handle_protocol == protocol:
                    print("IPv4 packet with protocol " + str(protocol) + " received from " + socket.inet_ntoa(
                        header[8]) + " at " + time.strftime("%H:%M:%S", time.localtime()))
                    if self.__handler.validate(packet):
                        ipv6_packet, dst_ipv6 = self.__handler.decapsulate(packet)

                        if ipv6_packet is not None:
                            # silently discard the packet
                            self.inject6(ipv6_packet, dst_ipv6)
            # elif version == 6:
            # else:
            #     self.__logger.debug("IPv6 packet received")
            #     packet_6in4, dst_v4 = self.__handler.encapsulate(packet)
            #     if packet_6in4 is not None:
            #         self.inject4(packet_6in4, dst_v4)

    def listen_v6(self):
        if self.__handler is None:
            logging.error("No handler added")
            return -1

        while True:
            packet = self.socket_pf6_raw.recvfrom(65535)
            self.__logger.debug("IPv6 packet received")
            packet = packet[0][14:]
            packet_6in4, dst_v4 = self.__handler.encapsulate(packet)
            if packet_6in4 is not None:
                self.inject4(packet_6in4, dst_v4)

    # def add_protocol(self):
    # ''' deprecated by add_handler()
    # '''
    #     i = 0
    #     self.__config.read('config/app.ini')
    #     if self.__config['6in4']['Enabled'] == "True":
    #             self.__protocols.append(41)
    #             i + 1
    #             self.__logger.debug("proto-41 protocol added")

    #     # for testing purposes
    #     # self.__protocols.append(6)

    #     self.__logger.info("protocols added: %s", self.__protocols)
    #     return i

    def add_handler(self, handler):
        self.__handler = handler
        self.__logger.info("%s handler added", handler.handler_type)

    def inject4(self, packet, dst):
        try:
            self.socket_inet4_raw.sendto(packet, (dst, 0))
        except Exception as e:
            self.__logger.error(e)
            print(traceback.format_exc())
            
        self.__logger.debug("Packet sent to IPv4 network")

    def inject6(self, packet, dst):
        self.socket_inet6_raw.sendto(packet, (dst, 0))
        


if __name__ == '__main__':
    socks = SocketInterface()
    proto41_handler = Proto41Handler()
    socks.add_handler(proto41_handler)
    try:
        _thread.start_new_thread(socks.listen_v4, ())
        _thread.start_new_thread(socks.listen_v6, ())
    except Exception as e:
        print("Error: unable to start thread")

    while True:
        pass
