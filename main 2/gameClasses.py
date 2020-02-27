import pygame
import game
from gameConstants import *
from auxiliares import *

class Entity(pygame.sprite.Sprite):
    def __init__(self,rect,path="",tags=[],color="#DD00FF",netstate=IS_MIRROR):
        super().__init__()
        print(isinstance(game.GameManager,object))
        self.manager=game.game.GameManager.instance()
        self.id=self.manager.createID()
        self.netstate=netstate

        x,y,w,h=rect
        self.rect = pygame.Rect(x,y,w,h) 
        
        self.tags=tags
        self.isAlive=True
        self.online=[]
        

        if "dinamic" in self.tags:
            self.sprites=OpenSprites(path,32,32)
            self.sprites_len=len(self.sprites)
            self.image=self.sprites[0]
            self.count=0

        elif "color" in self.tags:
            self.image =  pygame.Surface((self.rect.width,self.rect.height))
            self.image.fill(pygame.Color(color))

        elif path!="" and "static" in tags:
            img=pygame.image.load(path)
            width=self.rect.width
            heigh=self.rect.height
            self.image=pygame.transform.scale(img,(self.rect.width,self.rect.height))

        
    def post(self):
        return [self.rect.x,self.rect.y]

    def get(self,recived):
        self.rect.x=recived.pop(0)
        self.rect.y=recived.pop(0)



    def update(self):
        if "dinamic" in self.tags:
            self.image=self.sprites[self.count%self.sprites_len]
            self.count+=1
            self.online=[self.count]



    def collide(self,other,xvel,yvel):
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
            self.interact(other)

    def getDistance(self,other):
        return (abs(self.rect.x - other.rect.x)**2 + abs(self.rect.y - other.rect.y)**2)
            

class FireBall(Entity):
    def __init__(self,rect,path="textura/FireBall/",netstate=IS_MIRROR,vel=0):
        self.vel=vel
        super().__init__(rect,path,tags=["dinamic"],netstate=netstate)
    
    def update(self):
        self.rect.x+=self.vel
        Entity.update(self)

    def collide(self,other,xvel,yvel):
        self.isAlive=False
        self.interact(other)
    
    def interact(self,other):
        other.tirarVida(20)

    

class Coin(Entity):
    def __init__(self,rect,path="textura/coins/"):
        super().__init__( rect,path,tags=["dinamic"])
    
    def interact(self,other):
        if isinstance(other,Player):
            other.gold+=10
            self.isAlive=False
            print("collected")


class Lava(Entity):
    def __init__(self,rect,path="textura/lava/"):
        super().__init__(rect,path,tags=["dinamic"])
    
    def interact(self,other):
        other.tirarVida(10)

class Flag(Entity):
    def __init__(self,rect,path="",part=""):
        if part=="top":
            super().__init__(rect,"textura/flag/",tags=["dinamic"])
        elif part=="bottom":
            super().__init__(rect,"textura/f1.png",tags=["static"])

    def interact(self,other):
        if isinstance(other,Player):
            self.manager.hud.update(["Vitoria!"])

class Platform(Entity):
    def __init__(self,rect,path):
        super().__init__(rect,path,tags=["static","collider"])

class End(Entity):
    def __init__(self,rect):
        super().__init__(rect,tags=["color","collider"])




class NPC(Entity):
    def __init__(self,rect,path_run="inimigo1/andando/",path_jump="inimigo1/pulando",moveSpeed=5,max_jump=100,max_run=100,netstate=IS_MIRROR,gravity=2):
        Entity.__init__(self,rect,netstate=netstate)
        self.run=OpenSprites(path_run,width=self.rect.width,height=self.rect.height)
        
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
        self.gravity=gravity
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

         
    def oflineUpdate(self):
        #print(MANAGER.win,HUD.str_list)
        plataforms=self.manager.plataforms
        objects=self.manager.objects

        self.image=self.run[self.run_count%self.len_run]
        if self.is_left:
            self.image = pygame.transform.flip(self.image, 1,0)
        

    def update(self):

        plataforms=self.manager.plataforms
        objects=self.manager.objects
        
        self.move(self.getInput())

        self.is_jumping=True
        if self.is_jumping==True:
             
            self.speed.y+=self.gravity
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
        self.checkCollision(self.speed.x,0,plataforms)

        if self.is_jumping:
            self.rect.bottom+=self.speed.y

        self.checkCollision(0,self.speed.y,objects)
        self.checkInteractions(0,self.speed.y,plataforms)

        if self.rect.y > 1000:
            self.tirarVida(self.vida*100)

    def move(self,keyboard):
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

    def tirarVida(self,dano):
        self.vida-=dano
        if self.vida<0:
            self.isAlive=False

    def checkInteractions(self,xvel,yvel,objects):
        for o in objects.values():
            if pygame.sprite.collide_rect(self,o):
                o.collide(self,xvel,yvel)
                            

    def checkCollision(self,xvel,yvel,objectsdict):

        for o in objectsdict.values():
            if pygame.sprite.collide_rect(self,o):
                o.collide(self,xvel,yvel)
                            


    def getInput(self):
        keyboard=pygame.key.get_pressed()
        return keyboard

 
class Player(NPC):
    def __init__(self,rect, path_run="player/sans/right",path_jump="player/jump",moveSpeed=5,max_jump=100,max_run=100,netstate=IS_MIRROR):
        self.gold=0
        self.timer=0
        self.reloadTime=1
        self.manager=game.GameManager.instance()
        NPC.__init__(self,rect, path_run,path_jump,moveSpeed,max_jump,max_run,netstate=netstate)

    def update(self):
     
        
        self.manager.hud.update(["Vida: %i"%self.vida , "Gold: %i"%self.gold])
        NPC.update(self)

        if self.timer<0:
            self.checkAttack()
        else:
            self.timer-=D_TIME

    def oflineUpdate(self):
        
        NPC.oflineUpdate(self)


    def checkAttack(self):
        keyboard=self.getInput()
        if keyboard[pygame.K_e]:
            if self.is_left:
                vel=-10
                pos=pygame.Rect(self.rect.x-32,self.rect.y,32,32)
            else:
                vel=10
                pos=pygame.Rect(self.rect.x+32,self.rect.y,32,32)

            fire=FireBall(rect=pos,vel=vel,netstate=IS_LOCAL)
            self.manager.objects.append(fire)
            #self.manager.isLocalTemp.append(fire)
            self.timer=self.reloadTime


    def tirarVida(self,dano):
        NPC.tirarVida(self,dano)
        if not self.isAlive:
            self.manager.restart()


class Enemy(NPC):
    def __init__(self,rect,path_run="inimigo1/andando/",path_jump="inimigo1/pulando",moveSpeed=3,max_jump=100,max_run=100,netstate=IS_MIRROR):
        NPC.__init__(self,rect,path_run,path_jump,moveSpeed,max_jump,max_run,netstate=netstate)
        self.aware_distance=100000
        
        self.dano=1
        self.hasTarget=False
        self.target=None  


    def update(self):
        self.players=[]
        for i in self.manager.objects:
            if isinstance(i,Player):
                self.players.append(i)
        NPC.update(self)
        
        for i in self.players:
            if pygame.sprite.collide_rect(self,i):
                i.tirarVida(self.dano)

    def getInput(self):

        
        if self.target!=None:
            if self.getDistance(self.target) > self.aware_distance:
                self.hasTarget=False

        near=9999999
        if not self.hasTarget:
            for i in self.players:
                distance= self.getDistance(i) 
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
