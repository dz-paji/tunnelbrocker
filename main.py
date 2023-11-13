import socket_interface
import proto41_handler
import socket
import struct

if __name__ == '__main__':
    socks = socket_interface.SocketInterface()
    proto41_handler = proto41_handler.Proto41Handler()
    socks.add_handler(proto41_handler)
    
    # proto41_handler.register("10.10.0.1")
    # payload = b"test"
    # # contrust ipv6 header
    # vrl_v6 = 6 << 28
    # traffic_class = 0 << 20
    # flow_label = 0
    # payload_length_v6 = len(payload)
    # next_header = 0
    # hop_limit = 64
    # src_ipv6 = socket.inet_pton(socket.AF_INET6, "fe00::1")
    # dst_ipv6 = socket.inet_pton(socket.AF_INET6, "fc00::1")
    # ipv6_header = struct.pack('!IHBB16s16s', vrl_v6 | traffic_class | flow_label, payload_length_v6, next_header, hop_limit, src_ipv6, dst_ipv6)
    # ipv6_packet = ipv6_header + payload
    # test_6in4_packet = proto41_handler.encapsulate(ipv6_packet)
    # dst_ipv4 = socket.inet_aton("10.0.2.2")
    # socks.inject(test_6in4_packet, dst_ipv4)
    payload = b'test'
    id = 0
    flags = 0
    fragment_offset = 0
    ttl = 64

    src_ip_v4 = socket.inet_aton("10.0.2.15")
    dst_ip_v4 = socket.inet_aton("10.0.2.2")
    total_length_v4 = 5 * 4 + len(payload)

    ipv4_header = struct.pack('!BBHHHBBH4s4s', (4 << 4) + 5, 0, total_length_v4, id, flags << 13 + fragment_offset, ttl, 41, 0, src_ip_v4, dst_ip_v4)

    packet = ipv4_header + payload
    socks.inject(packet)