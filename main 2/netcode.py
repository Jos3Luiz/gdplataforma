
import sys 
import trace 
import threading 
import time 
import pygame
import socket
from socket import error as SocketError
import json
import os



PORTA=1290
import time 
import threading 
class thread_with_trace(threading.Thread): 
  def __init__(self, *args, **keywords): 
    threading.Thread.__init__(self, *args, **keywords) 
    self.killed = False
  
  def start(self): 
    self.__run_backup = self.run 
    self.run = self.__run       
    threading.Thread.start(self) 
  
  def __run(self): 
    sys.settrace(self.globaltrace) 
    self.__run_backup() 
    self.run = self.__run_backup 
  
  def globaltrace(self, frame, event, arg): 
    if event == 'call': 
      return self.localtrace 
    else: 
      return None
  
  def localtrace(self, frame, event, arg): 
    if self.killed: 
      if event == 'line': 
        raise SystemExit() 
    return self.localtrace 
  
  def kill(self): 
    self.killed = True
  

  


#o servidor ta sempre serto. Nao existem classes locais. Cada  objeto possui um ID setado pelo servidor o servidor pode setar qualquer variavel pra qualquer classe.
# os clientes enviam de tempo em tempo dados sobre poucas variaveis q eles controlam sobre algumas classes. como é impossivel o estado de jogo estar igual entre o servidor e cliente, no  começo do jogo, o servidor devera poder CRIAR classes 
# no game manager do jogador. 

#pra amanha: fazer uma classe serialize, deserialize pra cada entity.
#serialize pega os dados e transforma num json, dps envia deserialize recebe um json e dps carrega.
#havera o metodo update e online update.
# para multi instancia, sera uma lista de dicionarios o primeiro dicionario para a classe filha, que dara um pop(0)
class NetManagerServer:
    def __init__(self,isLocal,isOnline):
        
        self.isLocal=isLocal
        self.isOnline=isOnline

        self.socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.socket.bind(("",PORTA)) 
        self.socket.listen(10)
        self.isAlive=True

        self.tlist=[]
        self.x=thread_with_trace(target=self.init_thread)
        self.x.start()
        self.tlist.append(self.x)

    def init_thread(self):

        while True:
            try:
                conn,addr = self.socket.accept()
                x=thread_with_trace(target=self.client_t,args=(conn,addr))
                x.start()
                self.tlist.append(x)
            except:
                return

    def stop(self):
        #for i in self.tlist:
        #    i.kill()
        self.x.kill()
            


    def client_t(self,conn,addr):
        try:
        while self.isAlive:
            toSend=[]
            for i in self.isLocal:
                toSend.append(i.post())

            conn.sendall(bytes(json.dumps(toSend),"utf-8"))


            recived=json.loads(conn.recv(2048))
            for i in range(len(self.isOnline)):
                self.isOnline[i].get(recived[i])
        except:
                return


class NetManagerClient:
    def __init__(self,isLocal,isOnline,address="127.0.0.1"):
        self.address=address
        self.isLocal=isLocal
        self.isOnline=isOnline

        self.socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.socket.connect((address,PORTA))

        self.tlist=[]
        x=thread_with_trace(target=self.client_t)

        x.start()
        self.tlist.append(x)
        

    def stop(self):
        for i in self.tlist:
            i.kill()


    def client_t(self):
        while True:
            recived=json.loads(self.socket.recv(2048))
            for i in range(len(self.isOnline)):
                self.isOnline[i].get(recived[i])

            toSend=[]
            for i in self.isLocal:
                toSend.append(i.post())
            self.socket.sendall(bytes(json.dumps(toSend),"utf-8")) 


            