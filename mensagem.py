'''
Desenvolvedor: Gabriel Rios Souza
Data: 01/06/2021
Objetivo: Classe para representar Mensagem enviada/recebida no sistema de compartilhamento de Arquivos
'''

#Bibliotecas Padrão do Python
import json
   
class Mensagem:
  
  def __init__(self, sHead="", dicBody={}, jsonMessage=None) -> None:
    if not jsonMessage:
      self.head = sHead
      self.body = dicBody
    else:
      obj = json.loads(jsonMessage.decode(encoding='utf-8'))
      self.head = obj["head"]
      self.body = obj["body"]
      
  def toJSON(self) -> str:
    '''Converte a instancia dessa classe para JSON'''
    return str.encode(json.dumps(self, indent = 4, default=lambda o: o.__dict__), encoding='utf-8')
  
  
  