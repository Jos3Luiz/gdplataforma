import pygame
import math
import os
from  pygame.locals import *
import sys
import netcode

G_WIDTH=1280
G_HEIGHT=720
GRAVITY=pygame.Vector2(0,2)
GAME_CLOCK=30
BLOCK_SIZE=32
D_TIME=1/GAME_CLOCK
IS_MIRROR=0
IS_LOCAL=1
IS_ONLINE=2

MANAGER=None
HUD=None

GID=0

def CreateID():
    global GID
    GID+=1
    return GID 

def subTuple(t1,t2):
    return (t1[0]-t2[0],t1[1]-t2[1])


def OpenSprites(path,width,height):
    files = os.listdir(path)
    files.sort()
    if len(files)>100:
        print("this paste have more than 100 files on folder %s. Check for errors"%path)
        exit()
    for i in range (len(files)):
        img=pygame.image.load(path+"/"+files[i])
        scaled=pygame.transform.scale(img,(width,height))
        files[i]=scaled
    return files



class Entity(pygame.sprite.Sprite):
    def __init__(self,rect,path="",tags=[],color=pygame.Color("#DD00FF") ,netstate=IS_MIRROR,*groups):
        super().__init__(*groups)
        self.id=CreateID()
        self.netstate=netstate
        self.rect = rect 
        self.tags=tags
        self.isAlive=True
        self.online=[]
        

        if "dinamic" in self.tags:
            self.sprites=OpenSprites(path,32,32)
            self.sprites_len=len(self.sprites)
            self.image=self.sprites[0]
            self.count=0
        elif "color" in self.tags:
            self.image =  pygame.Surface((rect.width,rect.height))
            self.image.fill(color)
        elif path!="" and "static" in tags:
            img=pygame.image.load(path)
            width=rect.width
            heigh=rect.height
            self.image=pygame.transform.scale(img,(rect.width,rect.height))

        
    def post(self):
        
        return [self.rect.x,self.rect.y]

    def get(self,recived):
        self.rect.x=recived.pop(0)
        self.rect.y=recived.pop(0)



    def Update(self):
        if "dinamic" in self.tags:
            self.image=self.sprites[self.count%self.sprites_len]
            self.count+=1
            self.online=[self.count]



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
            

class FireBall(Entity):
    def __init__(self,rect,path="textura/FireBall/",netstate=IS_MIRROR,vel=0,*groups):
        self.vel=vel
        super().__init__(rect,path,tags=["dinamic"],netstate=netstate,*groups)
    def Update(self):

        self.rect.x+=self.vel
        Entity.Update(self)

    def Collide(self,other,xvel,yvel):
        self.isAlive=False
        self.Interact(other)
    def Interact(self,other):
        other.TirarVida(20)

    

class Coin(Entity):
    def __init__(self,rect,path="textura/coins/",*groups):
        super().__init__(rect,path,tags=["dinamic"],*groups)
    def Interact(self,other):
        if isinstance(other,Player):
            other.gold+=10
            self.isAlive=False
            print("collected")


class Lava(Entity):
    def __init__(self,rect,path="textura/lava/",*groups):
        super().__init__(rect,path,tags=["dinamic"],*groups)
    def Interact(self,other):
        other.TirarVida(10)

class Flag(Entity):
    def __init__(self,rect,path="",part="",*groups):
        if part=="top":
            super().__init__(rect,"textura/flag/",tags=["dinamic"],*groups)
        elif part=="bottom":
            super().__init__(rect,"textura/f1.png",tags=["static"],*groups)
    def Interact(self,other):
        if isinstance(other,Player):
            HUD.Update(["Vitoria!"])

class Platform(Entity):
    def __init__(self,rect,path,*groups):
        super().__init__(rect,path,tags=["static","collider"],*groups)

class End(Entity):
    def __init__(self,rect,*groups):
        super().__init__(rect,tags=["color","collider"],*groups)

