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

resizeGameScreenRect = None
oldFactorLength = 1

rootGroup = pygame.sprite.Group()

# CLASSES

class Fruit(pygame.sprite.Sprite):
   def __init__(self, images, startPosAdd, vertexPosAdd):
       pygame.sprite.Sprite.__init__(self)
       global resizeGameScreenRect

       self.refImages = images

       self.images = images  # the fruit images, an array with animation images in order, last image is explode img
       self.image = images[0]  # self.image is from the Sprite class
       self.imgIndex = 0
       self.rect = self.image.get_rect()  # from the Sprite class
       self.curPosAddX, self.curPosAddY = startPosAdd
       self.vertexPosAddX, self.vertexPosAddY = vertexPosAdd
       self.startXPos, self.startYPos = gameScreenRect.left + self.curPosAddX, gameScreenRect.top + self.curPosAddY
       self.vertexXPos, self.vertexYPos = gameScreenRect.left + vertexPosAdd[0], gameScreenRect.top + vertexPosAdd[1]
       self.curPosX, self.curPosY = self.startXPos, self.startYPos
       self.reachedVertex = False
       self.speedX, self.speedY = 5, -5
       self.setNewSpeed()
       self.movesDone = 0
       self.hasBeenSliced = False
       self.withCombo = False  # boolean that means if False then the Fruit isn't to be added to the combo num
       self.image = self.images[self.imgIndex]

       if not resizeGameScreenRect == None:
           self.resizeImg(resizeGameScreenRect, True)


       self.image = self.images[self.imgIndex]
       self.setImgPos()

   def checkHasBeenSliced(self):
       if self.hasBeenSliced == True:
           self.image = self.images[4]

   def checkShouldRemoveRoot(self): # returns true means remove fruit
       if self.curPosX < 0 or self.curPosX > windowWidth or self.curPosY < 0 or self.curPosY > windowHeight:
           return True
       else:
           return False

   def setImgPos(self):
       self.rect.center = int(self.curPosX), int(self.curPosY)

   def setNewSpeed(self):
       self.endXPos, self.endYPos = 0, 0
       if self.vertexXPos - self.startXPos >= 0:
           self.endXPos, self.endYPos = self.startXPos + int(2 * (self.vertexXPos - self.startXPos)), self.startYPos
       else:
           self.endXPos, self.endYPos = self.startXPos - int(2 * (self.startXPos - self.vertexXPos)), self.startYPos

       xDif = self.vertexXPos - self.startXPos
       yDif = self.vertexYPos - self.startYPos

       #print(str(self.curPosY))
       #print(str(self.vertexYPos))

       if self.curPosY <= self.vertexYPos or self.reachedVertex == True:
           self.reachedVertex = True
           xDif = self.endXPos - self.vertexXPos
           yDif = self.endYPos - self.vertexYPos
           print('hi')

       slantLength = math.sqrt(xDif*xDif + yDif*yDif)

       factor = gameScreenRect.w / 480

       self.speedX = xDif * (40*factor/slantLength)
       self.speedY = yDif * (40*factor/slantLength)


   def moveFruit(self):  # each time the fruit moves a certain distance, the image should change so the fruit is rotating
       self.movesDone += 1

       self.setNewSpeed()

       if self.imgIndex == 3:
           self.imgIndex = 0
       else:
           self.imgIndex += 1

       if self.movesDone >= 3:
           if not self.imgIndex == 3:
               self.movesDone = 0
               self.image = self.images[self.imgIndex + 1]

       self.image = self.images[self.imgIndex]
       self.curPosX, self.curPosY = self.curPosX + self.speedX, self.curPosY + self.speedY
       self.setImgPos()

       # add more

   def resizeImg(self, oldGameScreenRect, isSpawn):  # resize image to screen size dimensions
       global resizeGameScreenRect, oldFactorLength


       factorLengthX = gameScreenRect.w / oldGameScreenRect.w
       factorLengthY = gameScreenRect.h / oldGameScreenRect.h
       factorLength = factorLengthX

       if factorLengthX < factorLengthY:
           factorLength = factorLengthX
       else:
           factorLength = factorLengthY

       resizeGameScreenRect = oldGameScreenRect
       oldFactorLength = factorLength

       if isSpawn == True:
           factorLength = gameScreenRect.w/480

       for i, img in enumerate(self.images):
           curW, curH = img.get_rect().w, img.get_rect().h
           self.images[i] = pygame.transform.smoothscale(img, (int(curW * factorLength), int(curH * factorLength)))

       self.image = self.images[self.imgIndex]
       self.setImgPos()

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

