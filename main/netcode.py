

import pygame
import socket
from socket import error as SocketError
import json
import threading 
PORTA=1290



class Entity(pygame.sprite.Sprite):
    def __init__(self,rect,path="",tags=[],color=pygame.Color("#DD00FF") ,isLocal=True,*groups):
        super().__init__(*groups)
        self.isLocal=isLocal
        self.rect = rect 
        self.tags=tags
        self.isAlive=True
        self.count=0


        if "dinamic" in self.tags:
            self.sprites=OpenSprites(path,32,32)
            self.sprites_len=len(self.sprites)
            self.image=self.sprites[0]
            


        elif "color" in self.tags:
            self.image =  pygame.Surface((rect.width,rect.height))
            self.image.fill(color)

        elif path!="" and "static" in tags:
            img=pygame.image.load(path)
            width=rect.width
            heigh=rect.height
            self.image=pygame.transform.scale(img,(rect.width,rect.height))
    def serialize():
        #rectx
        varlist=[self.rect.x,self.rect.y,self.isAlive,self.count]
        return json.dumps(varlist)
    def unserialize(jsonlist):
        varlist=json.loads(jsonlist)
        self.rect.x=varlist[0]
        self.isAlive=varlist[1]
        self.count=varlist[2]
        




    def Update(self):
        if "dinamic" in self.tags:
            self.image=self.sprites[self.count%self.sprites_len]
            self.count+=1
  


    def Collide(self,other,xvel,yvel):
        if "collider" in self.tags:
            if xvel > 0:
                other.rect.right= self.rect.left
            elif xvel < 0 :
                other.rect.left = self.rect.right
            elif yvel > 0 :
                other.rect.bottom = self.rect.top
                other.is_jumping=False
                other.speed.y=0
            elif yvel <0:
                other.rect.top = self.rect.bottom
                other.speed.y=0

        if "dinamic" in self.tags:
            self.Interact(other)

    def GetDistance(self,other):
        return (abs(self.rect.x - other.rect.x)**2 + abs(self.rect.y - other.rect.y)**2)


#o servidor ta sempre serto. Nao existem classes locais. Cada  objeto possui um ID setado pelo servidor o servidor pode setar qualquer variavel pra qualquer classe.
# os clientes enviam de tempo em tempo dados sobre poucas variaveis q eles controlam sobre algumas classes. como é impossivel o estado de jogo estar igual entre o servidor e cliente, no  começo do jogo, o servidor devera poder CRIAR classes 
# no game manager do jogador. 

#pra amanha: fazer uma classe serialize, deserialize pra cada entity.
#serialize pega os dados e transforma num json, dps envia deserialize recebe um json e dps carrega.
#havera o metodo update e online update.
# para multi instancia, sera uma lista de dicionarios o primeiro dicionario para a classe filha, que dara um pop(0)
class NetManagerServer:
    def __init__(self,listalocal,listaOnline):
        self.listalocal=listalocal
        self.listaOnline=listaOnline

        self.socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.socket.bind(("",PORTA)) 
        self.socket.listen(10)
        while True:
            conn,addr = self.socket.accept()
            threading.Thread(target=self.client_t,args=(conn,addr)).start()

    def client_t(self,conn,addr):
        while True:
            try:
                conn.send(b"bem vindo ao server")
                print(conn.recv(1024))
            except SocketError as e :
                print("erro do cliente")
                return 

class NetManagerClient:
    def __init__(self,listalocal,listaOnline,address="127.0.0.1"):
        self.address=address
        self.listalocal=listalocal
        self.listaOnline=listaOnline

        self.socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.socket.connect((address,PORTA))


    def run(self):
        while True:
            #varre a lista de classes
            jsonlist=[]
            for i in listalocal:
                serializdo=i.serialize()
                if serializdo!=[]:
                    jsonlist.append(i.serialize())

            packet=[i+b"\x00" for i in bytes(jsonlist,"utf-8")][:-1]



            
            recebindo = self.socket.recv(1024)
            lista= recebindo.split(b"\x00")

            self.socket.send(packet)