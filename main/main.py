import pygame
import math
import os


G_WIDTH=1200
G_HEIGHT=600
GRAVITY=pygame.Vector2(0,2)
GAME_CLOCK=30
BLOCK_SIZE=20
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
                                                rect_matrix.append(Platform(pygame.Vector2(begin,BLOCK_SIZE*i),width=width*BLOCK_SIZE,height=BLOCK_SIZE))
                                        elif block_type=="B":
                                                rect_matrix.append(End(pygame.Vector2(begin,BLOCK_SIZE*i),width=width*BLOCK_SIZE,height=BLOCK_SIZE))
                                        width=1
                                started=False
                        
        for i in rect_matrix:
                print(i.rect)
        return rect_matrix
                            
def OpenSprites(path,width,height):
        files = os.listdir(path)
        if len(files)>100:
                print("this paste have more than 100 files on folder %s. Check for errors"%path)
                exit()
        for i in range (len(files)):
                img=pygame.image.load(path+"/"+files[i])
                scaled=pygame.transform.scale(img,(width,height))
                files[i]=scaled
                
        return files


class Entity(pygame.sprite.Sprite):
        def __init__(self, color, pos,width=32,height=32, *groups):
                super().__init__(*groups)
                self.image =  pygame.Surface((width,height))
                self.image.fill(color)
                self.rect = self.image.get_rect(topleft=pos)
                self.pos=pos
        def Update(self,win,plataforms):
                win.blit(self.image,self.pos)


class Player(pygame.sprite.Sprite):
        def __init__(self,rect=pygame.Rect(0,0,32,32),
                path_run="player/sans/right",path_jump="player/jump",moveSpeed=5,max_jump=100,max_run=100,*groups):

                self.run=OpenSprites(path_run,width=rect.width,height=rect.height)
                self.rect=rect
                self.is_jumping=True
                self.is_running=False
                self.is_left=False
                self.sprite=None
                self.jump_count=0
                self.run_count=0
                self.len_run=len(self.run)
                self.max_jump=max_jump
                self.max_run=max_run
                self.speed=pygame.Vector2((0,0))
                self.jump_power=30
                self.moveSpeed=moveSpeed



        def Update(self,win,plataforms):

                
                
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

                self.sprite=self.run[self.run_count%self.len_run]
                if self.is_left:
                        self.sprite = pygame.transform.flip(self.sprite, 1,0)
                

                self.rect.left+=self.speed.x
                self.collide(self.speed.x,0,plataforms)

                if self.is_jumping:
                        self.rect.bottom+=self.speed.y
                self.collide(0,self.speed.y,plataforms)
                
                win.blit(self.sprite,self.rect.topleft)

        def collide(self,xvel,yvel,obstacles):
                for o in obstacles:
                        if pygame.sprite.collide_rect(self,o):
                                collidad=True
                                if xvel >0:
                                        self.rect.right= o.rect.left
                                elif xvel < 0 :
                                        self.rect.left = o.rect.right
                                elif yvel > 0 :
                                        self.rect.bottom = o.rect.top
                                        self.is_jumping=False
                                        self.speed.y=0
                                elif yvel <0:
                                        self.rect.top = o.rect.bottom




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

class Platform(Entity):
        def __init__(self, pos,width,height, *groups):
                super().__init__(pygame.Color("#FF00FF"), pos,width,height, *groups)

class End(Entity):
        def __init__(self, pos,width,height, *groups):
                super().__init__(pygame.Color("#0022FF"), pos,width,height, *groups)
                
class MainGame:
        def __init__(self,bg_path="bg.bmp",title="jogo1",width=G_WIDTH,height=G_HEIGHT):
                pygame.init()

                self.clock_tick_rate= GAME_CLOCK
                self.size = (width, height)

                self.win = pygame.display.set_mode((width,height))
                pygame.display.set_caption(title)
                self.clock=pygame.time.Clock() 


                self.bg=pygame.image.load(bg_path).convert()
   
                self.plataforms=readMap("maps/map1.txt")
                
                
                self.player=Player()
                
                self.mainLoop()
        def mainLoop(self):
                is_running=True
                while is_running == True:
                        self.win.blit(self.bg,[ 0,0])
                        for e in pygame.event.get():
                                if e.type == pygame.QUIT: 
                                        return
                        self.player.Update(self.win,self.plataforms)
                        for i in self.plataforms:
                                i.Update(self.win,self.plataforms)

                        
                        pygame.display.flip()
                        self.clock.tick(self.clock_tick_rate)
    
                
                
                
                        
if __name__ == "__main__":
           j=MainGame()
                        


