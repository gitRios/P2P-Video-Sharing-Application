import socket

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 2000
SERVER_ADDRESS = (SERVER_HOST, SERVER_PORT)

with socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM) as oSocketTCP:
    oSocketTCP.connect(SERVER_ADDRESS)
    oSocketTCP.sendall(b'Hello World!')
    # 'sendall' method returns None on success.
    # It continues to send data from bytes until either all data has been sent or an error occurs

    data = oSocketTCP.recv(1024)
    # bufsize = 1024 (maximum amount of data to be received at once)

print('Received', repr(data))
