import argparse
import threading, _thread
import time
import signal
import socket
import sys
import time


# Fork listener
# Implement sender

def server_bind(sock, server, port):
    sock.bind((server, port))
    if (sock.type == socket.SOCK_STREAM):
        sock.listen(1)
        (conn, _) = sock.accept()
    else:
        conn = sock
    return conn

def client_connect(sock, server, port):
    try:
        sock.connect((server, port))
    except ConnectionRefusedError:
        # Failed to connect. Fail silently and exit
        sys.exit(0)

def recv_loop(sock:socket.socket):
    recv_bytes = True
    try:
        while (recv_bytes):
            recv_bytes = sock.recv(4096)
            print(recv_bytes.decode('utf-8'), end='')
    except ConnectionRefusedError:
        # Connection refused. Signal main htread to exit
        pass
    finally:
        signal.raise_signal(signal.SIGABRT)

def send_loop(sock:socket.socket):
    try:
        while (True):
            send_bytes = (input() + '\n').encode('utf-8')
            sock.send(send_bytes)
    except EOFError:
        # Signal main thread to exit
        pass
    finally:
        signal.raise_signal(signal.SIGABRT)

def foo(signum, unused):
    print('Handled')
    sys.exit(0)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='A simple nc clone in python')
    parser.add_argument('-l', '--listen', action='store_true', help='start nc as a client instead of a server')
    parser.add_argument('-u', '--udp', action='store_true', help='use UDP instead of TCP')
    parser.add_argument('server', type=str,  nargs='?', default='', help='the server to connect to')
    parser.add_argument('port', type=int, nargs='?', help='the port number to connect to or listen on')
    args = parser.parse_args()

    #server = None
    #port = None
    if (args.port):
        server = args.server
        port = args.port
    else:
        server = ''
        port = int(args.server)

    # Create Socket
    sock = None
    sock_type = socket.SOCK_DGRAM if args.udp else socket.SOCK_STREAM
    sock = socket.socket(socket.AF_INET, sock_type)

    # Bind or connect
    if (args.listen):
        sock = server_bind(sock, server, port)
    else:
        client_connect(sock, server, port)

    # Fork receiver
    tr = threading.Thread(target=recv_loop, args=(sock,))
    tr.setDaemon(True)
    tr.start()

    # Fork sender
    ts = threading.Thread(target=send_loop, args=(sock,))
    ts.setDaemon(True)
    ts.start()

    signal.pause()