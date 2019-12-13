import pygame
import math
import os


G_WIDTH=1200
G_HEIGHT=600
GRAVITY=pygame.Vector2(0,2)
GAME_CLOCK=30
BLOCK_SIZE=32
def readMap(mapPath):
        with open(mapPath,"r") as f:
                lines=f.read().split("\n")

        rect_matrix=[]
        for  i in range(len(lines)):
                
                width=1
                started=False
                block_type=0
                print(len(lines[i]))
                for j in range(len(lines[i])):
                        print(lines[i][j],end="")
                        if lines[i][j]=="A":
                                if started:
                                        width+=1
                                else:
                                        begin=j*BLOCK_SIZE
                                        started=True
                                        block_type="A"
                        if lines[i][j]=="B":
                                if started:
                                        width+=1
                                else:
                                        begin=j*BLOCK_SIZE
                                        started=True
                                        block_type="B"
                        if lines[i][j]==" ":
                                if started:
                                        if block_type=="A":
                                                rect_matrix.append(Platform(pygame.Rect(begin,BLOCK_SIZE*i,width*BLOCK_SIZE,BLOCK_SIZE)))
                                        elif block_type=="B":
                                                rect_matrix.append(Platform(pygame.Rect(begin,BLOCK_SIZE*i,width*BLOCK_SIZE,BLOCK_SIZE)))
                                        width=1
                                started=False
                        
        for i in rect_matrix:
                print(i.rect)
        return rect_matrix
                            



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
        def __init__(self,rect,path="",tags=[],color=pygame.Color("#DD00FF") ,*groups):
            super().__init__(*groups)
            self.rect = rect 
            self.tags=tags
            self.isAlive=True
            
        
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
                

        

        def Update(self,manager):
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
            
            if "dinamic" in self.tags:
                self.Interact(other)
            
        #def Interact(self,other):
        #    print("interacted w ",other)
        #    return                
        

class Coin(Entity):
    def __init__(self,rect,path="textura/coins/",*groups):
        super().__init__(rect,path,tags=["dinamic"],*groups)
    def Interact(self,other):
        other.gold+=10
        self.isAlive=False
        print("collected")

class Lava(Entity):
    def __init__(self,rect,path="textura/lava/",*groups):
        super().__init__(rect,path,tags=["dinamic"],*groups)
    def Interact(self,other):
        other.TirarVida(10)


class Platform(Entity):
    def __init__(self,rect,path,*groups):
        super().__init__(rect,path,tags=["static","collider"],*groups)

class End(Entity):
    def __init__(self,rect,*groups):
        super().__init__(rect,tags=["color","collider"],*groups)


class Player(Entity):
        def __init__(self,rect,
                path_run="player/sans/right",path_jump="player/jump",moveSpeed=5,max_jump=100,max_run=100,*groups):
                Entity.__init__(self,rect)
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
                self.gold=0
                self.vida=100



        def Update(self,manager):

                plataforms=manager.plataforms
                objects=manager.objects
                self.GetInput()
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
                #print("drawing")
                #self.rect=pygame.Rect(110,110,32,32)
                #win.blit(self.image,self.rect.topleft)
                
                self.CheckInteractions(0,self.speed.y,plataforms)
        
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
                
                if keyboard[pygame.K_UP]:
                        if not self.is_jumping:
                                self.speed.y-=self.jump_power
                                self.is_jumping=True

                elif keyboard[pygame.K_LEFT]:
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






                
class MainGame:
        def __init__(self,title="jogo1",width=G_WIDTH,height=G_HEIGHT):
                pygame.init()
                beginPlayer=pygame.Rect(600,0,32,32)

                self.clock_tick_rate= GAME_CLOCK
                self.size = (width, height)

                self.win = pygame.display.set_mode((width,height))
                pygame.display.set_caption(title)
                self.clock=pygame.time.Clock() 


                
                self.objects=[]
                self.plataforms=[]
                self.readMap2("maps/map2.txt")
                
                
                self.player=Player(rect=beginPlayer)
                
                self.objects.append(self.player)
                self.cam=Camera(self.win,self.objects,self.plataforms,focus=self.player.rect)
                self.mainLoop()
        def mainLoop(self):
                is_running=True
                while is_running == True:
                        
                        for e in pygame.event.get():
                                if e.type == pygame.QUIT: 
                                        return


                        
                        for i in self.objects:
                            if i.isAlive==False:
                                self.objects.remove(i)
                                if i==self.player:
                                    self.restart()
                            else:
                                i.Update(self)
                        
                        self.cam.DrawFrame(self.objects,self.plataforms)     
                                  
                        pygame.display.flip()
                        self.clock.tick(self.clock_tick_rate)
        def readMap2(self,mapPath):
            with open(mapPath,"r") as f:
                    lines=f.read().split("\n")

            rect_matrix=[]
            for  i in range(len(lines)):
                    for j in range(len(lines[i])):
                            print(lines[i][j],end="")
                            if lines[i][j]=="G":
                                    self.plataforms.append(Platform(pygame.Rect(BLOCK_SIZE*j,BLOCK_SIZE*i,BLOCK_SIZE,BLOCK_SIZE),"textura/grass.png"))
                            elif lines[i][j]=="M":
                                    self.plataforms.append(Platform(pygame.Rect(BLOCK_SIZE*j,BLOCK_SIZE*i,BLOCK_SIZE,BLOCK_SIZE),"textura/marble.png"))
                            elif lines[i][j]=="C":
                                    self.objects.append(Coin(pygame.Rect(BLOCK_SIZE*j,BLOCK_SIZE*i,BLOCK_SIZE,BLOCK_SIZE)))
                            elif lines[i][j]=="L":
                                    self.objects.append(Lava(pygame.Rect(BLOCK_SIZE*j,BLOCK_SIZE*i,BLOCK_SIZE,BLOCK_SIZE)))
                            
            for i in rect_matrix:
                    print(i.rect)
            
        def restart(self):
            print("restarted")
            self.__init__()
                
                
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
        #for i in plataforms:
        #    self.win.blit(i.image,(i.rect.left-self.focus.left+G_WIDTH/2,i.rect.top))


def subTuple(t1,t2):
    return (t1[0]-t2[0],t1[1]-t2[1])


if __name__ == "__main__":
           j=MainGame()
                        

