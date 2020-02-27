import pygame

from gameConstants import *
from gameClasses import *
from auxiliares import *
from netcode import *
import netcode
import pygame

class Hud:
    def __init__(self,size=20):
        self.manager=GameManager.instance()
        self.size=size
        self.font1 = pygame.font.Font('fonts/roboto/Roboto-Bold.ttf', self.size)
        self.buffer=[]

    def update(self,list):
        self.buffer=[]
        for i in range(len(list)):
            text1 = self.font1.render(list[i], True, (0, 0, 0))
            self.buffer.append(text1)

    def draw(self):
        for i in range(len(self.buffer)):
            self.manager.win.blit(self.buffer[i], (0, i*self.size))
                 
class Camera:
    def __init__(self,objects,plataforms,focus,bg_path="bg.bmp"):
        self.manager=GameManager.instance()
        self.focus=focus
        self.bg=pygame.image.load(bg_path).convert()
        self.limiteR=0
        self.limiteL=9999
        self.lastPos=0
        self.offset=pygame.Vector2(G_WIDTH/2,0)

    def drawFrame(self,objects,plataforms):
        self.manager.win.blit(self.bg,[ 0,0])

        allobjects={}
        allobjects.update(objects)
        allobjects.update(plataforms)

        for chave in plataforms:
            i=allobjects[chave]
            xpos=i.rect.x-self.focus.x+self.offset.x
            ypos=i.rect.top

            self.manager.win.blit(i.image,(xpos,ypos))
        self.manager.hud.draw() 

                 
class GameManager:


    _instance = None


    @classmethod
    def instance(cls):
        if GameManager._instance is None:
            raise Exception("Game manager foi pedido antes de ser invocado")
        else:
            return GameManager._instance

    def __init__(self,title="jogo1",width=G_WIDTH,height=G_HEIGHT,isServer=True,addr="127.0.0.1"):
        GameManager._instance =self
        self.GID=0 
        self.isServer=isServer
        self.width=width
        self.height=height
        self.title=title

    def start(self):



        pygame.init()
        self.win = pygame.display.set_mode((self.width,self.height))
        self.size = (self.width, self.height)
        pygame.display.set_caption(self.title)
        self.clock=pygame.time.Clock() 


        self.hud=Hud()
        


        self.objects={}
        self.plataforms={}
        self.readMap2("maps/map2.txt")
        
        


        if self.isServer:
            self.player=Player((600,0,32,320),netstate=IS_LOCAL)
            self.player2=Player((600,0,32,32),netstate=IS_ONLINE)
            self.inimigo1=Enemy((800,0,32,32),netstate=IS_LOCAL)
        else:
            self.player2=Player((600,0,32,320),netstate=IS_ONLINE)
            self.player=Player((600,0,32,32),netstate=IS_LOCAL)
            self.inimigo1=Enemy((800,0,32,32),netstate=IS_ONLINE)
        
        insertDict(self.objects,self.player)
        insertDict(self.objects,self.player2)
        insertDict(self.objects,self.inimigo1)




        if self.isServer:
            self.netManager=netcode.NetManagerServer(self)
        else:
            self.netManager=netcode.NetManagerClient(self)

        self.cam=Camera(self.objects,self.plataforms,focus=self.player.rect)
        self.hud=Hud()

       

        self.mainLoop()

    def createID(self):
        self.GID+=1
        return self.GID

    def mainLoop(self,gameClock=30):

        is_running=True
        while is_running :
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    self.netManager.stop() 
                    return
            
            for chave in self.objects:
                i=self.objects[chave]

                if i.isAlive==False:
                    del self.objects[chave]

                if i.netstate==IS_ONLINE:
                    i.oflineUpdate()
                else:
                    i.update()

            isok=self.netManager.update()
            if isok==-1:
                is_running=False



                                        
            self.cam.drawFrame(self.objects,self.plataforms)     
            #self.hud.Draw() 
            pygame.display.flip()
            self.clock.tick(gameClock)
            
    def readMap2(self,mapPath):
        with open(mapPath,"r") as f:
            lines=f.read().split("\n")

        rect_matrix=[]
        for  i in range(len(lines)):
            for j in range(len(lines[i])):
                block=None
                if lines[i][j]=="G":
                    block=Platform((BLOCK_SIZE*j,BLOCK_SIZE*i,BLOCK_SIZE,BLOCK_SIZE),"textura/grass.png")
                elif lines[i][j]=="M":
                    block=Platform((BLOCK_SIZE*j,BLOCK_SIZE*i,BLOCK_SIZE,BLOCK_SIZE),"textura/marble.png")
                elif lines[i][j]=="C":
                    block=Coin((BLOCK_SIZE*j,BLOCK_SIZE*i,BLOCK_SIZE,BLOCK_SIZE))
                elif lines[i][j]=="L":
                    block=Lava((BLOCK_SIZE*j,BLOCK_SIZE*i,BLOCK_SIZE,BLOCK_SIZE))
                elif lines[i][j]=="f":
                    block=Flag((BLOCK_SIZE*j,BLOCK_SIZE*i,BLOCK_SIZE,BLOCK_SIZE),part="bottom")
                elif lines[i][j]=="F":
                    block=Flag((BLOCK_SIZE*j,BLOCK_SIZE*i,BLOCK_SIZE,BLOCK_SIZE),part="top")
                if not block is None:
                    insertDict(self.plataforms,block)
        
    def restart(self):
        print("restarted")
        self.__init__()
    def winGame(self,other):
        print("ganhou o jogo")






