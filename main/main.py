import pygame
import math
import os


G_WIDTH=800
G_HEIGHT=600
GRAVITY=pygame.Vector2(0,2)



def OpenSprites(path,width,height):
        files = os.listdir(path)
        if len(files)>100:
                print("this paste have more than 100 files. Check for errors")
                exit()
        ret= [pygame.image.load(path+"/"+x) for x in files]
        #print(ret[0])
        for i in range(len(ret)):
                ret[i]=pygame.transform.scale(ret[i],(width,height))
        return ret


class Entity(pygame.sprite.Sprite):
    def __init__(self, color, pos,width=32,height=32, *groups):
        super().__init__(*groups)
        self.image =  pygame.Surface((width,height))
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft=pos)
        self.pos=pos
    def Update(self,win,plataforms):
        
        win.blit(self.image,self.pos)
        #print("plataform pos=",self.pos)
class Player(Entity):
        def __init__(self,transform=pygame.Vector2((0,0)),
                path_run="player/sans/right",path_jump="player/jump",
                width=32,height=32,max_jump=100,max_run=100,*groups):

                super().__init__(pygame.Color("#0000FF"), transform)
                self.run=OpenSprites(path_run,width,height)
                #self.jump=OpenSprites(path_jump)
                self.transform=transform
                self.width=width
                self.height=height
                self.is_jumping=False
                self.is_running=False
                self.sprite=None
                self.jump_count=0
                self.run_count=0
                #self.len_jump=len(self.jump)
                self.len_run=len(self.run)
                self.max_jump=max_jump
                self.max_run=max_run
                self.speed=pygame.Vector2((0,0))
                self.jump_power=10
                self.moveSpeed=4



        def Update(self,win,plataforms):
                self.GetInput()
                if self.is_jumping==True:
                        #self.sprite=(self.jump[self.jump_count//self.len_jump],self.transform)
                        self.speed+=GRAVITY
                        self.jump_count+=1
                        if self.jump_count > self.max_jump:
                                self.jump_count = 0
                                self.jumping = False
                                self.run_count=0
                                

                elif self.is_running:
                        self.run_count+=1
                        #
                #print("pos=1",self.transform)        
                self.sprite=self.run[self.run_count%self.len_run]


                self.collideX(plataforms)
                
                self.is_jumping=True
                self.collideY(plataforms)
                self.transform+=self.speed
                self.collideY(plataforms)
                self.rect.top=self.transform.y
                self.rect.left=self.transform.x
                #print("win=",win,"sprite=",self.sprite) 
                #print(self.speed,self.is_jumping)
                #self.transform=pygame.Vector2(10,-20)
                win.blit(self.sprite,self.transform)
        def collideX(self,obstacles):
                for o in obstacles:
                        if pygame.sprite.collide_rect(self,o):
                                if self.speed.x >0:
                                        self.rect.right = o.rect.left
                                elif self.speed.x < 0 :
                                        self.rect.left = o.rect.right
        def collideY(self,obstacles):
                for o in obstacles:
                        if pygame.sprite.collide_rect(self,o):
                                if self.speed.y > 0 :
                                        print("hity grnd",self.rect,o.rect)
                                        self.rect.bottom = o.rect.top
                                        self.is_jumping=False
                                        self.speed.y=0
                                if self.speed.y <0:
                                        self.rect.top = o.rect.bottom


        def GetInput(self):
                keyboard=pygame.key.get_pressed()
                
                if keyboard[pygame.K_UP]:
                        if not self.is_jumping:
                                self.speed.y-=self.jump_power
                                self.is_jumping=True

                elif keyboard[pygame.K_LEFT]:
                        print("pressed ")
                        self.speed.x = -self.moveSpeed
                        self.is_running=True
                elif keyboard[pygame.K_RIGHT]:
                        self.speed.x = self.moveSpeed
                        self.is_running=True
                #if keyboard[K_RIGHT]:
                else:
                        self.speed.x=0
                        self.is_running=False

class Platform(Entity):
    def __init__(self, pos,width,height, *groups):
        super().__init__(pygame.Color("#00DDFF"), pos,width,height, *groups)
        #self.sprite=
    #def









class MainGame:
        def __init__(self,bg_path="bg.bmp",title="jogo1",width=G_WIDTH,height=G_HEIGHT):
                pygame.init()

                self.clock_tick_rate=5
                self.size = (width, height)

                self.win = pygame.display.set_mode((width,height))
                pygame.display.set_caption(title)
                self.clock=pygame.time.Clock() 


                self.bg=pygame.image.load(bg_path).convert()
                p1=Platform(pygame.Vector2(20,400),width=200,height=30)
                self.plataforms=[p1]
                
                
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
                        


