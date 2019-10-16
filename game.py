#!/usr/bin/python3

import pygame
WIDTH=500
HEIGHT=480
IMG_ROOT="img/"


class Player:
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
    def InitCoord(self,x=200,y=410,width=32,height=32):
        self.x=x
        self.y=y
        self.widht=width
        self.height=height
        
    def LoadSprites(self):
        self.walkRight=[]
        for i in range(1,self.lenSprites+1):
            self.walkRight.append(pygame.image.load("%sR%i.png"%(IMG_ROOT,i)))
    
        self.walkLeft=[]
        for i in range(1,self.lenSprites+1):
            self.walkLeft.append(pygame.image.load("%sL%i.png"%(IMG_ROOT,i)))
    
    def Update(self):
        keys=pygame.key.get_pressed()

        if keys[pygame.K_LEFT] and self.x > self.speed:
            self.x-=self.speed
            self.left = True
            self.right=False
        elif keys[pygame.K_RIGHT] and self.x < (WIDTH - self.speed):
            self.x+=self.speed
            self.right=True
            self.left=False
        else:
            self.walkCount=0
        if not(self.isJump):
            if keys[pygame.K_SPACE]:
                print("PUAN")
                self.isJump=True
                self.up=True
                self.walkCount=0
                self.jumpCount=0
        else:
            if (self.jumpCount < 10) and self.up:
                self.y -= (self.jumpCount **2) *0.5 
                self.jumpCount+=1
                print (self.jumpCount)
            if self.jumpCount ==10:
                self.up=False
                self.jumpCount=0
            if self.jumpCount<10 and not(self.up):
                self.y += ((10-self.jumpCount) **2) *0.5 
                self.jumpCount=+1

            print(self.y)
        

    def Draw(self,win):
        if self.walkCount>27:
            self.walkCount =0 
        if not (self.stoped):
            if self.left:
                win.blit(self.walkLeft[self.walkCount//3],(self.x,self.y))
                self.walkCount+=1
            else:
                win.blit(self.walkRight[self.walkCount//3],(self.x,self.y))
                self.walkCount+=1
        else:
            if self.right:
                win.blit(self.walkRight[0],(self.x,self.y))
            else:
                win.blit(self.walkLeft[0],(self.x,self.y))


class GameManager:
    def __init__(self):
        #global WIDTH,HEIGHT
        pygame.init()
        self.win=pygame.display.set_mode((WIDTH,HEIGHT))
    
        self.bg=pygame.image.load(IMG_ROOT+'bg.jpg')

        self.clock = pygame.time.Clock()

        self.dinamicItens=[]

    def RedrawWindow(self):
        self.win.blit(self.bg,(0,0))
        for i in self.dinamicItens:
            i.Draw(self.win)
        pygame.display.update()

    def AddDinamic(self,dinamicObj):
        self.dinamicItens.append(dinamicObj)
    

    def MainLoop(self):
        run = True
        while run:
            self.clock.tick(27)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False

            for obj in self.dinamicItens:
                obj.Update()

            self.RedrawWindow()
if __name__=="__main__":

    man = Player()
    manager= GameManager()
    manager.AddDinamic(man)
    manager.MainLoop()

