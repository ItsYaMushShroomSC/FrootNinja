import math
from random import randint

from pygame.locals import *
import pygame
import sys
from pygame.locals import *

pygame.init()

# Constants
windowWidth = 500
windowHeight = 500

# Surface
factor = 5
DISPLAYSURF = pygame.display.set_mode((windowWidth, windowHeight), pygame.RESIZABLE)
surfaceRect = DISPLAYSURF.get_rect()
pygame.display.set_caption('Root Ninja')

# Time
FPS = 160
FPSCLOCK = pygame.time.Clock()

# Colors

RED = (255, 0, 0)
BLACK = (0, 0, 0)
GREY = (128, 128, 128)

# Global Variables

isFast = False

openScreenRects = []  # stores rectangles of the opening screen
gameStarted = False  # when is gameStarted is False, start screen appears
gameScreenRect = None

resizeGameScreenRect = None
oldFactorLength = 1

rootGroup = pygame.sprite.Group()

score = 0
livesLeft = 3

# CLASSES

class Fruit(pygame.sprite.Sprite):
   def __init__(self, images, startPosAdd, vertexPosAdd, isBomb):
       pygame.sprite.Sprite.__init__(self)
       global resizeGameScreenRect

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
       self.sliceImgTime = 0
       self.hasBeenSliced = False
       self.withCombo = False  # boolean that means if False then the Fruit isn't to be added to the combo num
       self.image = self.images[self.imgIndex]
       self.isBomb = isBomb
       self.lostPoints = 0

       self.resizeImg(resizeGameScreenRect, True)

       self.image = self.images[self.imgIndex]
       self.setImgPos()

       self.mask = pygame.mask.from_surface(self.image)

   def setMask(self):
       self.mask = pygame.mask.from_surface(self.image)

   def checkHasBeenSliced(self):
       global score, isFast

       if self.hasBeenSliced == True:
           if self.sliceImgTime == 0 and self.isBomb == False:
               score += 10
               if isFast == True:
                   self.withCombo = True

           if self.sliceImgTime == 0 and self.isBomb == True:
               if score < 10:
                   self.lostPoints = score
                   score = 0
               elif score >= 10:
                   self.lostPoints = 10
                   score -= 10

           self.image = self.images[4]
           self.sliceImgTime += 1;

           if self.isBomb == True and self.sliceImgTime <= 6:
               openingFONT = pygame.font.SysFont('chiller', int(gameScreenRect.w / 480 * 50))
               textSurface = openingFONT.render('--- ' + str(self.lostPoints), True, BLACK, GREY)
               textRect = textSurface.get_rect()
               textRect.topleft = (self.curPosX+self.rect.w/2, self.curPosY)
               DISPLAYSURF.blit(textSurface, textRect)

   def checkShouldRemoveRoot(self): # returns true means remove fruit
       if self.hasBeenSliced == True and self.sliceImgTime >= 15:
           #pointSpriteGroup.add()
           return True
       elif self.curPosX < 0 or self.curPosX > windowWidth or self.curPosY < 0 or self.curPosY > windowHeight:
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

       if self.curPosY <= self.vertexYPos or self.reachedVertex == True:
           self.reachedVertex = True
           xDif = self.endXPos - self.vertexXPos
           yDif = self.endYPos - self.vertexYPos

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
       self.setMask()
       self.checkHasBeenSliced()
       # add more

   def resizeImg(self, oldGameScreenRect, isSpawn):  # resize image to screen size dimensions
       global resizeGameScreenRect, oldFactorLength

       if oldGameScreenRect:
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

# GLOBAL METHODS

def drawXLives():
    global livesLeft
    blackImg = pygame.image.load('BlackX.png')
    redImg = pygame.image.load('RedX.png')
    rect = blackImg.get_rect()
    black = pygame.transform.smoothscale(blackImg, (int(rect.w * gameScreenRect.w/480), int(rect.h * gameScreenRect.w/480)))
    red = pygame.transform.smoothscale(redImg, (int(rect.w * gameScreenRect.w/480), int(rect.h * gameScreenRect.w/480)))
    x1, x2, x3 = black, black, black
    if livesLeft <= 2:
        x1 = red
    if livesLeft <= 1:
        x2 = red
    if livesLeft <= 0:
        x3 = red

    rect = black.get_rect()

    rect.center = (int(windowWidth / 2 + rect.w + 10), int(gameScreenRect.top + gameScreenRect.h / 12))
    DISPLAYSURF.blit(x1, rect)
    rect.center = (int(windowWidth / 2 + rect.w*2 + 10), int(gameScreenRect.top + gameScreenRect.h / 12))
    DISPLAYSURF.blit(x2, rect)
    rect.center = (int(windowWidth / 2 + rect.w*3 + 10), int(gameScreenRect.top + gameScreenRect.h / 12))
    DISPLAYSURF.blit(x3, rect)

