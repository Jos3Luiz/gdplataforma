#!/usr/bin/python3

import pygame
WIDTH=500
HEIGHT=480
IMG_ROOT="img/"
class Vector3d:
    def __init__(self,x=0,y=0,z=0):
        self.x=x
        self.y=y
        self.z=z
    def __add__(self,other):
        return Vector3d(self.x+other.x,self.y+other.y,self.z+other.z)
    def __sub__(self,other):
        return Vector3d(self.x-other.x,self.y-other.y,self.z-other.z)



class NPC:
    def __init__(self,charset=0,lenSprites=8,speed=5):
        self.sprites={}
        self.lenSprites=lenSprites
        self.LoadSprites()
        self.InitCoord()
        self.speed=speed
        self.isJump=False
        self.up=False
        self.right=True
        self.walkCount=0
        self.jumpCount=0
        self.stoped=True
        self.facing=1
        self.jumpHeight=0.5
    def InitCoord(self,x=300,y=410,width=32,height=32):
        self.transform=Vector3d(x,y)
        self.widht=width
        self.height=height
        
    def LoadSprites(self):
        self.walkRight=[]
        for i in range(1,self.lenSprites+1):
            self.walkRight.append(pygame.image.load("%sR%i.png"%(IMG_ROOT,i)))
    
        self.walkLeft=[]
        for i in range(1,self.lenSprites+1):
            self.walkLeft.append(pygame.image.load("%sL%i.png"%(IMG_ROOT,i)))
    
        self.sprite=self.walkLeft[0]
    def Update(self):
        
        return

    def Draw(self,win,globalVector):
        local=Vector3d(self.transform.x-globalVector.x+WIDTH//2,
                self.transform.y-globalVector.y+HEIGHT//2,0)
        win.blit(self.sprite,(local.x,local.y))



class Player(NPC):
    
   
    def Update(self):
        keys=pygame.key.get_pressed()

        if keys[pygame.K_LEFT]:# and self.transform.x > self.speed:
            self.transform.x-=self.speed
            self.left = True
            self.right=False
        elif keys[pygame.K_RIGHT]:# and self.transform.x < (WIDTH - self.speed):
            self.transform.x+=self.speed
            self.right=True
            self.left=False
        else:
            self.walkCount=0
        if not(self.isJump):
            if keys[pygame.K_SPACE]:
                print("PUAN")
                self.isJump=True
                self.walkCount=0
                self.jumpCount=10
        else:
            if self.jumpCount==-11:
                self.isJump=False
                self.jumpCount=0
            if self.jumpCount >=-10:
                if self.jumpCount>0:
                    self.transform.y -= self.jumpCount**2 *self.jumpHeight
                else:
                    self.transform.y += self.jumpCount**2 *self.jumpHeight
                self.jumpCount-=1
        

    def Draw(self,win,globalVector):
        if self.walkCount>27:
            self.walkCount =0 
        if not (self.stoped):
            if self.left:
                self.sprite=self.walkLeft[self.walkCount//3]
                self.walkCount+=1
            else:
                self.sprite=self.walkRight[self.walkCount//3]
                self.walkCount+=1
        else:
            if self.right:
                self.sprite=self.walkRight[0]
            else:
                self.sprite=self.walkLeft[0]
        NPC.Draw(self,win,globalVector)

class GameManager:
    def __init__(self):
        #global WIDTH,HEIGHT
        pygame.init()
        self.win=pygame.display.set_mode((WIDTH,HEIGHT))
    
        
        self.bg=pygame.image.load(IMG_ROOT+'bg.jpg')
        self.bg = pygame.transform.scale(self.bg,(2000,2000))

        self.clock = pygame.time.Clock()

        self.dinamicItens=[]
        self.globalvector=Vector3d(0,0,0)

    def RedrawWindow(self):
        self.win.fill((0,0,1))
        local=Vector3d(-self.globalVector.x+WIDTH//2,
                -1600-self.globalVector.y+HEIGHT//1,0)
        self.win.blit(self.bg,(local.x,local.y))
        for i in self.dinamicItens:
            i.Draw(self.win,self.globalVector)

        pygame.display.update()

    def AddDinamic(self,dinamicObj):
        self.dinamicItens.append(dinamicObj)
    

    def MainLoop(self,focus):
        run = True
        while run:
            self.globalVector=focus.transform
            #self.bg.scroll(-10,0)
            
            self.clock.tick(27)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False

            for obj in self.dinamicItens:
                obj.Update()

            self.RedrawWindow()
if __name__=="__main__":

    man = Player()
    npc = NPC()
    manager= GameManager()
    manager.AddDinamic(man)
    manager.AddDinamic(npc)
    manager.MainLoop(man)