class Hud:
    def __init__(self,size=20):
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
            MANAGER.win.blit(self.buffer[i], (0, i*self.size))



class NPC(Entity):
    def __init__(self,rect,path_run="inimigo1/andando/",path_jump="inimigo1/pulando",moveSpeed=5,max_jump=100,max_run=100,netstate=IS_MIRROR,*groups):
        Entity.__init__(self,rect,netstate=netstate)
        self.run=OpenSprites(path_run,width=rect.width,height=rect.height)
        #self.rect=rect
        self.is_jumping=True
        self.is_running=False
        self.is_left=False
        
        self.jump_count=0
        self.run_count=0
        self.len_run=len(self.run)
        self.max_jump=max_jump
        self.max_run=max_run
        self.speed=pygame.Vector2((0,0))
        self.jump_power=30
        self.moveSpeed=moveSpeed
        
        self.vida=100

    def post(self):
        return Entity.post(self)+[self.is_jumping,self.is_running,self.is_left,self.jump_count,self.run_count,self.vida]

    def get(self,recived):
        Entity.get(self,recived)
        self.is_jumping=recived.pop(0)
        self.is_running=recived.pop(0)
        self.is_left=recived.pop(0)
        self.jump_count=recived.pop(0)
        self.run_count=recived.pop(0)
        self.vida=recived.pop(0)

         
    def OflineUpdate(self):
        global MANAGER , HUD
        #print(MANAGER.win,HUD.str_list)
        plataforms=MANAGER.plataforms
        objects=MANAGER.objects

        self.image=self.run[self.run_count%self.len_run]
        if self.is_left:
            self.image = pygame.transform.flip(self.image, 1,0)
        

    def Update(self):
        global MANAGER , HUD
        #print(MANAGER.win,HUD.str_list)
        plataforms=MANAGER.plataforms
        objects=MANAGER.objects


        
        self.Move(self.GetInput())

        self.is_jumping=True
        if self.is_jumping==True:
             
            self.speed+=GRAVITY
            self.jump_count+=1
            if self.jump_count > self.max_jump:
                self.jump_count = 0
                self.jumping = False
                self.run_count=0
                                                                        

        if self.is_running:
            self.run_count+=1

        self.image=self.run[self.run_count%self.len_run]
        if self.is_left:
            self.image = pygame.transform.flip(self.image, 1,0)
        

        self.rect.left+=self.speed.x
        self.CheckCollision(self.speed.x,0,plataforms)

        if self.is_jumping:
            self.rect.bottom+=self.speed.y

        self.CheckCollision(0,self.speed.y,objects)
        self.CheckInteractions(0,self.speed.y,plataforms)

        if self.rect.y > 1000:
            self.TirarVida(self.vida*100)

    def Move(self,keyboard):
        if keyboard[pygame.K_UP]:
            if not self.is_jumping:
                self.speed.y-=self.jump_power
                self.is_jumping=True
        elif keyboard[pygame.K_DOWN]:
            if self.is_jumping:
                self.speed.y+=GRAVITY.y *2

        if keyboard[pygame.K_LEFT]:
            self.speed.x = -self.moveSpeed
            self.is_running=True
            self.is_left=True
                                                        
                                                        
        elif keyboard[pygame.K_RIGHT]:
            self.speed.x = self.moveSpeed
            self.is_running=True
            self.is_left=False
        else:
            self.speed.x=0
            self.is_running=False

    def TirarVida(self,dano):
        self.vida-=dano
        if self.vida<0:
            self.isAlive=False

    def CheckInteractions(self,xvel,yvel,objects):
        for o in objects:
            if pygame.sprite.collide_rect(self,o):
                o.Collide(self,xvel,yvel)
                            

    def CheckCollision(self,xvel,yvel,obstacles):
        for o in obstacles:
            if pygame.sprite.collide_rect(self,o):
                o.Collide(self,xvel,yvel)
                            


    def GetInput(self):
        keyboard=pygame.key.get_pressed()
        return keyboard

 