def checkComboPoints():
    global score

    numCombos = 0
    for root in rootGroup:
        if root.withCombo == True:
            numCombos += 1
            root.withCombo = False
            posX, posY = root.curPosX + root.rect.w/2, root.curPosY

    if numCombos > 1:
        score += numCombos
        openingFONT = pygame.font.SysFont('chiller', int(gameScreenRect.w / 480 * 50))
        textSurface = openingFONT.render('+++ ' + str(numCombos), True, BLACK, GREY)
        textRect = textSurface.get_rect()
        textRect.center = (posX, posY)
        DISPLAYSURF.blit(textSurface, textRect)

def drawScore():
    global score
    openingFONT = pygame.font.SysFont('chiller', int(gameScreenRect.w/480 * 30))
    textSurface = openingFONT.render('Score: ' + str(score), True, BLACK, GREY)
    textRect = textSurface.get_rect()
    textRect.center = (int(windowWidth / 2), int(windowHeight / 12))
    DISPLAYSURF.blit(textSurface, textRect)

def getLinePoints(initPosX, initPosY, curPosX, curPosY):
    linePointAry = []
    #y=(Ay-By)/(Ax-Bx)*(x-Ax)+Ay

    start, end = None, None

    if initPosX >= curPosX:
        start = curPosX
        end = initPosX
    else:
        start = initPosX
        end = curPosX
    for x in range(start, end+1):
        if not initPosX-curPosX == 0:
            y = (initPosY-curPosY)/(initPosX-curPosX) * (x - initPosX) + initPosY
            linePointAry.append((x, y))

    return linePointAry

def checkMouseRootCollide(initPosX, initPosY, curPos):
    curPosX, curPosY = curPos
    for root in rootGroup:
        linePointAry = getLinePoints(initPosX, initPosY, curPosX, curPosY)

        for point in linePointAry:
            pointX, pointY = point

            if root.rect.collidepoint((pointX, pointY)):
                root.hasBeenSliced = True
                print("poo")


def getSlicedRoots(lineRect, collidedRoots):
    for cRoot in collidedRoots:
        collidePoint = pygame.sprite.collide_mask(lineRect, cRoot)
        cRoot.hasBeenSliced = True

def drawBlackOutsideOfGSR(): # GSR = gameScreenRect
    right = gameScreenRect.right
    bottom = gameScreenRect.bottom

    pygame.draw.rect(DISPLAYSURF, BLACK, (0, 0, gameScreenRect.left, windowHeight))
    pygame.draw.rect(DISPLAYSURF, BLACK, (0, 0, windowWidth, gameScreenRect.top))
    pygame.draw.rect(DISPLAYSURF, BLACK, (right, 0, gameScreenRect.left, windowHeight))
    pygame.draw.rect(DISPLAYSURF, BLACK, (0, bottom, windowWidth, gameScreenRect.top))

def removeRoots():
    global livesLeft
    for root in rootGroup:
        if root.checkShouldRemoveRoot() == True:
            if root.hasBeenSliced == False and root.isBomb == False:
                livesLeft -= 1
            rootGroup.remove(root)

def moveAllRoots():
    for root in rootGroup:
        root.moveFruit()

def reconfigAllRootsPosAndSize(oldGameScreenRect):
    global resizeFactor

    rooty = addNewRanRoot()
    rootGroup.add(rooty)

    for i, root in enumerate(rootGroup):
        root.resizeImg(oldGameScreenRect, False)
        root.curPosAddX, root.curPosAddY = reconfigFruitPos(root.curPosAddX, root.curPosAddY, oldGameScreenRect)
        root.curPosX, root.curPosY = gameScreenRect.left + root.curPosAddX, gameScreenRect.top + root.curPosAddY
        root.startXPos, root.startYPos = reconfigFruitPos(root.startXPos, root.startYPos, oldGameScreenRect)
        #root.setImgPos()
        root.vertexPosAddX, root.vertexPosAddY = reconfigFruitPos(root.vertexPosAddX, root.vertexPosAddY, oldGameScreenRect)
        root.vertexXPos, root.vertexYPos = gameScreenRect.left + root.vertexPosAddX, gameScreenRect.top + root.vertexPosAddY
        root.setImgPos()

        rooty.kill()


