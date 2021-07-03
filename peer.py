'''
Desenvolvedor: Gabriel Rios Souza
Data: 01/06/2021
Objetivo: Classe para representar Peers no sistema de compartilhamento de Arquivos
'''

#Bibliotecas Padrão do Python 
import socket
import os
import random

#Classes Criadas
from mensagem import Mensagem

class Peer:
  
  def __init__(self, serverHost, serverPort, bufferSize) -> None:
    
    self.SERVER_ADDRESS = (serverHost, serverPort)
    self.PEER_ADDRESS = None
    self.PATH = None
    self.BUFFER_SIZE = bufferSize
    
    self.socketUDP = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)  #UDP for Internet IPv4
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

  def requestSEARCH(self) -> None:
    '''Realiza o request SEARCH do Peer ao Servidor'''
    
    #Inputs Iniciais
    file = input('Arquivo: ').lower()
    
    #Cria Mensagem do Request SEARCH
    dicBody = {"PeerAddress": self.PEER_ADDRESS,
               "File": file}
    oMensagemEnvio = Mensagem("SEARCH", dicBody)    
    
    #Enviar Request SEARCH ao Servidor
    self.socketUDP.sendto(oMensagemEnvio.toJSON(), self.SERVER_ADDRESS)

    #Recebe Resposta do Servidor
    serverJSON, _ = self.socketUDP.recvfrom(self.BUFFER_SIZE)
    oMensagemResposta = Mensagem(jsonMessage=serverJSON)

    if oMensagemResposta.head == "SEARCH_OK":
      if oMensagemResposta.body['PeersList'] != []:
        print(f"Peers com arquivo solicitado: {' '.join([str(peerAddres[0])+':'+str(peerAddres[1]) for peerAddres in oMensagemResposta.body['PeersList']])}")
      else: print("Não há Peers com o arquivo solicitado")
       
  def requestDOWNLOAD(self) -> None:
    pass

  def requestLEAVE(self) -> None:
    '''Realiza o request LEAVE do Peer ao Servidor'''
    
    #Cria Mensagem do Request LEAVE
    dicBody = {"PeerAddress": self.PEER_ADDRESS}
    oMensagemEnvio = Mensagem("LEAVE", dicBody)    
    
    #Enviar Request LEAVE ao Servidor
    self.socketUDP.sendto(oMensagemEnvio.toJSON(), self.SERVER_ADDRESS)

    #Recebe Resposta do Servidor
    serverJSON, serverAddr = self.socketUDP.recvfrom(self.BUFFER_SIZE)
    oMensagemResposta = Mensagem(jsonMessage=serverJSON)

    if oMensagemResposta.head == "LEAVE_OK": self.close()

  def getFilesFromPath(self) -> None:
    '''Analisa pasta do Peer e retorna lista de arquivos .mp4'''
    entries = os.listdir(self.PATH)
    self.files = [file.lower() for file in entries if file.lower().endswith('.ipynb')]

  def close(self) -> None:
    self.socketUDP.close()



#Constantes
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 10098
BUFFER_SIZE = 1024

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




# CLIENT_MESSAGE = input(">")
# BYTES_MESSAGE = str.encode(CLIENT_MESSAGE, encoding='utf-8') # Convert String to Bytes (using UTF-8)

# # Sending message to Server
# sock.sendto(BYTES_MESSAGE, SERVER_ADDRESS)

# # Get message from Server
# serverData, serverAddr = sock.recvfrom(BUFFER_SIZE)
# serverMSG = serverData.decode(encoding='utf-8')

# print(f"Message from Server: {serverMSG}")

