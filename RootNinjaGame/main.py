import math
from random import randint

from pygame.locals import *
import pygame
import sys
from pygame.locals import *

# import SpriteSheet
from pygame.tests.test_utils import fixture_path

pygame.init()

# Constants
windowWidth = 500
windowHeight = 500

# Surface
factor = 5
DISPLAYSURF = pygame.display.set_mode((windowWidth, windowHeight), pygame.RESIZABLE)
surfaceRect = DISPLAYSURF.get_rect()
pygame.display.set_caption('Root Ninja')

# Mouse variables
mouseX, mouseY = None, None
cursorSpeed = 0, 200
MINBONUSSPEED = 100  # When the mouse moves faster than this speed, the fruit can give bonuses
MINSLICESPEED = 100  # When the mouse moves faster than this speed, a fruit can be sliced
comboBonusNum = 0

# Fonts
# openingFONT = pygame.font.Font('arial.ttf', 32)

# Time
FPS = 160
FPSCLOCK = pygame.time.Clock()
countdownTimer = 100, 000  # for the timed game mode

# Colors
BGCOLOR = (51, 153, 51)

WATERMELON = (6, 165, 67)

RED = (255, 0, 0)
ORANGE = (255, 127, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
PURPLE = (75, 0, 130)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREY = (128, 128, 128)

# Global Variables


openScreenRects = []  # stores rectangles of the opening screen
gameMode = None  # when is gameMode is none, start screen appears
gameScreenRect = None

resizeFactor = 1

rootGroup = pygame.sprite.Group()

# CLASSES

class Fruit(pygame.sprite.Sprite):
   def __init__(self, images, startPos, endPos):
       pygame.sprite.Sprite.__init__(self)
       global resizeFactor

       self.images = images  # the fruit images, an array with animation images in order, last image is explode img
       self.image = images[0]  # self.image is from the Sprite class
       self.imgIndex = 0
       self.rect = self.image.get_rect()  # from the Sprite class
       self.startXPos, self.startYPos = startPos
       self.vertexXPos, self.vertexYPos = endPos
       self.curPosX, self.curPosY = startPos
       self.setImgPos()
       self.speedX, self.speedY = 5, 5
       self.movesDone = 0
       self.hasBeenSliced = False
       self.withCombo = False  # boolean that means if False then the Fruit isn't to be added to the combo num

       for i, img in enumerate(self.images):
           curW, curH = img.get_rect().w, img.get_rect().h
           self.images[i] = pygame.transform.smoothscale(img.convert_alpha(), (int(curW * resizeFactor), int(curH * resizeFactor)))

       self.image = self.images[self.imgIndex]

   def setImgPos(self):
       self.rect.center = int(self.curPosX), int(self.curPosY)

   def setNewSpeed(self):
       self.endXPos, self.endYPos = 0, 0
       if self.vertexXPos - self.startXPos >= 0:
           self.endXPos, self.endYPos = self.startXPos + int(2 * (self.vertexXPos - self.startXPos)), self.startYPos
       else:
           self.endXPos, self.endYPos = self.startXPos - int(2 * (self.startXPos - self.vertexXPos)), self.startYPos

       xDif = self.vertexXPos - self.startXPos
       yDif = self.vertexXPos - self.startXPos

       slantLength = math.sqrt(xDif*xDif + yDif*yDif)

       factor = getFactorLength()

       self.speedX = xDif * (20*factor/slantLength)
       self.speedY = yDif * (20*factor/slantLength)

   def moveFruit(self):  # each time the fruit moves a certain distance, the image should change so the fruit is rotating
       self.moveDone += 1
       if self.movesDone >= 4:
           self.image = self.images[self.imgIndex + 1]

           if self.imgIndex == 3:
               self.imgIndex = 0
           else:
               self.imgIndex += 1

           self.image = self.images[self.imgIndex]
           self.rect = self.image.get_rect()
           centerX, centerY = self.rect.centerx, self.rect.centery
           self.rect.center = (centerX + self.speedX, centerY + self.speedY)

       # add more
   def resizeImg(self, oldGameScreenRect): # resize image to screen size dimensions
       global resizeFactor

       factorLengthX = gameScreenRect.w / oldGameScreenRect.w
       factorLengthY = gameScreenRect.h / oldGameScreenRect.h
       factorLength = factorLengthX

       if factorLengthX < factorLengthY:
           factorLength = factorLengthX
       else:
           factorLength = factorLengthY

       #Factor = factorLength * resizeFactor

       for i, img in enumerate(self.images):
           curW, curH = img.get_rect().w, img.get_rect().h
           self.images[i] = pygame.transform.smoothscale(img, (int(curW * factorLength), int(curH * factorLength)))

       self.image = self.images[self.imgIndex]


   def drawFruit(self):
       pass

   def drawExplodeFruit(self):  # draws the fruit when it's been cut
       pass


class Bomb():

   def __init__(self, hitboxRect, startPos, endPos):
       # self.images = img  # the bomb images, an array with an animation of the images in order
       self.hitboxRect = hitboxRect
       self.startXPos, self.startYPos = startPos
       self.endXPos, self.endYPos = endPos
       self.curPosX, self.curPosY = startPos
       self.hasBeenSliced = False

   def moveBomb(self, speed):
       pass

   def drawBomb(self):
       pass

   def drawExplodingBomb(self):
       pass


# GLOBAL METHODS
#def drawRoots():

def reconfigAllRootsPosAndSize(oldGameScreenRect):
    for root in rootGroup:
        root.curPosX, root.curPosY = reconfigFruitPos(root.curPosX, root.curPosY, oldGameScreenRect)
        root.setImgPos()
        root.resizeImg(oldGameScreenRect)

def addNewRanRoot():
    images = None
    randy = randint(0, 8)
    if randy == 0:
        img1 = pygame.image.load('ClassicPotato-1.png')
        img2 = pygame.image.load('ClassicPotato-2.png')
        img3 = pygame.image.load('ClassicPotato-3.png')
        img4 = pygame.image.load('ClassicPotato-4.png')
        images = [img1, img2, img3, img4]
    if randy == 1:
        img1 = pygame.image.load('Carrot-1.png.png')
        img2 = pygame.image.load('Carrot-2.png.png')
        img3 = pygame.image.load('Carrot-3.png.png')
        img4 = pygame.image.load('Carrot-4.png.png')
        images = [img1, img2, img3, img4]
    if randy == 2:
        img1 = pygame.image.load('Garlic-1.png.png')
        img2 = pygame.image.load('Garlic-2.png.png')
        img3 = pygame.image.load('Garlic-3.png.png')
        img4 = pygame.image.load('Garlic-4.png.png')
        images = [img1, img2, img3, img4]
    if randy == 3:
        img1 = pygame.image.load('PurpleVitelottePotato-1.png.png')
        img2 = pygame.image.load('PurpleVitelottePotato-2.png.png')
        img3 = pygame.image.load('PurpleVitelottePotato-3.png.png')
        img4 = pygame.image.load('PurpleVitelottePotato-4.png.png')
        images = [img1, img2, img3, img4]
    if randy == 4:
        img1 = pygame.image.load('Radish-1.png.png')
        img2 = pygame.image.load('Radish-2.png.png')
        img3 = pygame.image.load('Radish-3.png.png')
        img4 = pygame.image.load('Radish-4.png.png')
        images = [img1, img2, img3, img4]
    if randy == 5:
        img1 = pygame.image.load('RedLauraPotato-1.png.png')
        img2 = pygame.image.load('RedLauraPotato-2.png.png')
        img3 = pygame.image.load('RedLauraPotato-3.png.png')
        img4 = pygame.image.load('RedLauraPotato-4.png.png')
        images = [img1, img2, img3, img4]
    if randy == 6:
        img1 = pygame.image.load('SweetPotato-1.png.png')
        img2 = pygame.image.load('SweetPotato-2.png.png')
        img3 = pygame.image.load('SweetPotato-3.png.png')
        img4 = pygame.image.load('SweetPotato-4.png.png')
        images = [img1, img2, img3, img4]
    if randy == 7:
        img1 = pygame.image.load('Turnip-1.png.png')
        img2 = pygame.image.load('Turnip-2.png.png')
        img3 = pygame.image.load('Turnip-3.png.png')
        img4 = pygame.image.load('Turnip-4.png.png')
        images = [img1, img2, img3, img4]
    if randy == 8:
        img1 = pygame.image.load('YukonGoldPotato-1.png.png')
        img2 = pygame.image.load('YukonGoldPotato-2.png.png')
        img3 = pygame.image.load('YukonGoldPotato-3.png.png')
        img4 = pygame.image.load('YukonGoldPotato-4.png.png')
        images = [img1, img2, img3, img4]

    img, (startX, startY), (vertexX, vertexY) = getRanStartAndVertexPos()
    rootGroup.add(Fruit(images, (startX, startY), (vertexX, vertexY)))

def reconfigFruitPos(posX, posY, oldGameScreenRect): # scales the positions of coordinates appropriately when screen size changes
    global gameScreenRect

    factorLengthX = gameScreenRect.w/oldGameScreenRect.w
    factorLengthY = gameScreenRect.h/oldGameScreenRect.h
    #print(factorLengthY)
    #print(factorLengthX)
    newPosX, newPosY = factorLengthX*posX, factorLengthY*posY
    return newPosX, newPosY

def getRanStartAndVertexPos():
    global gameScreenRect

    left, top = gameScreenRect.topleft
    left, bottom = gameScreenRect.bottomleft
    w, h = gameScreenRect.w, gameScreenRect.h
    ranStartXAdd, ranStartYAdd = randint(0, w), h - 20
    ranVertexXAdd, ranVertexYAdd = randint(0, w), randint(30, h - 30)
    img = pygame.image.load('ClassicPotato-1.png')
    return img, (ranStartXAdd, ranStartYAdd), (ranVertexXAdd, ranVertexYAdd)

def redrawScreen():
    DISPLAYSURF.fill(BLACK)
    drawScreenArea()

def getFactorLength():
   factorLength = windowWidth

   if windowWidth >= windowHeight:
       factorLength = windowHeight
   else:
       factorLength = windowWidth
   return factorLength

def drawCursorTrail():  # if the cursor speed is greater than minSpeed, then a trail will for behind it until it's greater than a certain amount
    global cursorSpeed
    particles = []
    particles.append()


def getCursorSpeedIsFast(initialMousePos, curMousePos): # every 200 milliseconds, the mouse should have moved past at least 100 pixels

   xInitial, yInitial = initialMousePos
   xCur, yCur = curMousePos
   xDif = abs(xCur - xInitial)
   yDif = abs(yCur - yInitial)
   distance = math.sqrt(xDif*xDif + yDif*yDif)
   cursorSpeed = distance, 200 # cursor speed is distance/200 millaseconds
   if distance > 200:
       return True
   else:
       return False

def drawScreenArea():
   global gameScreenRect

   gameScreenRect = None
   factorLength = getFactorLength()
   img = pygame.image.load('choppingBoard.png')

   remainder = int(factorLength * 80 / 81) % 15
   length = int(factorLength * 80 / 81) - remainder
   img = pygame.transform.smoothscale(img, (length, length))
   img.get_rect().center = (int(windowWidth / 2), int(windowHeight / 2))
   gameScreenRect = img.get_rect()
   gameScreenRect.center = (int(windowWidth / 2), int(windowHeight / 2))
   left, top = gameScreenRect.topleft
   DISPLAYSURF.blit(img, (left, top))

def determineMode(position):
   global DISPLAYSURF
   xPos, yPos = position
   if openScreenRects[0].collidepoint(xPos, yPos):
       DISPLAYSURF.fill(BLACK)
       return "TIMER"
   elif openScreenRects[1].collidepoint(xPos, yPos):
       DISPLAYSURF.fill(BLACK)
       return "3STRIKES"
   else:
       return None

def openingScreen(bool):
   global DISPLAYSURF, openingFONT, windowWidth, windowHeight, openScreenRects, factor, rootGroup
   openScreenRects.clear();
   color1 = RED
   color2 = WATERMELON
   factorW = windowWidth / 500
   factorH = windowHeight / 500
   factor = factorW
   if factorH <= factorW:
       factor = factorH
   if bool == True:
       color1 = WATERMELON
       color2 = RED

   openingFONT = pygame.font.SysFont('chiller', int(factor * 70))
   DISPLAYSURF.fill(BLACK)
   textSurface = openingFONT.render('Root Ninja:', True, color1, color2)
   textRect = textSurface.get_rect()
   textRect.center = (int(windowWidth / 2), int(windowHeight / 10))
   DISPLAYSURF.blit(textSurface, textRect)
   textSurface = openingFONT.render('Timer Mode', True, RED, YELLOW)
   textRect = textSurface.get_rect()
   openScreenRects.append((textRect))  # adds TIMER rect at index 0
   textRect.center = (int(windowWidth / 2), int(4 * windowHeight / 10))
   DISPLAYSURF.blit(textSurface, textRect)
   textSurface = openingFONT.render('3 Strikes Mode', True, PURPLE, ORANGE)
   textRect = textSurface.get_rect()
   openScreenRects.append((textRect))  # adds 3STRIKES rect at index 1
   textRect.center = (int(windowWidth / 2), int(8 * windowHeight / 10))
   DISPLAYSURF.blit(textSurface, textRect)


def terminate():
   pygame.quit()
   sys.exit()


def main():
   global DISPLAYSURF, windowWidth, windowHeight, gameMode
   my_eventTime = USEREVENT + 1
   pygame.time.set_timer(my_eventTime, 200)
   changeEventTime = True
   openingScreen(True)
   titleTime = pygame.time.get_ticks()
   titleBool = True
   initMousePosX, initMousePosY = pygame.mouse.get_pos()
   pygame.mouse.set_cursor(*pygame.cursors.broken_x)
   drawScreenArea()
   img, (startX, starty), (vertexX, vertexY) = getRanStartAndVertexPos()
   oldGameScreenRect = None

   fruitSpawnTimer = 2000 # when fruitSpawnTimer time has elapsed, a new fruit should spawn
   startTics = pygame.time.get_ticks()

   while True:
       for event in pygame.event.get():

           if not gameMode == None and changeEventTime == True:
               changeEventTime = False
               pygame.time.set_timer(my_eventTime, 150)
               initMousePosX, initMousePosY = pygame.mouse.get_pos()

           if gameMode == 'TIMER' and event.type == my_eventTime:
               redrawScreen()
               oldGameScreenRect = gameScreenRect

               rootGroup.draw(DISPLAYSURF) # draws the roots
               rootGroup.update()

               imgRect = img.get_rect()
               imgRect.center = int(gameScreenRect.left + startX), int(gameScreenRect.top + starty)
               DISPLAYSURF.blit(img, imgRect)

           if gameMode == 'TIMER' and pygame.time.get_ticks() - startTics >= fruitSpawnTimer:
               startTics = pygame.time.get_ticks()
               fruitSpawnTimer = randint(400, 4000)
               addNewRanRoot()

           if gameMode == None and event.type == pygame.MOUSEBUTTONUP:
               gameMode = determineMode(pygame.mouse.get_pos())
               #print(str(gameMode))

           if event.type == my_eventTime and gameMode == None:
               titleBool = not titleBool
               openingScreen(titleBool)
               imgRect = img.get_rect()
               imgRect.center = gameScreenRect.left + startX, gameScreenRect.top + starty
               DISPLAYSURF.blit(img, imgRect)

           if event.type == QUIT:
               terminate()

           if event.type == pygame.VIDEORESIZE:  # Allows resizing screen
               DISPLAYSURF = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
               windowWidth, windowHeight, = event.w, event.h
               if not gameMode == None:
                   redrawScreen()
                   startX, starty = reconfigFruitPos(startX, starty, oldGameScreenRect)
                   reconfigAllRootsPosAndSize(oldGameScreenRect)

           if event.type == my_eventTime and pygame.mouse.get_pressed()[0]:
               pygame.draw.aaline(DISPLAYSURF, RED, (initMousePosX, initMousePosY), (pygame.mouse.get_pos()), 6)
               isFast = getCursorSpeedIsFast((initMousePosX, initMousePosY), pygame.mouse.get_pos())
               initMousePosX, initMousePosY = pygame.mouse.get_pos()
               #print(str(isFast))

           if event.type == my_eventTime:
               initMousePosX, initMousePosY = pygame.mouse.get_pos()


       pygame.display.update()
       FPSCLOCK.tick(FPS)


# RUN MAIN
if __name__ == '__main__':
   main()







