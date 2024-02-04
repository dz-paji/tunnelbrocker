import socket
import configparser
import hashlib

import struct

class MD5Context:
    def __init__(self):
        self.buf = [0x67452301, 0xefcdab89, 0x98badcfe, 0x10325476]
        self.bits = [0, 0]
        self.inp = bytearray(64)

    def update(self, input_bytes):
        input_length = len(input_bytes)
        index = (self.bits[0] >> 3) & 0x3F
        self.bits[0] += input_length << 3
        if self.bits[0] < (input_length << 3):
            self.bits[1] += 1
        self.bits[1] += input_length >> 29

        part_len = 64 - index
        if input_length >= part_len:
            self.inp[index:] = input_bytes[:part_len]
            self.transform(self.inp)
            i = part_len
            while i + 63 < input_length:
                self.transform(input_bytes[i:i+64])
                i += 64
            else:
                index = 0
        else:
            i = 0
        self.inp[index:index + input_length - i] = input_bytes[i:input_length]

    def final(self):
        count = (self.bits[0] >> 3) & 0x3f
        if count < 56:
            pad_len = 56 - count
        else:
            pad_len = 120 - count
        padding = bytes([0x80]) + bytes(pad_len - 1)
        self.update(padding)
        self.update(struct.pack("<2Q", self.bits[0], self.bits[1]))
        result = struct.pack("<4I", *self.buf)
        return result

    def transform(self, block):
        a, b, c, d = self.buf
        x = [struct.unpack('<I', block[i:i + 4])[0] for i in range(0, 64, 4)]

        # Define the auxiliary functions
        def F(x, y, z): return x & y | ~x & z
        def G(x, y, z): return x & z | y & ~z
        def H(x, y, z): return x ^ y ^ z
        def I(x, y, z): return y ^ (x | ~z)

        # Define the transformation function
        def rotate_left(x, n): return (x << n) | (x >> (32 - n))
        def FF(a, b, c, d, x, s, ac): return rotate_left(a + F(b, c, d) + x + ac, s) + b
        def GG(a, b, c, d, x, s, ac): return rotate_left(a + G(b, c, d) + x + ac, s) + b
        def HH(a, b, c, d, x, s, ac): return rotate_left(a + H(b, c, d) + x + ac, s) + b
        def II(a, b, c, d, x, s, ac): return rotate_left(a + I(b, c, d) + x + ac, s) + b

        # Apply rounds
        a = FF(a, b, c, d, x[ 0],  7, 0xd76aa478); d = FF(d, a, b, c, x[ 1], 12, 0xe8c7b756)
        c = FF(c, d, a, b, x[ 2], 17, 0x242070db); b = FF(b, c, d, a, x[ 3], 22, 0xc1bdceee)
        a = FF(a, b, c, d, x[ 4],  7, 0xf57c0faf); d = FF(d, a, b, c, x[ 5], 12, 0x4787c62a)
        c = FF(c, d, a, b, x[ 6], 17, 0xa8304613); b = FF(b, c, d, a, x[ 7], 22, 0xfd469501)
        a = FF(a, b, c, d, x[ 8],  7, 0x698098d8); d = FF(d, a, b, c, x[ 9], 12, 0x8b44f7af)
        c = FF(c, d, a, b, x[10], 17, 0xffff5bb1); b = FF(b, c, d, a, x[11], 22, 0x895cd7be)
        a = FF(a, b, c, d, x[12],  7, 0x6b901122); d = FF(d, a, b, c, x[13], 12, 0xfd987193)
        c = FF(c, d, a, b, x[14], 17, 0xa679438e); b = FF(b, c, d, a, x[15], 22, 0x49b40821)

        a = GG(a, b, c, d, x[ 1],  5, 0xf61e2562); d = GG(d, a, b, c, x[ 6],  9, 0xc040b340)
        c = GG(c, d, a, b, x[11], 14, 0x265e5a51); b = GG(b, c, d, a, x[ 0], 20, 0xe9b6c7aa)
        a = GG(a, b, c, d, x[ 5],  5, 0xd62f105d); d = GG(d, a, b, c, x[10],  9, 0x02441453)
        c = GG(c, d, a, b, x[15], 14, 0xd8a1e681); b = GG(b, c, d, a, x[ 4], 20, 0xe7d3fbc8)
        a = GG(a, b, c, d, x[ 9],  5, 0x21e1cde6); d = GG(d, a, b, c, x[14],  9, 0xc33707d6)
        c = GG(c, d, a, b, x[ 3], 14, 0xf4d50d87); b = GG(b, c, d, a, x[ 8], 20, 0x455a14ed)
        a = GG(a, b, c, d, x[13],  5, 0xa9e3e905); d = GG(d, a, b, c, x[ 2],  9, 0xfcefa3f8)
        c = GG(c, d, a, b, x[ 7], 14, 0x676f02d9); b = GG(b, c, d, a, x[12], 20, 0x8d2a4c8a)

        a = HH(a, b, c, d, x[ 5],  4, 0xfffa3942); d = HH(d, a, b, c, x[ 8], 11, 0x8771f681)
        c = HH(c, d, a, b, x[11], 16, 0x6d9d6122); b = HH(b, c, d, a, x[14], 23, 0xfde5380c)
        a = HH(a, b, c, d, x[ 1],  4, 0xa4beea44); d = HH(d, a, b, c, x[ 4], 11, 0x4bdecfa9)
        c = HH(c, d, a, b, x[ 7], 16, 0xf6bb4b60); b = HH(b, c, d, a, x[10], 23, 0xbebfbc70)
        a = HH(a, b, c, d, x[13],  4, 0x289b7ec6); d = HH(d, a, b, c, x[ 0], 11, 0xeaa127fa)
        c = HH(c, d, a, b, x[ 3], 16, 0xd4ef3085); b = HH(b, c, d, a, x[ 6], 23, 0x04881d05)
        a = HH(a, b, c, d, x[ 9],  4, 0xd9d4d039); d = HH(d, a, b, c, x[12], 11, 0xe6db99e5)
        c = HH(c, d, a, b, x[15], 16, 0x1fa27cf8); b = HH(b, c, d, a, x[ 2], 23, 0xc4ac5665)

        a = II(a, b, c, d, x[ 0],  6, 0xf4292244); d = II(d, a, b, c, x[ 7], 10, 0x432aff97)
        c = II(c, d, a, b, x[14], 15, 0xab9423a7); b = II(b, c, d, a, x[ 5], 21, 0xfc93a039)
        a = II(a, b, c, d, x[12],  6, 0x655b59c3); d = II(d, a, b, c, x[ 3], 10, 0x8f0ccc92)
        c = II(c, d, a, b, x[10], 15, 0xffeff47d); b = II(b, c, d, a, x[ 1], 21, 0x85845dd1)
        a = II(a, b, c, d, x[ 8],  6, 0x6fa87e4f); d = II(d, a, b, c, x[15], 10, 0xfe2ce6e0)
        c = II(c, d, a, b, x[ 6], 15, 0xa3014314); b = II(b, c, d, a, x[13], 21, 0x4e0811a1)
        a = II(a, b, c, d, x[ 4],  6, 0xf7537e82); d = II(d, a, b, c, x[11], 10, 0xbd3af235)
        c = II(c, d, a, b, x[ 2], 15, 0x2ad7d2bb); b = II(b, c, d, a, x[ 9], 21, 0xeb86d391)

        self.buf[0] = (self.buf[0] + a) & 0xFFFFFFFF
        self.buf[1] = (self.buf[1] + b) & 0xFFFFFFFF
        self.buf[2] = (self.buf[2] + c) & 0xFFFFFFFF
        self.buf[3] = (self.buf[3] + d) & 0xFFFFFFFF