class Player(NPC):
    def __init__(self,rect, path_run="player/sans/right",path_jump="player/jump",moveSpeed=5,max_jump=100,max_run=100,netstate=IS_MIRROR,*groups):
        self.gold=0
        self.timer=0
        self.reloadTime=1
        NPC.__init__(self,rect, path_run,path_jump,moveSpeed,max_jump,max_run,netstate=netstate,*groups)

    def Update(self):
        global MANAGER, HUD
        
        HUD.Update(["Vida: %i"%self.vida , "Gold: %i"%self.gold])
        NPC.Update(self)

        if self.timer<0:
            self.CheckAttack()
        else:
            self.timer-=D_TIME

    def OflineUpdate(self):
        global MANAGER, HUD
        
        NPC.OflineUpdate(self)


    def CheckAttack(self):
        keyboard=self.GetInput()
        if keyboard[pygame.K_e]:
            if self.is_left:
                vel=-10
                pos=pygame.Rect(self.rect.x-32,self.rect.y,32,32)
            else:
                vel=10
                pos=pygame.Rect(self.rect.x+32,self.rect.y,32,32)

            fire=FireBall(rect=pos,vel=vel,netstate=IS_LOCAL)
            MANAGER.objects.append(fire)
            MANAGER.isLocalTemp.append(fire)
            self.timer=self.reloadTime


    def TirarVida(self,dano):
        NPC.TirarVida(self,dano)
        if not self.isAlive:
            MANAGER.restart()


class Enemy(NPC):
    def __init__(self,rect,path_run="inimigo1/andando/",path_jump="inimigo1/pulando",moveSpeed=3,max_jump=100,max_run=100,netstate=IS_MIRROR,*groups):
        NPC.__init__(self,rect,path_run,path_jump,moveSpeed,max_jump,max_run,netstate=netstate,*groups)
        self.aware_distance=100000
        
        self.dano=1
        self.hasTarget=False
        self.target=None  


    def Update(self):
        self.players=[]
        for i in MANAGER.objects:
            if isinstance(i,Player):
                self.players.append(i)
        NPC.Update(self)
        
        for i in self.players:
            if pygame.sprite.collide_rect(self,i):
                i.TirarVida(self.dano)

    def GetInput(self):

        
        if self.target!=None:
            if self.GetDistance(self.target) > self.aware_distance:
                self.hasTarget=False

        near=9999999
        if not self.hasTarget:
            for i in self.players:
                distance= self.GetDistance(i) 
                if (distance < near) and (distance < self.aware_distance):
                    near=distance
                    self.target=i
                    self.hasTarget=True

        keyboard={pygame.K_RIGHT: False , pygame.K_LEFT: False ,pygame.K_DOWN : False , pygame.K_UP: False}
        if self.hasTarget:
            direction=self.target.rect.x-self.rect.x,self.target.rect.y-self.rect.y
            if  direction[0]>0:
                keyboard[pygame.K_RIGHT]=True
            elif direction[0]<0:
                keyboard[pygame.K_LEFT]=True

            if  direction[1]>32:
                keyboard[pygame.K_DOWN]=True
            elif direction[1]<-32:
                keyboard[pygame.K_UP]=True
        return keyboard

                        
class Camera:
    def __init__(self,win,objects,plataforms,focus,bg_path="bg.bmp"):
        self.win=win
        self.focus=focus
        self.bg=pygame.image.load(bg_path).convert()
        self.limiteR=0
        self.limiteL=9999
        self.lastPos=0
        self.offset=pygame.Vector2(G_WIDTH/2,0)
    def DrawFrame(self,objects,plataforms):
        self.win.blit(self.bg,[ 0,0])
        allobjects=objects+plataforms
        for i in allobjects:
            xpos=i.rect.x-self.focus.x+self.offset.x

            ypos=i.rect.top

            self.win.blit(i.image,(xpos,ypos))
        HUD.Draw() 

                 
