'''
Desenvolvedor: Gabriel Rios Souza
Data: 01/06/2021
Objetivo: Classe para representar o Servidor no sistema de compartilhamento de Arquivos

https://www.thepythoncode.com/article/send-receive-files-using-sockets-python
'''

#Bibliotecas Padrão do Python
import socket
import threading

#Classes Criadas
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

            # Recebendo Mensagem do Peer
            peerJSON, peerAddress = self.socketUDP.recvfrom(BUFFER_SIZE)

            # Criando Thread para se comunicar com o Peer
            thread = threading.Thread(group=None, target=self.communicate, args=(peerJSON, peerAddress))
            thread.start()
            
    def communicate(self, peerJSON, peerAddress) -> None:
        '''Metodo utilizado em Threads para enviar mensagens com sockets UDP para Peers'''
        
        oMensagemRecebida = Mensagem(jsonMessage=peerJSON)
        
        if oMensagemRecebida.head == "JOIN": self.executeJOIN(oMensagemRecebida)
        elif oMensagemRecebida.head == "SEARCH": self.executeSEARCH(oMensagemRecebida)
        elif oMensagemRecebida.head == "LEAVE": self.executeLEAVE(oMensagemRecebida)
        elif oMensagemRecebida.head == "UPDATE": self.executeUPDATE(oMensagemRecebida)
        
    def executeJOIN(self, oMensagem) -> None:
        '''Executa a Requisição JOIN vinda do Peer'''
        
        # Adicionando Peer e Files ao Servidor
        peerAddress = tuple(oMensagem.body['PeerAddress'])
        self.dicPeers[peerAddress] = oMensagem.body['files']
        for file in oMensagem.body['files']:
            if file in self.dicFiles: self.dicFiles[file].append(peerAddress)
            else: self.dicFiles[file] = [peerAddress]
        
        # Enviando Resposta ao Peer
        oSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #UDP Using Internet Address IPv4
        oMensagemEnvio = Mensagem("JOIN_OK", {})
        oSocket.sendto(oMensagemEnvio.toJSON(), peerAddress)
        oSocket.close()
                
        print(f"Peer {peerAddress[0]}:{peerAddress[1]} adicionado com arquivos {' '.join(oMensagem.body['files'])}")
    
    def executeSEARCH(self, oMensagem) -> None:
        '''Executa a Requisição SEARCH vinda do Peer'''
        
        peerAddress = tuple(oMensagem.body['PeerAddress'])
        file = oMensagem.body['File']
        
        print(f"Peer {peerAddress[0]}:{peerAddress[1]} solicitou arquivo {file}")
        
        # Enviando Resposta ao Peer:
        oSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #UDP Using Internet Address IPv4
        
        lPeers = [] if file not in self.dicFiles.keys() else self.dicFiles[file]  
        dicBody = {"PeersList": lPeers}
        oMensagemEnvio = Mensagem("SEARCH_OK", dicBody)
        
        oSocket.sendto(oMensagemEnvio.toJSON(), peerAddress)
        oSocket.close()
         
    def executeUPDATE(self, oMensagem) -> None:
        '''Executa a Requisição UPDATE vinda do Peer'''
        
        #Recebendo Endereço do Peer e Arquivo para Atualizar
        peerAddress = tuple(oMensagem.body['PeerAddress'])
        file = oMensagem.body['File']
        
        # Enviando Resposta ao Peer:
        oSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #UDP Using Internet Address IPv4
        
        # Atualiza o arquivo com o Peer na estrutura de dados do Servidor
        if file in self.dicFiles: self.dicFiles[file].append(peerAddress)
        else: self.dicFiles[file] = [peerAddress]
        self.dicPeers[peerAddress].append(file)
        
        oMensagemEnvio = Mensagem("UPDATE_OK", {})
        oSocket.sendto(oMensagemEnvio.toJSON(), peerAddress)
        
        oSocket.close()
    
    
    def executeLEAVE(self, oMensagem) -> None:
        '''Executa a Requisição LEAVE vinda do Peer'''
        
        # Removendo Peer e seus Files do Servidor
        peerAddress = tuple(oMensagem.body['PeerAddress'])
        removeFiles = self.dicPeers[peerAddress]
        del self.dicPeers[peerAddress]
        
        for file in removeFiles: 
            self.dicFiles[file].remove(peerAddress)
            if self.dicFiles[file] == []: del self.dicFiles[file] 
            
        # Enviando Resposta ao Peer:
        oSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #UDP Using Internet Address IPv4
        oMensagemEnvio = Mensagem("LEAVE_OK", {})
        oSocket.sendto(oMensagemEnvio.toJSON(), peerAddress)
        oSocket.close()
        
    def close(self) -> None:
        self.socketUDP.close()


#########################################################################################

# Constantes
PORT = 10098  # Listen on (1-65535, non-privileged ports are > 1023)
BUFFER_SIZE = 4096

# Iniciando Servidor
HOST = input("IP do Servidor: ")      # Hostname, IP Address or empty string. (localhost IP)

try:
    oServidor = Servidor(HOST, PORT, BUFFER_SIZE)
    oServidor.listen()
except:
    oServidor.close()