def drawBlackOutsideOfGSR(): # GSR = gameScreenRect
    right = gameScreenRect.right
    bottom = gameScreenRect.bottom

    pygame.draw.rect(DISPLAYSURF, BLACK, (0, 0, gameScreenRect.left, windowHeight))
    pygame.draw.rect(DISPLAYSURF, BLACK, (0, 0, windowWidth, gameScreenRect.top))
    pygame.draw.rect(DISPLAYSURF, BLACK, (right, 0, gameScreenRect.left, windowHeight))
    pygame.draw.rect(DISPLAYSURF, BLACK, (0, bottom, windowWidth, gameScreenRect.top))

def removeRoots():
    for root in rootGroup:
        if root.checkShouldRemoveRoot() == True:
            rootGroup.remove(root)

def moveAllRoots():
    for root in rootGroup:
        root.moveFruit()

def reconfigAllRootsPosAndSize(oldGameScreenRect):
    global resizeFactor

    for root in rootGroup:
        root.resizeImg(oldGameScreenRect, False)
        root.curPosAddX, root.curPosAddY = reconfigFruitPos(root.curPosAddX, root.curPosAddY, oldGameScreenRect)
        root.curPosX, root.curPosY = gameScreenRect.left + root.curPosAddX, gameScreenRect.top + root.curPosAddY
        root.startXPos, root.startYPos = reconfigFruitPos(root.startXPos, root.startYPos, oldGameScreenRect)
        #root.setImgPos()
        root.vertexPosAddX, root.vertexPosAddY = reconfigFruitPos(root.vertexPosAddX, root.vertexPosAddY, oldGameScreenRect)
        root.vertexXPos, root.vertexYPos = gameScreenRect.left + root.vertexPosAddX, gameScreenRect.top + root.vertexPosAddY
        root.setImgPos()


def addNewRanRoot():
    images = None
    randy = randint(0, 8)
    if randy == 0:
        img1 = pygame.image.load('ClassicPotato-1.png')
        img2 = pygame.image.load('ClassicPotato-2.png')
        img3 = pygame.image.load('ClassicPotato-3.png')
        img4 = pygame.image.load('ClassicPotato-4.png')
        img5 = pygame.image.load('ClassicPotatoSlice.png.png')
        images = [img1, img2, img3, img4, img5]
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
    left, top = gameScreenRect.topleft
    rootGroup.add(Fruit(images, (startX, startY), (vertexX, vertexY)))

def reconfigFruitPos(posX, posY, oldGameScreenRect): # scales the positions of coordinates appropriately when screen size changes
    global gameScreenRect, resizeGameScreenRect

    factorLengthX = gameScreenRect.w/oldGameScreenRect.w
    factorLengthY = gameScreenRect.h/oldGameScreenRect.h
    #print(factorLengthY)
    #print(factorLengthX)
    resizeGameScreenRect = oldGameScreenRect
    newPosX, newPosY = factorLengthX*posX, factorLengthY*posY
    return newPosX, newPosY

def getRanStartAndVertexPos():
    global gameScreenRect

    left, top = gameScreenRect.topleft
    left, bottom = gameScreenRect.bottomleft
    w, h = gameScreenRect.w, gameScreenRect.h
    ranStartXAdd, ranStartYAdd = randint(35, w-35), h - 35
    ranVertexXAdd, ranVertexYAdd = randint(30, h-30), randint(30, h - 60)
    img = pygame.image.load('ClassicPotato-1.png')
    return img, (ranStartXAdd, ranStartYAdd), (ranVertexXAdd, ranVertexYAdd)

def redrawScreen():
    DISPLAYSURF.fill(BLACK)
    drawScreenArea(True)

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

def drawScreenArea(booDraw):
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
   if booDraw == True:
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
   drawScreenArea(False)
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
               removeRoots()
               moveAllRoots()
               rootGroup.draw(DISPLAYSURF) # draws the roots
               rootGroup.update()
               drawBlackOutsideOfGSR()

           if gameMode == 'TIMER' and pygame.time.get_ticks() - startTics >= fruitSpawnTimer:
               startTics = pygame.time.get_ticks()
               fruitSpawnTimer = randint(100, 4000)
               addNewRanRoot()

           if gameMode == None and event.type == pygame.MOUSEBUTTONUP:
               gameMode = determineMode(pygame.mouse.get_pos())
               #print(str(gameMode))

           if event.type == my_eventTime and gameMode == None:
               titleBool = not titleBool
               openingScreen(titleBool)

           if event.type == QUIT:
               terminate()

           if event.type == pygame.VIDEORESIZE:  # Allows resizing screen
               DISPLAYSURF = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
               windowWidth, windowHeight, = event.w, event.h
               if not gameMode == None:
                   redrawScreen()
                   reconfigAllRootsPosAndSize(oldGameScreenRect)
                   oldGameScreenRect = gameScreenRect

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