class MainGame:
    def __init__(self,title="jogo1",width=G_WIDTH,height=G_HEIGHT,isServer=True,addr="127.0.0.1"):
        global MANAGER , HUD
        
        self.isServer=isServer


        pygame.init()
        
        self.hud=Hud()


        HUD=self.hud
        MANAGER=self

        self.win = pygame.display.set_mode((width,height))

        
        self.size = (width, height)

        pygame.display.set_caption(title)
        self.clock=pygame.time.Clock() 


        
        self.objects=[]

        self.plataforms=[]
        self.readMap2("maps/map2.txt")
        
        
        self.player=Player(pygame.Rect(600,0,32,32),netstate=IS_LOCAL)
        self.player2=Player(pygame.Rect(600,0,32,32),netstate=IS_ONLINE)
        if self.isServer:
            self.inimigo1=Enemy(pygame.Rect(800,0,32,32),netstate=IS_LOCAL)
        else:
            self.inimigo1=Enemy(pygame.Rect(800,0,32,32),netstate=IS_ONLINE)
        
        self.objects.append(self.player)
        self.objects.append(self.player2)
        self.objects.append(self.inimigo1)

        self.cam=Camera(self.win,self.objects,self.plataforms,focus=self.player.rect)



        self.hud=Hud()
        

        self.isOnline=[]
        self.isLocal=[]
        self.isOnlineTemp=[]
        self.isLocalTemp=[]
        for i in self.objects:
            if i.netstate==IS_LOCAL:
                self.isLocal.append(i)
            if i.netstate==IS_ONLINE:
                self.isOnline.append(i)

        if self.isServer:
            self.netManager=netcode.NetManagerServer(self.isLocal,self.isOnline)
        else:
            self.netManager=netcode.NetManagerClient(self.isLocal,self.isOnline)


       

        self.mainLoop()

    def mainLoop(self):
        global GAME_CLOCK
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


                                        
            self.cam.DrawFrame(self.objects,self.plataforms)     
            #self.hud.Draw() 
            pygame.display.flip()
            self.clock.tick(GAME_CLOCK)
            
    def readMap2(self,mapPath):
        with open(mapPath,"r") as f:
            lines=f.read().split("\n")

        rect_matrix=[]
        for  i in range(len(lines)):
            for j in range(len(lines[i])):
                #print(lines[i][j],end="")
                if lines[i][j]=="G":
                    self.plataforms.append(Platform(pygame.Rect(BLOCK_SIZE*j,BLOCK_SIZE*i,BLOCK_SIZE,BLOCK_SIZE),"textura/grass.png"))
                elif lines[i][j]=="M":
                    self.plataforms.append(Platform(pygame.Rect(BLOCK_SIZE*j,BLOCK_SIZE*i,BLOCK_SIZE,BLOCK_SIZE),"textura/marble.png"))
                elif lines[i][j]=="C":
                    self.objects.append(Coin(pygame.Rect(BLOCK_SIZE*j,BLOCK_SIZE*i,BLOCK_SIZE,BLOCK_SIZE)))
                elif lines[i][j]=="L":
                    self.objects.append(Lava(pygame.Rect(BLOCK_SIZE*j,BLOCK_SIZE*i,BLOCK_SIZE,BLOCK_SIZE)))
                elif lines[i][j]=="f":
                    self.objects.append(Flag(pygame.Rect(BLOCK_SIZE*j,BLOCK_SIZE*i,BLOCK_SIZE,BLOCK_SIZE),part="bottom"))
                elif lines[i][j]=="F":
                    self.objects.append(Flag(pygame.Rect(BLOCK_SIZE*j,BLOCK_SIZE*i,BLOCK_SIZE,BLOCK_SIZE),part="top"))
                                                                        
        #for i in rect_matrix:
                                 
        
    def restart(self):
        print("restarted")
        self.__init__()
    def WinGame(self,other):
        print("ganhou o jogo")