def addNewRanRoot():
    images = None
    randy = randint(0, 9)
    isBomb = False
    if randy == 0:
        img1 = pygame.image.load('ClassicPotato-1.png')
        img2 = pygame.image.load('ClassicPotato-2.png')
        img3 = pygame.image.load('ClassicPotato-3.png')
        img4 = pygame.image.load('ClassicPotato-4.png')
        img5 = pygame.image.load('ClassicPotato-7.png.png')
        images = [img1, img2, img3, img4, img5]
    if randy == 1:
        img1 = pygame.image.load('Carrot-1.png.png')
        img2 = pygame.image.load('Carrot-2.png.png')
        img3 = pygame.image.load('Carrot-3.png.png')
        img4 = pygame.image.load('Carrot-4.png.png')
        img5 = pygame.image.load('Carrot-7.png.png')
        images = [img1, img2, img3, img4, img5]
    if randy == 2:
        img1 = pygame.image.load('Garlic-1.png.png')
        img2 = pygame.image.load('Garlic-2.png.png')
        img3 = pygame.image.load('Garlic-3.png.png')
        img4 = pygame.image.load('Garlic-4.png.png')
        img5 = pygame.image.load('Garlic-6.png.png')
        images = [img1, img2, img3, img4, img5]
    if randy == 3:
        img1 = pygame.image.load('PurpleVitelottePotato-1.png.png')
        img2 = pygame.image.load('PurpleVitelottePotato-2.png.png')
        img3 = pygame.image.load('PurpleVitelottePotato-3.png.png')
        img4 = pygame.image.load('PurpleVitelottePotato-4.png.png')
        img5 = pygame.image.load('PurpleVitelottePotato-6.png.png')
        images = [img1, img2, img3, img4, img5]
    if randy == 4:
        img1 = pygame.image.load('Radish-1.png.png')
        img2 = pygame.image.load('Radish-2.png.png')
        img3 = pygame.image.load('Radish-3.png.png')
        img4 = pygame.image.load('Radish-4.png.png')
        img5 = pygame.image.load('Radish-8.png.png')
        images = [img1, img2, img3, img4, img5]
    if randy == 5:
        img1 = pygame.image.load('RedLauraPotato-1.png.png')
        img2 = pygame.image.load('RedLauraPotato-2.png.png')
        img3 = pygame.image.load('RedLauraPotato-3.png.png')
        img4 = pygame.image.load('RedLauraPotato-4.png.png')
        img5 = pygame.image.load('RedLauraPotato-7.png.png')
        images = [img1, img2, img3, img4, img5]
    if randy == 6:
        img1 = pygame.image.load('SweetPotato-1.png.png')
        img2 = pygame.image.load('SweetPotato-2.png.png')
        img3 = pygame.image.load('SweetPotato-3.png.png')
        img4 = pygame.image.load('SweetPotato-4.png.png')
        img5 = pygame.image.load('SweetPotato-5.png.png')
        images = [img1, img2, img3, img4, img5]
    if randy == 7:
        img1 = pygame.image.load('Turnip-1.png.png')
        img2 = pygame.image.load('Turnip-2.png.png')
        img3 = pygame.image.load('Turnip-3.png.png')
        img4 = pygame.image.load('Turnip-4.png.png')
        img5 = pygame.image.load('Turnip-10.png.png')
        images = [img1, img2, img3, img4, img5]
    if randy == 8:
        img1 = pygame.image.load('YukonGoldPotato-1.png.png')
        img2 = pygame.image.load('YukonGoldPotato-2.png.png')
        img3 = pygame.image.load('YukonGoldPotato-3.png.png')
        img4 = pygame.image.load('YukonGoldPotato-4.png.png')
        img5 = pygame.image.load('YukonGoldPotato-7.png.png')
        images = [img1, img2, img3, img4, img5]
    if randy == 9:
        img1 = pygame.transform.smoothscale(pygame.image.load('Bomb-1.png.png'), (128, 128))
        img2 = pygame.transform.smoothscale(pygame.image.load('Bomb-2.png.png'), (128, 128))
        img3 = pygame.transform.smoothscale(pygame.image.load('Bomb-3.png.png'), (128, 128))
        img4 = pygame.transform.smoothscale(pygame.image.load('Bomb-4.png.png'), (128, 128))
        img5 = pygame.transform.smoothscale(pygame.image.load('Bomb-6.png.png'), (128, 128))
        images = [img1, img2, img3, img4, img5]
        isBomb = True

    img, (startX, startY), (vertexX, vertexY) = getRanStartAndVertexPos()
    left, top = gameScreenRect.topleft
    return Fruit(images, (startX, startY), (vertexX, vertexY), isBomb)

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
   if distance > 185:
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
       return True
   else:
       return False

