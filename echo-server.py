import socket

HOST = '127.0.0.1'    # Hostname, IP Address or empty string. (localhost IP)
PORT = 2000           # Listen on (1-65535, non-privileged ports are > 1023)
SERVER_ADDRESS = (HOST, PORT)

with socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM) as oSocketTCP:
    # Use the socket object without calling oSocketTCP.close()
    # AF_NET is the internet address family for IPv4.
    # SOCK_STREAM is the socket type for TCP.

    oSocketTCP.bind(SERVER_ADDRESS)
    oSocketTCP.listen()

    oSocketConnection, clientAddress = oSocketTCP.accept()

    with oSocketConnection:
        # Use the socket object without calling oSocketConnection.close()
        print('Conected by', clientAddress)  # clientAddress = (HOST, PORT)

        while True:
            data = oSocketConnection.recv(1024)
            # bufsize = 1024 (maximum amount of data to be received at once)

            if not data:
                break
            else:
                oSocketConnection.sendall(data)
