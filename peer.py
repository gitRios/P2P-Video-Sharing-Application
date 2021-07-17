'''
Desenvolvedor: Gabriel Rios Souza
Data: 01/06/2021
Objetivo: Classe para representar Peers no sistema de compartilhamento de Arquivos
'''

#Bibliotecas Padrão do Python 
import socket
import os
import random
import threading

#Classes Criadas
from mensagem import Mensagem

class Peer:
  
  def __init__(self, serverHost, serverPort, bufferSize) -> None:
    
    self.SERVER_ADDRESS = (serverHost, serverPort)
    self.PEER_ADDRESS = None
    self.PATH = None
    self.BUFFER_SIZE = bufferSize
    
    self.socketUDP = socket.socket(socket.AF_INET,socket.SOCK_DGRAM) #UDP for Internet IPv4
    self.socketTCP = socket.socket(socket.AF_INET,socket.SOCK_STREAM) #TCP for Internet IPv4
    self.files = []

  def requestJOIN(self) -> None:
    '''Realiza o request JOIN do Peer ao Servidor'''
    
    #Inputs Iniciais
    peerIP = input('IP: ')
    peerPort = int(input('Porta: '))
    self.PATH = input('Pasta dos Arquivos: ')
    
    self.PEER_ADDRESS = (peerIP, peerPort)
    self.socketUDP.bind(self.PEER_ADDRESS)
    
    #Varre Pasta e Verifica Arquivos .mp4 
    self.getFilesFromPath()

    #Cria Mensagem do Request JOIN
    dicBody = {"PeerAddress": self.PEER_ADDRESS,
               "files": self.files}
    oMensagemEnvio = Mensagem("JOIN", dicBody)    
    
    #Enviar Request JOIN ao Servidor
    self.socketUDP.sendto(oMensagemEnvio.toJSON(), self.SERVER_ADDRESS)

    #Recebe Resposta do Servidor
    serverJSON, _ = self.socketUDP.recvfrom(self.BUFFER_SIZE)
    oMensagemResposta = Mensagem(jsonMessage=serverJSON)

    if oMensagemResposta.head == "JOIN_OK":
      print(f"Sou peer {peerIP}:{peerPort} com arquivos {' '.join(self.files)}")
      
      # Criando Thread para se comunicar com outros Peers
      thread = threading.Thread(group=None, target=self.startSocketTCP, args=())
      thread.daemon = True #Configurando a Thread como Daemon para que interrompa caso acabe o programa.
      thread.start()
      
      # Criando Thread para receber respostas e requisições ALIVE do Servidor
      threadALIVE = threading.Thread(group=None, target=self.listen, args=())
      threadALIVE.daemon = True #Configurando a Thread como Daemon para que interrompa caso acabe o programa.
      threadALIVE.start()

  def requestSEARCH(self) -> None:
    '''Realiza o request SEARCH do Peer ao Servidor'''
    
    #Inputs Iniciais
    file = input('Arquivo: ').lower()
    
    #Cria Mensagem do Request SEARCH
    dicBody = {"PeerAddress": self.PEER_ADDRESS,
               "File": file}
    oMensagemEnvio = Mensagem("SEARCH", dicBody)    
    
    #Enviar Request SEARCH ao Servidor
    oSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #UDP Using Internet Address IPv4    
    oSocket.sendto(oMensagemEnvio.toJSON(), self.SERVER_ADDRESS)    
    oSocket.close()
    
  def requestDOWNLOAD(self) -> None:
    '''Realiza o request DOWNLOAD do Peer a outro Peer'''
    
    #Inputs Iniciais
    peerIP = input('IP: ')
    peerPort = int(input('Porta: '))
    file = input('Arquivo: ').lower()
    
    #Cria Socket TCP e se Conecta com o Peer selecionado
    oSocketTCP = socket.socket()
    oSocketTCP.connect((peerIP, peerPort))
    oSocketTCP.settimeout(5)

    try:

      #Cria e envia Mensagem para requisitar DOWNLOAD
      dicBody = {"File": file}
      oMensagemEnvio = Mensagem("DOWNLOAD", dicBody)
      oSocketTCP.send(oMensagemEnvio.toJSON())
      
      #Recebe Resposta do Peer
      peerJSON = oSocketTCP.recv(self.BUFFER_SIZE)
      oMensagemRecebida = Mensagem(jsonMessage=peerJSON)
          
      if oMensagemRecebida.head == "DOWNLOAD_NEGADO":
        print(f"Peer {peerIP}:{peerPort} negou o download")
      
      else:
        
        fileSize = int(oMensagemRecebida.body['FileSize'])
        filePath = self.PATH + "\\" + file
        
        with open(filePath, "wb") as newFile:
            while True:
              
                # Read Bytes from the socket (receive)
                bytes_read = oSocketTCP.recv(BUFFER_SIZE)
                
                if not bytes_read: break # file transmitting is done
              
                # write to the file the bytes we just received
                newFile.write(bytes_read)
        print(f"Arquivo {file} baixado com sucesso na pasta {self.PATH}")
        self.requestUPDATE(file)
      
    except Exception as e:
      print(e)            
    
    oSocketTCP.close()   

  def requestLEAVE(self) -> None:
    '''Realiza o request LEAVE do Peer ao Servidor'''
    
    #Cria Mensagem do Request LEAVE
    dicBody = {"PeerAddress": self.PEER_ADDRESS}
    oMensagemEnvio = Mensagem("LEAVE", dicBody)    
    
    #Enviar Request LEAVE ao Servidor
    oSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #UDP Using Internet Address IPv4    
    oSocket.sendto(oMensagemEnvio.toJSON(), self.SERVER_ADDRESS)    
    oSocket.close()
    
  def requestUPDATE(self, file) -> None:
    '''Realiza o request UPDATE do Peer ao Servidor'''
    
    #Cria Mensagem do Request UPDATE
    dicBody = {"PeerAddress": self.PEER_ADDRESS,
               "File": file}
    oMensagemEnvio = Mensagem("UPDATE", dicBody)    
    
    #Enviar Request UPDATE ao Servidor
    oSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #UDP Using Internet Address IPv4    
    oSocket.sendto(oMensagemEnvio.toJSON(), self.SERVER_ADDRESS)    
    oSocket.close()

  def startSocketTCP(self) -> None:
    
    self.socketTCP.bind(self.PEER_ADDRESS)
    self.socketTCP.listen(5)

    while True:
          
      oSocketConnected, _ = self.socketTCP.accept()
      
      # Criando Thread para abrir comunicação com o Peer
      thread = threading.Thread(group=None, target=self.executeDOWNLOAD, args=(oSocketConnected,))
      thread.start()
    
  def executeDOWNLOAD(self, oSocketConnected) -> None:
    '''Executa o request DOWNLOAD vindo de outro Peer'''
        
    #Recebe Requisição do Peer
    peerJSON = oSocketConnected.recv(self.BUFFER_SIZE)
    oMensagemRecebida = Mensagem(jsonMessage=peerJSON)
    arquivoBuscado = oMensagemRecebida.body['File']

    if oMensagemRecebida.head == "DOWNLOAD":
      
      if random.random() > 0.5 or arquivoBuscado not in self.files:
        oMensagemEnvio = Mensagem("DOWNLOAD_NEGADO", {})
        oSocketConnected.send(oMensagemEnvio.toJSON())
      
      else:
        
        # Get Tamanho do Arquivo
        filePath = self.PATH + "\\" + arquivoBuscado
        filesize = os.path.getsize(filePath)

        #Cria Mensagem para Confirmar DOWNLOAD
        dicBody = {"FileSize": filesize}
        oMensagemEnvio = Mensagem("DOWNLOAD_ACEITO", dicBody)
        oSocketConnected.send(oMensagemEnvio.toJSON())
        
        with open(filePath, "rb") as file:
          while True:
              # read the bytes from the file
              bytes_read = file.read(BUFFER_SIZE)
              
              if not bytes_read: break # file transmitting is done
              
              # we use sendall to assure transimission in busy networks
              oSocketConnected.sendall(bytes_read)
         
    oSocketConnected.close()
    
  def listen(self) -> None:
    '''Thread para receber respostas e requisições ALIVE do Servidor'''
        
    while True:
        # Recebendo Mensagem do Peer
        serverJSON, serverAddress = self.socketUDP.recvfrom(BUFFER_SIZE)
        oMensagemRecebida = Mensagem(jsonMessage=serverJSON)
        
        if oMensagemRecebida.head == "ALIVE":
          oMensagemEnvio = Mensagem("ALIVE_OK", {})
          self.socketUDP.sendto(oMensagemEnvio.toJSON(), serverAddress)
        
        elif oMensagemRecebida.head == "SEARCH_OK":
          if oMensagemRecebida.body['PeersList'] != []:
            print(f"Peers com arquivo solicitado: {' '.join([str(peerAddres[0])+':'+str(peerAddres[1]) for peerAddres in oMensagemRecebida.body['PeersList']])}")
          else: print("Não há Peers com o arquivo solicitado")
        
        elif oMensagemRecebida.head == "LEAVE_OK": self.close()
        elif oMensagemRecebida.head == "UPDATE_OK": pass
        
  def getFilesFromPath(self) -> None:
    '''Analisa pasta do Peer e retorna lista de arquivos .mp4'''
    entries = os.listdir(self.PATH)
    self.files = [file.lower() for file in entries if file.lower().endswith('.mp4')]

  def close(self) -> None:
    self.socketUDP.close()
    self.socketTCP.close()


#Constantes
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 10098
BUFFER_SIZE = 4096


#Trocar o SocketUDP das requisições por oSocket

#Iniciar Peer
oPeer = Peer(SERVER_HOST, SERVER_PORT, BUFFER_SIZE)

dicOpcoes = {1: oPeer.requestJOIN,
             2: oPeer.requestSEARCH,
             3: oPeer.requestDOWNLOAD,
             4: oPeer.requestLEAVE}

while True:
  
  print("\n" + ("-" * 10), "MENU INTERATIVO", "-" * 10)
  print("\n1 - JOIN")
  print("2 - SEARCH")
  print("3 - DOWNLOAD")
  print("4 - LEAVE\n")
  
  opcao = int(input("> "))
  print()
  
  # Executa a Opçao Selecionada
  dicOpcoes[opcao]()
  
  if opcao == 4: break