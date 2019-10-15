
import pygame
WIDTH=1280
HEIGHT=720



class Player:
    def __init__(self,charset=0,lenSprites=8,speed=5):
        self.sprites={}
        self.LoadSprites()
        self.InitCoord()
        self.speed=speed
        self.isJump=False
        self.right=False
        self.walkCount=0
        self.jumpCount=0
        self.stoped=True
        self.facing=1
    def InitCoord(self,x=10,y=10,width=32,height=32):
        self.x=x
        self.y=y
        self.widht=width
        self.height=height

    def LoadSprites(self):
        sub=[]
        for i in range(1,lenSprites+1):
            sub.append(pygame.image.load("R%i.png"%i))
        self.sprites["R"]=sub
        sub=[]

        for i in range(1,lenSprites+1):
            sub.append(pygame.image.load("L%i.png"%i))
        self.sprites["L"]=sub
    
    def KeyUpdate(self):
        keys=pygame.key.get_pressed()

        if keys[pygame.K_SPACE]:
            if self.left:


    def Draw(self,win):
        if self.walkCount>27:
            self.walkCount =0 
        if not (self.stoped):
            if self.left:
                win.blit(walkLeft[self.walkCount//3],(self.x,self.y))
                self.walkCount+=1
            else:
                win.blit(walkRight[self.walkCount//3],(self.x,self.y))
                self.walkCount+=1
        else:
            if self.right:
                win.blit(walkRight[0],(self.x,self.y))
            else:
                win.blit(walkLeft[0],(self.x,self.y))


class GameManager:
    def __init__(self):
        global WIDTH,HEIGHT
        pygame.init()
        self.win=pygame.display.set_mode(WIDHT,HEIGHT)
    
        self.bg=pygame.image.load('bg.jpg')

        clock = pygame.time.Clock()

        self.dinamicItens=[]
    

    def RedrawWindow(self):
        self.win.blit(self.bg,(0,0))
        for i in self.DinamicItes:
            i.Draw(win)
        pygame.display.update()

    def AddDinamic(self,dinamicObj):
        self.dinamicItens.append(dinamicObj)
    