def openingScreen(bool):
   global DISPLAYSURF, openingFONT, windowWidth, windowHeight, openScreenRects, factor, rootGroup
   openScreenRects.clear();
   color1 = GREY
   color2 = BLACK
   factorW = windowWidth / 500
   factorH = windowHeight / 500
   factor = factorW
   if factorH <= factorW:
       factor = factorH
   if bool == True:
       color1 = BLACK
       color2 = GREY

   openingFONT = pygame.font.SysFont('chiller', int(factor * 110))
   DISPLAYSURF.fill(BLACK)
   textSurface = openingFONT.render('Root Ninja:', True, color1, color2)
   textRect = textSurface.get_rect()
   textRect.center = (int(windowWidth / 2), int(windowHeight / 2))
   openScreenRects.append((textRect))
   DISPLAYSURF.blit(textSurface, textRect)

def terminate():
   pygame.quit()
   sys.exit()


def main():
   global DISPLAYSURF, windowWidth, windowHeight, gameStarted, isFast, score, livesLeft, rootGroup
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

   collideLine = None

   fruitSpawnTimer = 2000 # when fruitSpawnTimer time has elapsed, a new fruit should spawn
   startTics = pygame.time.get_ticks()

   while True:
       for event in pygame.event.get():

           if livesLeft <= 0 and gameStarted == True:
               drawXLives()
               pygame.display.update()
               pygame.time.wait(2000)
               rootGroup = pygame.sprite.Group()
               changeEventTime = True
               gameStarted = False
               livesLeft = 3
               score = 0
               pygame.time.set_timer(my_eventTime, 200)
               drawScreenArea(False)
               oldGameScreenRect = None
               startTics = pygame.time.get_ticks()

           if gameStarted == True and changeEventTime == True:
               changeEventTime = False
               pygame.time.set_timer(my_eventTime, 150)
               initMousePosX, initMousePosY = pygame.mouse.get_pos()

           if gameStarted == True and event.type == my_eventTime:
               redrawScreen()
               oldGameScreenRect = gameScreenRect
               drawScore()
               drawXLives()
               checkComboPoints()
               removeRoots()
               moveAllRoots()
               rootGroup.draw(DISPLAYSURF) # draws the roots
               rootGroup.update()
               drawBlackOutsideOfGSR()

           if gameStarted == True and pygame.time.get_ticks() - startTics >= fruitSpawnTimer:
               startTics = pygame.time.get_ticks()
               fruitSpawnTimer = randint(80, 2000)
               rootGroup.add(addNewRanRoot())

           if gameStarted == False and event.type == pygame.MOUSEBUTTONUP:
               gameStarted = determineMode(pygame.mouse.get_pos())
               startTics = pygame.time.get_ticks()

           if event.type == my_eventTime and gameStarted == False:
               titleBool = not titleBool
               openingScreen(titleBool)

           if event.type == QUIT:
               terminate()

           if event.type == pygame.VIDEORESIZE:  # Allows resizing screen
               DISPLAYSURF = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
               windowWidth, windowHeight, = event.w, event.h

               if gameStarted == True:
                   redrawScreen()
                   reconfigAllRootsPosAndSize(oldGameScreenRect)
                   oldGameScreenRect = gameScreenRect

           if event.type == my_eventTime and pygame.mouse.get_pressed()[0]:
               pygame.draw.aaline(DISPLAYSURF, RED, (initMousePosX, initMousePosY), (pygame.mouse.get_pos()), 6)
               curPos = pygame.mouse.get_pos()

               isFast = getCursorSpeedIsFast((initMousePosX, initMousePosY), curPos)
               if isFast == True:
                   checkMouseRootCollide(initMousePosX, initMousePosY, curPos)

               initMousePosX, initMousePosY = pygame.mouse.get_pos()
               #print(str(isFast))

           if event.type == my_eventTime:
               initMousePosX, initMousePosY = pygame.mouse.get_pos()


       pygame.display.update()
       FPSCLOCK.tick(FPS)


# RUN MAIN
if __name__ == '__main__':
   main()