def sockethello():
    socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket.connect(("localhost", 3874))
    socket.send(b"Hello World!")

def config():
    configger = configparser.ConfigParser()
    configger.read('config/tic.ini')
    field = configger.get("TLS", "Enable")
    print(field + "->" + str(type(field)))
    
def switchCase():
    a = 1
    match 1:
        case 1:
            print("1")
        case 2:
            print("2")
        case _:
            print("default")
    
    print("b")
    
def testMD5():
    '''
    Client returned: 50de2f3d81e19ad17473f59e0db54b9d
    password: admin
    challenge: 60d11a81a26df3738026b1839644a1ae
    '''
    hash = hashlib.md5()
    hash.update("admin".encode("utf-8"))
    passwd_md5 = hash.hexdigest()
    print(passwd_md5)
    signature = "60d11a81a26df3738026b1839644a1ae" + passwd_md5
    newsig = "60d11a81a26df3738026b1839644a1ae21232f297a57a5a743894a0e4a801fc3"
    anotherHash = hashlib.md5()
    anotherHash.update(newsig.encode("utf-8"))
    print (anotherHash.hexdigest())
    
if __name__ == "__main__":
    # md5 = MD5Context()
    # md5.update(b"admin")
    # passwd_md5 = md5.final().hex()
    # signature = "60d11a81a26df3738026b1839644a1ae" + passwd_md5
    # md5.update(signature.encode("utf-8"))
    # print(md5.final().hex())
    testMD5()