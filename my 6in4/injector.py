import socket
import struct

s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)

# create IP header
version = 4
hl = 5
tos = 0
id = 11451
flags = 0
fragment_offset = 0
ttl = 64
protocol = 41
src_ip = '127.0.0.1'
dst_ip = '127.0.0.1'
payload = b'testing'
total_length = hl * 4 + len(payload)
src_ip = socket.inet_aton(src_ip)
dst_ip_b = socket.inet_aton(dst_ip)

ip_header = struct.pack('!BBHHHBBH4s4s', (version << 4) + hl, tos, total_length, id, flags << 13 + fragment_offset, ttl, protocol, 0, src_ip, dst_ip_b)

# send packet
s.sendto(ip_header + payload, (dst_ip, 0))
