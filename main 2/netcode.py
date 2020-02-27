from gameConstants import *
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
  
# {id: objlist [aadd, update,remove] } init dos metodos chama uma funcao do manager 

#o servidor ta sempre serto. Nao existem classes locais. Cada  objeto possui um ID setado pelo servidor o servidor pode setar qualquer variavel pra qualquer classe.
# os clientes enviam de tempo em tempo dados sobre poucas variaveis q eles controlam sobre algumas classes. como é impossivel o estado de jogo estar igual entre o servidor e cliente, no  começo do jogo, o servidor devera poder CRIAR classes 
# no game manager do jogador. 

#pra amanha: fazer uma classe serialize, deserialize pra cada entity.
#serialize pega os dados e transforma num json, dps envia deserialize recebe um json e dps carrega.
#havera o metodo update e online update.
# para multi instancia, sera uma lista de dicionarios o primeiro dicionario para a classe filha, que dara um pop(0)

def parse(id,list):





class NetBase:
    def __init__(self,manager,address="127.0.0.1"):
        
        self.manager=manager
        self.objects=self.manager.objects
        self.address=address
        self.comands={}
        self.start()

    def addToOnline(object):
        pass




class NetManagerServer(NetBase):


    def start(self):
        self.socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.socket.bind((self.address,PORTA)) 
        self.socket.listen(10)
        self.conn,self. cliente = self.socket.accept()

    def update(self):

        print(self.objects)
               
        toSend={}
        for chave in self.objects:
            i=self.objects[chave]
            if i.netstate==IS_LOCAL:
                toSend[i.id]=i.post()
            
            
        #try:
            #print("enviando",toSend)
            self.conn.sendall(bytes(json.dumps(toSend),"utf-8"))
            recebido=self.conn.recv(2048)
            #print("recebido",recebido)
            recived=json.loads(recebido)
            for chave in recived:
                i=self.objects[int(chave)]
                i.get(recived[chave])
        #except:
        #    print("pacote perdido")
        #    return -1

        self.comands={}



class NetManagerClient(NetBase):

    def start(self):
        self.socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.socket.connect((self.address,PORTA))


    def update(self):
        #try:
            print(self.objects)

            recived=self.socket.recv(2048)
            #print("recebido",recived)
            recived=json.loads(recived)
            
            for chave in recived:
                
                i=self.objects[int(chave)]
                i.get(recived[chave])

            toSend=self.comands
            for chave in self.objects:
                i=self.objects[chave]
                if i.netstate==IS_LOCAL:
                    toSend[i.id]=i.post()
            #print("enviando",toSend)
            self.socket.sendall(bytes(json.dumps(toSend),"utf-8"))
        #except:
        #    print("pacote perdido")
        #    return -1
        self.comands={}

            