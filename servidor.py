import socket
import threading
from mensagem import Mensagem

class Servidor:
    
    def __init__(self, sHost, nPort, nBufferSize)  -> None:
        
        self.HOST = sHost
        self.SERVER_ADDRESS = (sHost, nPort)
        self.BUFFER_SIZE = nBufferSize
        
        self.socketUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #UDP for Internet Address IPv4          
        self.socketUDP.bind(self.SERVER_ADDRESS)
                
        self.dicFiles = {}
        self.dicPeers = {}

    def listen(self) -> None:
        '''Metodo para iniciar o servidor e aguardar mensagens dos Peers'''

        while True:

            # Receiving message from client
            peerJSON, peerAddr = self.socketUDP.recvfrom(BUFFER_SIZE)

            #Creating Thread to Comunicate with Peers
            thread = threading.Thread(group=None, target=self.communicate, args=(peerJSON, peerAddr))
            thread.start()
                
    def communicate(self, peerJSON, peerAddress) -> None:
        '''Metodo utilizado em Threads para enviar mensagens com sockets UDP para Peers'''
        
        oMensagemRecebida = Mensagem(jsonMessage=peerJSON)
        
        if oMensagemRecebida.head == "JOIN": self.executeJOIN(oMensagemRecebida, peerAddress)
        elif oMensagemRecebida.head == "LEAVE": self.executeLEAVE(peerAddress)
        
    def executeJOIN(self, oMensagem, peerAddress) -> None:
        
        # Adicionando Peer e Files ao Servidor 
        self.dicPeers[peerAddress] = oMensagem.body['files']
        for file in oMensagem.body['files']:
            if file in self.dicFiles: self.dicFiles[file].append(peerAddress)
            else: self.dicFiles[file] = [peerAddress]
        
        # Sending a reply to peer:
        oSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #UDP Using Internet Address IPv4
        oMensagemEnvio = Mensagem("JOIN_OK", {})
        oSocket.sendto(oMensagemEnvio.toJSON(), peerAddress)
        oSocket.close()
        
        print(f"Peer {peerAddress[0]}:{peerAddress[1]} adicionado com arquivos {' '.join(oMensagem.body['files'])}")
        print(self.dicFiles)
        print(self.dicPeers)
        
    def executeLEAVE(self, peerAddress) -> None:
        
        # Removendo Peer e seus Files do Servidor
        removeFiles = self.dicPeers[peerAddress]
        del self.dicPeers[peerAddress]
        
        for file in removeFiles: 
            self.dicFiles[file].remove(peerAddress)
            if self.dicFiles[file] == []: del self.dicFiles[file] 
            
        # Sending a reply to peer:
        oSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #UDP Using Internet Address IPv4
        oMensagemEnvio = Mensagem("LEAVE_OK", {})
        oSocket.sendto(oMensagemEnvio.toJSON(), peerAddress)
        oSocket.close()
        
        print(self.dicFiles)
        print(self.dicPeers)
        
    def close(self) -> None:
        self.socketUDP.close()


# Constantes
HOST = "127.0.0.1"      # Hostname, IP Address or empty string. (localhost IP)
PORT = 10098            # Listen on (1-65535, non-privileged ports are > 1023)
BUFFER_SIZE = 1024


# Iniciando Servidor
try:
    oServidor = Servidor(HOST, PORT, BUFFER_SIZE)
    oServidor.listen()
except:
    oServidor.close()