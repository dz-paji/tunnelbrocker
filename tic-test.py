import socket
import configparser
import hashlib
import ssl
import sys, os

def sockethello():
    socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket.connect(("localhost", 3874))
    socket.send(b"Hello World!")

def config() -> configparser.ConfigParser:
    configger = configparser.ConfigParser()
    configger.read('config/tic.ini')
    return configger
    
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
    # hash = hashlib.md5()
    hash = hashlib.sha256()
    hash.update("admin".encode("utf-8"))
    passwd_md5 = hash.hexdigest()
    print(passwd_md5)
    print("length is " + str(len(passwd_md5)))
    # signature = "60d11a81a26df3738026b1839644a1ae" + passwd_md5
    # newsig = "60d11a81a26df3738026b1839644a1ae21232f297a57a5a743894a0e4a801fc3"
    # anotherHash = hashlib.md5()
    # anotherHash.update(newsig.encode("utf-8"))
    # print (anotherHash.hexdigest())
    
def testSHA256():
    hash = hashlib.sha256()
    hash.update("admin".encode("utf-8"))
    passwd_sha256 = hash.hexdigest()
    print(f"password sha is {passwd_sha256}")
    configger = config()
    challenge = configger.get("Database", "Salt")
    hash_2 = hashlib.sha256()
    hash_2.update((challenge + passwd_sha256).encode("utf-8"))
    print(f"challenge sha is {hash_2.hexdigest()}")
    
def typeTest():
    a = 1
    print(type(a) == int)
    
def sprinfTest():
    print("%d" % "1")

def whatIsTheLength():
    print(len("RmgC.8eAtKJUAfs97KCZ!R96p*BuZKyu"))
    
def testAddTunnel():
    pass
    # idofT = "5"
    # tid = "T4155"
    # type = "10.2.0.5"
    # endpoint_v6 = ""
    # endpoint_v6_prefix = 64
    # endpoint_v4 = ""
    # uid = 1
    # admin_id = 1
    # password = "admin"
    # heartbeat_interval = 120
    # mtu = 1480
    # pop_id = "desktop"
    # sqlConner = SQLConnector()
    # user = sqlConner.getUserById(2)
    # pop = sqlConner.getPop("desktop")
    # print(pop)
    # tEntity = TunnelEntity((idofT, tid,  type, endpoint_v6, endpoint_v6_prefix, endpoint_v4, uid, admin_id, password, heartbeat_interval, mtu, pop_id), user, user, pop)
    # tic_server.addTunnel(tEntity, pop_id)
    
def testTLS():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ctx.load_cert_chain("certs/cer.cer", "certs/key.key")
    sock = ctx.wrap_socket(sock, server_side=True, do_handshake_on_connect=False)
    sock.bind(("localhost", 20089))
    sock.listen(0)
    while True:
        conn, addr = sock.accept()
        print(conn.recv(1024))
        conn.send(b"Hello World!")
        conn.close()
        
def testTLSVer():
    from urllib.request import urlopen
    urlopen('https://www.howsmyssl.com/a/check').read()
    
if __name__ == "__main__":
    # md5 = MD5Context()
    # md5.update(b"admin")
    # passwd_md5 = md5.final().hex()
    # signature = "60d11a81a26df3738026b1839644a1ae" + passwd_md5
    # md5.update(signature.encode("utf-8"))
    # print(md5.final().hex())
    testTLSVer()