

import pygame
import socket
from socket import error as SocketError
import json
import os
import threading 


PORTA=1290
def generateID():
    return os.urandom(8).hex()

              
class MainGameServer:

        
    def __init__(self):
        self.dinamics={}
        self.statics=[]
        self.readMap2("maps/map2.txt")
            
            
        player1=Player(pygame.Rect(600,0,32,32))
        player2=Player(pygame.Rect(600,0,32,32))
        inimigo1=Enemy(pygame.Rect(800,0,32,32))
            
        self.dinamics[player1.id]=player1
        self.dinamics[player2.id]=player2
        self.dinamics[inimigo1.id]=inimigo1

        self.netManager=netcode.NetManagerServer()

        self.mainLoop()

        

    def mainLoop(self):
        is_running=True
 
        while is_running :
            for i in self.dinamics:
                if i.isAlive==False:
                    del self.dinamics[i.id]
                else:
                    i.Update()
                                        
            
    def readMap2(self,mapPath):
        with open(mapPath,"r") as f:
            lines=f.read().split("\n")

        rect_matrix=[]
        for  i in range(len(lines)):
            for j in range(len(lines[i])):
                #print(lines[i][j],end="")
                if lines[i][j]=="G":
                    self.statics.append(Platform(pygame.Rect(BLOCK_SIZE*j,BLOCK_SIZE*i,BLOCK_SIZE,BLOCK_SIZE),"textura/grass.png"))
                elif lines[i][j]=="M":
                    self.statics.append(Platform(pygame.Rect(BLOCK_SIZE*j,BLOCK_SIZE*i,BLOCK_SIZE,BLOCK_SIZE),"textura/marble.png"))
                elif lines[i][j]=="C":
                    self.statics.append(Coin(pygame.Rect(BLOCK_SIZE*j,BLOCK_SIZE*i,BLOCK_SIZE,BLOCK_SIZE)))
                elif lines[i][j]=="L":
                    self.statics.append(Lava(pygame.Rect(BLOCK_SIZE*j,BLOCK_SIZE*i,BLOCK_SIZE,BLOCK_SIZE)))
                elif lines[i][j]=="f":
                    self.statics.append(Flag(pygame.Rect(BLOCK_SIZE*j,BLOCK_SIZE*i,BLOCK_SIZE,BLOCK_SIZE),part="bottom"))
                elif lines[i][j]=="F":
                    self.statics.append(Flag(pygame.Rect(BLOCK_SIZE*j,BLOCK_SIZE*i,BLOCK_SIZE,BLOCK_SIZE),part="top"))
                                                                        
        #for i in rect_matrix:
                                 
        
    def restart(self):
        print("restarted")
        self.__init__()
    def WinGame(self,other):
        print("ganhou o jogo")

                 
class MainGameClient:
    def __init__(self,title="jogo1",width=720,height=G_HEIGHT,addr="127.0.0.1"):
        global MANAGER , HUD
        
        self.netManager=netcode.NetManagerClient(self,addr)
        pygame.init()
        self.hud=Hud()
        HUD=self.hud
        MANAGER=self
        self.win = pygame.display.set_mode((width,height))
        self.size = (width, height)
        pygame.display.set_caption(title)
        self.clock=pygame.time.Clock() 
        
        self.dinamics=self.ask_dinamics()
        self.statics=self.ask_statics()
        
        self.player=self.ask_player()

        self.cam=Camera(self.win,self.dinamics,self.statics,focus=self.player.rect)

        self.hud=Hud()
        self.netManager.run()
        #atualiza a lista dinamics assincronamente, alem de ser capaz de ativar eventos no manager
        self.mainLoop()

        

    def mainLoop(self):
        global GAME_CLOCK
        is_running=True
 
        while is_running :
            for e in pygame.event.get():
                if e.type == pygame.QUIT: 
                    is_running=False
                    

            for i in self.dinamics:
                if i.isAlive==False:
                    del self.dinamics[i.id]
                else:
                    i.Update()

            for i in self.statics:
                i.UpdateSprite()
                                        
            self.cam.DrawFrame(self.dinamics,self.statics)     
            self.hud.Draw() 
            pygame.display.flip()
            self.clock.tick(GAME_CLOCK)                                 
        
    def restart(self):
        print("restarted")
        self.__init__()
    def WinGame(self,other):
        print("ganhou o jogo")
             




class Entity(pygame.sprite.Sprite):
    def __init__(self,rect,path="",tags=[],color=pygame.Color("#DD00FF") ,isLocal=True,*groups):
        super().__init__(*groups)
        self.id=generateID()
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