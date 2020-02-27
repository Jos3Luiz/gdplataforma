import pygame

from gameConstants import *
from gameClasses import *
import netcode
import pygame

class hud:
    def __init__(self,size=20):
        self.manager=gameManager.Instance()
        self.size=size
        self.font1 = pygame.font.Font('fonts/roboto/Roboto-Bold.ttf', self.size)
        self.buffer=[]

    def Update(self,list):
        self.buffer=[]
        for i in range(len(list)):
            text1 = self.font1.render(list[i], True, (0, 0, 0))
            self.buffer.append(text1)

    def Draw(self):
        for i in range(len(self.buffer)):
            self.win.blit(self.buffer[i], (0, i*self.size))
                 
class camera:
    def __init__(self,objects,plataforms,focus,bg_path="bg.bmp"):
        self.manager=gameManager.Instance()
        self.focus=focus
        self.bg=pygame.image.load(bg_path).convert()
        self.limiteR=0
        self.limiteL=9999
        self.lastPos=0
        self.offset=pygame.Vector2(G_WIDTH/2,0)

    def DrawFrame(self,objects,plataforms):
        self.manager.win.blit(self.bg,[ 0,0])
        allobjects=objects+plataforms
        for i in allobjects:
            xpos=i.rect.x-self.focus.x+self.offset.x

            ypos=i.rect.top

            self.manager.win.blit(i.image,(xpos,ypos))
        self.manager.hud.Draw() 

                 
class gameManager:


    _instance = None


    @classmethod
    def Instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self,title="jogo1",width=G_WIDTH,height=G_HEIGHT,isServer=True,addr="127.0.0.1"):
        
        self.GID=0 
        self.isServer=isServer


        pygame.init()
        self.win = pygame.display.set_mode((width,height))
        self.size = (width, height)
        pygame.display.set_caption(title)
        self.clock=pygame.time.Clock() 


        self.hud=Hud()
        


        self.objects=[]
        self.plataforms=[]
        self.ReadMap2("maps/map2.txt")
        
        
        self.player=Player((600,0,32,320),netstate=IS_LOCAL)
        self.player2=Player((600,0,32,32),netstate=IS_ONLINE)

        if self.isServer:
            self.inimigo1=Enemy((800,0,32,32),netstate=IS_LOCAL)
        else:
            self.inimigo1=Enemy((800,0,32,32),netstate=IS_ONLINE)
        
        self.objects.append(self.player)
        self.objects.append(self.player2)
        self.objects.append(self.inimigo1)

        self.cam=camera(self.objects,self.plataforms,focus=self.player.rect)



        self.hud=Hud()
        

        self.isOnline={}
        self.isLocal={}

        for i in self.objects:
            if i.netstate==IS_LOCAL:
                self.isLocal[i.id]=i
            if i.netstate==IS_ONLINE:
                self.isOnline[i.id]=i

        if self.isServer:
            self.netManager=netcode.NetManagerServer(self.isLocal,self.isOnline)
        else:
            self.netManager=netcode.NetManagerClient(self.isLocal,self.isOnline)


       

        self.mainLoop()

    def CreateID(self):
        self.GID+=1
        return self.GID

    def MainLoop(self,GAME_CLOCK=30):

        is_running=True
        while is_running :
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    self.netManager.stop() 
                    return
            
            for i in self.objects:
                if i.isAlive==False:
                    self.objects.remove(i)
                if i.netstate==IS_ONLINE:
                    i.OflineUpdate()
                else:
                    i.Update()

            isok=self.netManager.update()
            if isok==-1:
                is_running=False



                                        
            self.cam.DrawFrame(self.objects,self.plataforms)     
            #self.hud.Draw() 
            pygame.display.flip()
            self.clock.tick(GAME_CLOCK)
            
    def ReadMap2(self,mapPath):
        with open(mapPath,"r") as f:
            lines=f.read().split("\n")

        rect_matrix=[]
        for  i in range(len(lines)):
            for j in range(len(lines[i])):
                if lines[i][j]=="G":
                    self.plataforms.append(Platform((BLOCK_SIZE*j,BLOCK_SIZE*i,BLOCK_SIZE,BLOCK_SIZE),"textura/grass.png"))
                elif lines[i][j]=="M":
                    self.plataforms.append(Platform((BLOCK_SIZE*j,BLOCK_SIZE*i,BLOCK_SIZE,BLOCK_SIZE),"textura/marble.png"))
                elif lines[i][j]=="C":
                    self.objects.append(Coin((BLOCK_SIZE*j,BLOCK_SIZE*i,BLOCK_SIZE,BLOCK_SIZE)))
                elif lines[i][j]=="L":
                    self.objects.append(Lava((BLOCK_SIZE*j,BLOCK_SIZE*i,BLOCK_SIZE,BLOCK_SIZE)))
                elif lines[i][j]=="f":
                    self.objects.append(Flag((BLOCK_SIZE*j,BLOCK_SIZE*i,BLOCK_SIZE,BLOCK_SIZE),part="bottom"))
                elif lines[i][j]=="F":
                    self.objects.append(Flag((BLOCK_SIZE*j,BLOCK_SIZE*i,BLOCK_SIZE,BLOCK_SIZE),part="top"))
 
        
    def Restart(self):
        print("restarted")
        self.__init__()
    def WinGame(self,other):
        print("ganhou o jogo")






