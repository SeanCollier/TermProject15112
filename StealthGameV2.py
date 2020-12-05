from cmu_112_graphics import *
import random
import math
import copy
import time


#################################        Math Helpers           #######################################

def getDistance(x0,y0,x1,y1):
    return ((x0-x1)**2+(y0-y1)**2)**0.5

def fixAngle(angle):
    result = angle%(2*math.pi)
    if result > math.pi:
        result -= 2*math.pi
    return result

def getAngleBetweenTwoPoints(x1,y1,x2,y2):
    dy = y2-y1
    dx = x2-x1
    if dx == 0:
        if dy >= 0:
            result = math.pi/2
        else:
            result = -math.pi/2
    else:
        abs_dy_dx = abs(dy/dx)
        if dx>0:
            if dy>0:
                result = math.atan(abs_dy_dx)
            else:
                result = -math.atan(abs_dy_dx)
        else:
            if dy>=0:
                result = math.pi-math.atan(abs_dy_dx)
            else:
                result = math.pi+math.atan(abs_dy_dx)
    return fixAngle(result)

def degreesToRadians(angle):
    return angle*math.pi/180

def radiansToDegrees(angle):
    return angle*180/math.pi

def turnAngle(faceAngle, targetAngle):
    return fixAngle(targetAngle-faceAngle)

def minDistPoint(x,y,L):
    minDist = None
    minPoint = None
    for point in L:
        pX, pY = point
        dist = getDistance(pX, pY, x, y)
        if minDist == None or dist < minDist:
            minDist = dist
            minPoint = point
    return minPoint

def findClosestGridPoint(x,y,app):
    col1 = int(x//60-1)
    col2 = int(col1 +1)
    row1 = int(y//60-1)
    row2 = int(row1+1)
    minDist = None
    minPoint = None
    if row1<0:
        row1 = 0
    if col1 <0:
        col1 = 0
    if row2 >= len(app.gridPoints):
        row2 = len(app.gridPoints)-1
    if col2 >= len(app.gridPoints[0]):
        col2 -= 1
    for row in [row1, row2]:
        for col in [col1, col2]:
            point = app.gridPoints[row][col]
            px,py = point
            Distance = getDistance(x,y,px,py)
            if minDist == None or Distance <= minDist:
                minDist = Distance
                minPoint = (px,py)
    px, py = minPoint
    return px,py

def findClosestGridRowCol(app, x,y):
    col1,row1 = findClosestGridPoint(x,y,app)
    row1//=60
    col1//=60
    row1 = int(row1)-1
    col1 = int(col1)-1
    return row1,col1

def isValidCell(row, col, L):
    if row < 0 or col < 0 or row >= len(L) or col >= len(L[0]):
        return False
    return True

def getRandomNearbyPoint(app, distance, startRow, startCol, badPoints):
    pointFound = False
    dxList = [x for x in range(-distance, distance+1)]
    endRow = 0
    endCol = 0
    while not pointFound:
        xIndex = random.randint(0,len(dxList)-1)
        yIndex = random.randint(0,len(dxList)-1)
        if yIndex == xIndex == 0:
            continue
        potentialCol = startCol + dxList[xIndex]
        potentialRow = startRow + dxList[yIndex]
        if (isValidCell(potentialRow, potentialCol, app.gridPoints) and 
                (potentialRow, potentialCol) not in badPoints):
            endRow = potentialRow
            endCol = potentialCol
            pointFound = True
    return (endRow, endCol)

        

        



#######################################################################################################
#############################  Node class modified from https://medium.com/@nicholas.w.swift/easy-a-star-pathfinding-7e6689c7f7b2
class Node():
    def __init__(self,position, rowCol, h = 0,g = 0, parent = None):
        self.f = h+g
        self.h = h
        self.g = g
        self.position = position
        self.parent = parent
        self.rowCol = rowCol

    def __eq__(self,other):
        return self.rowCol == other.rowCol
    
    def __repr__(self):
        return f"Node at : {self.rowCol}"

#######################################################################################################

class rectangle(object):
    def __init__(self, x1, y1, x2, y2, fill):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.fill = fill

    def draw(self, canvas):
        canvas.create_rectangle(self.x1, self.y1, self.x2, self.y2,
                 fill = self.fill)
    def viablePoint(self, startX, startY, intX, intY, endX, endY):
        minX = min(startX, endX)
        maxX = max(startX, endX)
        minY = min(startY, endY)
        maxY = max(startY, endY)

        inRectangle = False
        if intX >= self.x1 and intX<=self.x2 and intY >= self.y1 and intY <= self.y2:
            inRectangle = True

        if inRectangle and intX <= maxX and intX >= minX and intY <= maxY and intY >= minY:
            return intX, intY
        else:
            return None
    
    def pointInRectangle(self, x,y):
        if x<=self.x2 and x>= self.x1 and y<=self.y2 and y>=self.y1:
            return True
        return False


    def collisionCheck(self, x, y, x2, y2, length):
        LLInt = None
        RLInt = None
        BLInt = None
        TLInt = None
        if x == x2:
            if x >= self.x1 and x <= self.x2:
                TLInt = self.viablePoint(x,y,x, self.y1,x2,y2)
                BLInt = self.viablePoint(x,y,x, self.y2,x2,y2)
        elif y == y2:
            if y>=self.y1 and y<= self.y2:
                LLInt = self.viablePoint(x,y,self.x1, y,x2,y2)
                RLInt = self.viablePoint(x,y,self.x2, y,x2,y2)
        else:
            slope = (y2-y)/(x2-x)
            b = y-slope*x

            #### Top Line
            intX = (self.y1-b)/slope
            TLInt = self.viablePoint(x,y,intX,self.y1,x2,y2)

            #### Left Line
            intY = slope*self.x1 + b
            LLInt = self.viablePoint(x,y,self.x1, intY,x2,y2)

            #### Right Line
            intY = slope*self.x2 + b
            RLInt = self.viablePoint(x,y,self.x2, intY,x2,y2)

            #### Bottom Line
            intX = (self.y2-b)/slope
            BLInt = self.viablePoint(x,y,intX, self.y2,x2,y2)

        allViablePoints = [x for x in [TLInt, LLInt, RLInt, BLInt] if x!= None]
        return minDistPoint(x,y, allViablePoints)


class Entity(object):

    def __init__(self, fill,speed):
        self.radius = 20
        self.fill = fill
        self.speed = speed
    
    def move(self, direction, app):
        x,y = self.position
        dx, dy = direction
        dx *= self.speed
        dy *= self.speed
        newX=x+dx
        newY=y+dy
        if (newY-self.radius < 0 or newY +self.radius > app.height or 
                newX -self.radius < 0 or newX+self.radius > app.width):
            newX = x
            newY = y
        
        if self.overlappingObstacle(app, newX, newY):
            newX = x
            newY = y
        self.position = newX, newY
    
    def overlappingObstacle(self, app, x1, y1):
        offset = 0.707
        possiblePoints = [(x1-self.radius, y1), 
            (x1-offset*self.radius, y1+offset*self.radius),
            (x1, y1+self.radius), (x1+offset*self.radius, y1+offset*self.radius),
            (x1+self.radius, y1),(x1+offset*self.radius,y1-offset*self.radius),
            (x1, y1-self.radius),(x1-offset*self.radius,y1-offset*self.radius)]
        for point in possiblePoints:
            x,y = point
            for obstacle in app.obstacleDictionary[app.level]:
                if obstacle.pointInRectangle(x,y):
                    return True
        return False

    def draw(self,canvas):
        x,y = self.position
        x0 = x-self.radius
        y0 = y-self.radius
        x1 = x+self.radius
        y1 = y+self.radius
        canvas.create_oval(x0,y0,x1,y1,fill=self.fill)

class Player(Entity):
    def __init__(self, fill,speed):
        super().__init__(fill,speed)
        self.position = (60,300)
        self.stealthed = True


class Enemy(Entity):
    PlayersLKP = (0,0)
    def __init__(self,fill, pathType, path,speed):
        super().__init__(fill,speed)
        self.state = "patrolling"
        self.chaseCount = 0
        self.isDetected = False
        self.face = 0
        self.path = path
        self.pathType = pathType
        self.isMoving = False
        self.currentPointIndex = 0
        self.position = path[0]
        self.dPath = 1
        self.turnAngleUnknown = True
        self.turnSpeed = math.pi/180 * 20
        self.turnAngle = 0
        self.turnComplete = False
        self.turnCount = 0
        self.rawTurnAngle = 0
        self.chaseMoveDone = True
        self.faceAngle = 0
        self.visionEndpoints = []

        self.searchPath = []
        self.searchPathFound = False
        self.obstaclePoints = []
        self.openList = []
        self.closedList = []
        self.originalFill = self.fill

        self.patrolPath = path  

        self.printed = False

        self.sweepAngleSet = False
        self.sweepAngle = 0
        self.sweepCount = 0
        self.sweepPath = []
        self.sweepPathFound = False
        self.returnPathFound = False
        self.returnPath = []

    def behave(self,app):
        if self.state == "patrolling":
            self.path = self.patrolPath
            self.followAnyPath(app)
        elif self.state == "chasing":
            self.chase(app)
        elif self.state == "searching":
            self.search(app)
        elif self.state == "sweeping":
            self.sweep(app)
    def castVision(self,app):
        self.visionEndpoints = []
        numLines = 60
        visionLength = 150
        anglePerLine = math.pi/(4*numLines)
        startAngle = self.faceAngle-math.pi/8
        x1, y1 = self.position
        playerX, playerY = app.player.position
        playerDetectSet = set()
        playerInRange = False
        if getDistance(playerX, playerY, x1, y1) <= visionLength + app.player.radius:
            playerInRange = True
        for i in range(numLines):
            newAngle = startAngle+anglePerLine*i
            x2 = x1 + visionLength * math.cos(newAngle)
            y2=y1+visionLength*math.sin(newAngle)
            endPoints = []
            for item in app.obstacleDictionary[app.level]:
                EP = item.collisionCheck(x1, y1, x2, y2, visionLength)
                if EP != None:
                    endPoints.append(EP)
            if endPoints == []:
                self.visionEndpoints.append((x2,y2))
            else:
                x2, y2 = minDistPoint(x1,y1,endPoints)
                self.visionEndpoints.append((x2,y2))
            if playerInRange:
                playerDetectSet.add(self.checkForPlayerInRay(x2, y2, app))
        if True in playerDetectSet:
            return True
        else:
            return False
            

    def checkForPlayerInRay(self, x2, y2, app):
        x1,y1 = self.position
        angle = getAngleBetweenTwoPoints(x1,y1,x2,y2)
        x, y = x1, y1
        totalDistance = getDistance(x1,y1,x2,y2)
        increment = 3
        while(getDistance(x1,y1,x,y)<=totalDistance):
            x1+= increment*math.cos(angle)
            y1+= increment*math.sin(angle)
            x2, y2 = app.player.position
            if getDistance(x1,y1,x2, y2) <= app.player.radius:
                return True
        return False

    def determineTurnAngle(self):
        x1,y1 = self.position
        tempDPath = self.dPath
        nextPointIndex = self.currentPointIndex + tempDPath
        if self.pathType == "wrapped":
            if self.currentPointIndex == 0:
                nextPointIndex = 1
            elif self.currentPointIndex == len(self.path)-1:
                nextPointIndex = len(self.path)-2        
        if self.pathType == "looped" and self.currentPointIndex == len(self.path)-1:
            nextPointIndex = 0
        if len(self.path)==1:
            self.state = "sweeping"
            self.currentPointIndex = 0
            self.sweepCount = 0
            self.dPath = 1
        else:
            x2,y2 = self.path[nextPointIndex]
            self.rawTurnAngle = getAngleBetweenTwoPoints(x1,y1,x2,y2)
            self.turnAngle = turnAngle(self.faceAngle, self.rawTurnAngle)
            self.turnAngleUnknown = False

    def turn(self,dAngle):
        self.faceAngle=fixAngle(self.faceAngle+dAngle) 
        if fixAngle(abs(self.rawTurnAngle-self.faceAngle)) <= 0.01:
            self.turnComplete = True
    
    def move(self, px, py, distance, app):
        x,y = self.position
        if distance <= self.speed:
            movement = distance
        else:
            movement = self.speed
        if distance == 0:
            return
        xDist = px-x
        yDist = py-y
        cos = xDist/distance
        sin = yDist/distance

        dx = cos*movement*0.9
        dy = sin*movement*0.9

        newX = x+dx
        newY = y+dy
        if (newY-self.radius < 0 or newY +self.radius > app.height or 
                newX -self.radius < 0 or newX+self.radius > app.width):
                newX = x
                newY = y
        if self.overlappingObstacle(app, newX, newY):
            newX = x
            newY = y
        self.position = newX,newY
    
    def determinePathBetween2GridPoints(self, app, startRow, startCol, endRow, endCol, badPoints, dirs):
        openList = []
        closedList = []

        startX, startY = app.gridPoints[startRow][startCol]
        endX, endY = app.gridPoints[endRow][endCol]

        startNode = Node((startX,startX),(startRow,startCol))
        endNode = Node((endX,endY),(endRow,endCol))

        openList.append(startNode)

        rows = len(app.gridPoints)
        cols = len(app.gridPoints[0])

        #self,position, rowCol, h = 0,g = 0, parent = None

        for i in range(len(badPoints)):
            row, col = badPoints[i]
            x,y = findClosestGridPoint(row,col,app)
            h = getDistance(x,y,startX,startY)
            g = getDistance(x,y, endX, endY)
            closedList.append(Node((x,y),(row,col),h,g))
        while openList != []:
            currentNode = openList[0]
            currentIndex = 0
            for i in range(len(openList)):
                checkNode = openList[i]
                if checkNode.f < currentNode.f:
                    currentNode = checkNode
                    currentIndex = i
            inClosedList = False
            for node in closedList:
                if node == currentNode:
                    inClosedList = True
            if inClosedList:
                openList.pop(currentIndex)
                continue

            openList.pop(currentIndex)

            closedList.append(currentNode)

            if currentNode == endNode:
                pathNode = currentNode
                path = []
                while pathNode is not None:
                    path.append(pathNode)
                    pathNode = pathNode.parent
                if self.state == "searching":
                    self.searchPath = path[::-1]
                elif self.state == "sweeping":
                    self.returnPath = path[::-1]
                return
            row,col = currentNode.rowCol
            currX, currY = currentNode.position
            for direction in dirs:
                drow, dcol = direction
                newRow = row+drow
                newCol = col+dcol
                if newCol < 0 or newRow < 0 or newRow >= rows or newCol >= cols:
                    continue
                childNode = Node(app.gridPoints[newRow][newCol], (newRow, newCol), parent = currentNode)
                inClosedList = False
                for node in closedList:
                    if childNode == node:
                        inClosedList = True
                if inClosedList:
                    continue
                childNode = Node(app.gridPoints[newRow][newCol], (newRow, newCol), parent = currentNode)
                cx,cy = childNode.position
                childNode.g = getDistance(cx,cy,currX,currY) + currentNode.g
                childNode.h = getDistance(cx,cy, endX, endY)
                if childNode == endNode:
                    childNode.f = 0
                inOpenList = False
                for node in openList:
                    if childNode == node and childNode.g > node.g:
                        inOpenList = True

                if not(inClosedList or inOpenList):
                    openList.append(childNode)
  
    def pathFindToPlayer(self,app):
        badPoints = []
        for row in range(len(app.gridPoints)):
            for col in range(len(app.gridPoints[0])):
                x1,y1 = app.gridPoints[row][col]
                for obstacle in app.obstacleDictionary[app.level]:
                    if obstacle.pointInRectangle(x1,y1):
                        badPoints.append((row,col))
        if not self.searchPathFound:
            x,y = self.position
            row1,col1 = findClosestGridRowCol(app, x,y)
            x2,y2 = self.PlayersLKP
            row2,col2 = findClosestGridRowCol(app, x2, y2)
            dirs = [ (-1, 0),
                    (0,-1),            (0,1),
                       (1,0)]
            self.determinePathBetween2GridPoints(app,row1,col1,row2,col2,badPoints, dirs)
            self.searchCount = 0
            self.currentPointIndex = 0
            self.searchPathFound = True
            self.dPath = 1
        else:
            self.path = []
            for node in self.searchPath:
                row,col = node.rowCol
                x = (col+1)*60
                y = (row+1)*60
                self.path.append((x,y))
            self.followAnyPath(app)
    
    def determineSweepPath(self, app):
        startX, startY = self.position
        startRow, startCol = findClosestGridRowCol(app, startX, startY)
        distance = 3
        badPoints = []
        for row in range(len(app.gridPoints)):
            for col in range(len(app.gridPoints[0])):
                x1,y1 = app.gridPoints[row][col]
                for obstacle in app.obstacleDictionary[app.level]:
                    if obstacle.pointInRectangle(x1,y1):
                        badPoints.append((row,col))
        endRow, endCol = getRandomNearbyPoint(app, distance, startRow, startCol, badPoints)
        dirs = [ (-1, 0),
                    (0,-1),            (0,1),
                       (1,0)]
        self.determinePathBetween2GridPoints(app, startRow, startCol, endRow, endCol, badPoints, dirs)

    def determineReturnPath(self,app):
        x,y = self.position
        row1,col1 = findClosestGridRowCol(app, x,y)
        x2,y2 = self.patrolPath[0]
        row2,col2 = findClosestGridRowCol(app, x2, y2)
        dirs = [ (-1, 0),
                (0,-1),            (0,1),
                       (1,0)]
        badPoints = []
        for row in range(len(app.gridPoints)):
            for col in range(len(app.gridPoints[0])):
                x1,y1 = app.gridPoints[row][col]
                for obstacle in app.obstacleDictionary[app.level]:
                    if obstacle.pointInRectangle(x1,y1):
                        badPoints.append((row,col))
        self.determinePathBetween2GridPoints(app,row1,col1,row2,col2,badPoints, dirs)
        self.searchCount = 0
        self.currentPointIndex = 0
        self.dPath = 1
    def dumpState(self):
        print("******************************************")
        print(self.fill)
        print(self.state)
        print(self.path)
        print(self.currentPointIndex)

        
    
    ############################# Behavioral functions #########################
    
    def followAnyPath(self, app):
        if self.castVision(app):
            self.state="chasing"
            self.currentPointIndex = 0
            self.dPath = 1
            self.chaseCount = 0
            return
        
        if self.currentPointIndex >= len(self.path) and self.state == "searching":
            self.state = "sweeping"
            self.sweepCount = 0
            self.currentPointIndex = 0
            self.searchPathFound = False
            self.dPath = 1
            return
        point = self.path[self.currentPointIndex]
        x,y = self.position
        px, py = point
        maxDistance = 1

        distance = getDistance(x,y,px,py)
        if distance <= maxDistance:
            if(self.turnAngleUnknown):
                self.determineTurnAngle()
            elif(not self.turnComplete):
                remainingAngle = fixAngle(self.rawTurnAngle-self.faceAngle)
                if abs(remainingAngle) <= abs(self.turnSpeed):
                    dAngle = remainingAngle
                else:
                    if remainingAngle > 0:
                        dAngle = self.turnSpeed
                    else:
                        dAngle = -self.turnSpeed
                self.turn(dAngle)
            else:
                self.currentPointIndex += self.dPath
                if self.state != "searching":
                    if self.pathType == "looped":
                        self.currentPointIndex = self.currentPointIndex%len(self.path)
                    elif ((self.currentPointIndex == len(self.path)-1 or 
                    self.currentPointIndex == 0) and self.pathType == "wrapped"):
                        self.dPath *= -1
        else:
            self.turnAngleUnknown = True
            self.turnComplete = False
            self.move(px, py, distance, app)
        

    def chase(self, app):
        if self.castVision(app):
            Enemy.PlayersLKP = app.player.position
            x1,y1 = self.position
            alertDistance = 1000
            for enemy in app.enemyDictionary[app.level]:
                x2,y2 = enemy.position
                if getDistance(x1,y1,x2,y2) <= alertDistance:
                    if enemy.state != "chasing":
                        enemy.state = "searching"
            x1,y1 = self.position
            x2,y2 = app.player.position
            self.targetPosition = x2,y2
            self.rawTurnAngle = getAngleBetweenTwoPoints(x1,y1,x2,y2)
            self.turnAngle = turnAngle(self.faceAngle, self.rawTurnAngle)
            self.chaseTurnDone = False
            if abs(self.turnAngle) < self.turnSpeed:
                dAngle = self.turnSpeed - abs(self.turnAngle)
            else:
                dAngle = self.turnSpeed
            if self.turnAngle < 0:
                dAngle = -1*dAngle
            self.turn(dAngle)
            
            x1,y1 = self.position
            x2,y2 = self.targetPosition
            maxDistance = self.radius + 5
            distance = getDistance(x1,y1,x2,y2)
            if not distance <= maxDistance:
                self.move(x2,y2, distance, app)
            self.chaseCount += 1
        else:
            self.currentPointIndex = 0
            self.dPath = 1
            self.state = "searching"
            self.searchPathFound = False
    
    def search(self, app):
        if self.castVision(app):
            self.currentPointIndex = 0
            self.dPath = 1
            self.state = "chasing"
        else:
            self.pathFindToPlayer(app)
    
    def sweep(self, app):
        if self.castVision(app):
            self.currentPointIndex = 0
            self.dPath = 1
            self.state = "chasing"
            return
        if not self.sweepAngleSet:
            self.sweepAngle = fixAngle(self.faceAngle + math.pi)
            self.sweepCount += 1
            self.sweepAngleSet = True
        elif self.sweepCount <= 2:
            remainingAngle = fixAngle(self.sweepAngle-self.faceAngle)
            if abs(remainingAngle) <= abs(self.turnSpeed):
                dAngle = remainingAngle
            else:
                if remainingAngle > 0:
                    dAngle = self.turnSpeed
                else:
                    dAngle = -self.turnSpeed
            self.turn(dAngle)
            if abs(fixAngle(self.sweepAngle - self.faceAngle)) <= 0.1:
                self.sweepAngleSet = False
                self.sweepCount += 1
        else:
            x,y = self.position
            x1,y1 = self.patrolPath[0]
            if not self.returnPathFound:
                #self.determineSweepPath(app)
                #self.sweepPathFound = True
                self.determineReturnPath(app)
                self.currentPointIndex = 0
                self.dPath = 1
                self.returnPathFound = True
                self.path = []
                for node in self.returnPath:
                    row,col = node.rowCol
                    x = (col+1)*60
                    y = (row+1)*60
                    self.path.append((x,y))
            elif not (getDistance(x,y,x1,y1) <= 1):
                self.followAnyPath(app)
            else:
                self.currentPointIndex = 0
                self.returnPathFound = False
                self.dPath = 1
                self.path = self.patrolPath
                self.state = "patrolling"
                return



        
        
        

    
        
def timerFired(app):
    determineVisionCones(app)
    for enemy in app.enemyDictionary[app.level]:
        enemy.behave(app)


def mousePressed(app, event):
    print(event.x, event.y)
    for enemy in app.enemyDictionary[app.level]:
        x1,y1 = enemy.position
        if getDistance(event.x,event.y,x1,y1) <= enemy.radius:
            enemy.dumpState()

def appStarted(app):
    app.gridPoints = []
    for y in range(1,app.height//60):
        row = []
        for x in range(1,app.width//60):
            row.append((x*60,y*60))
        app.gridPoints.append(row)

    app.player = Player("blue",10)
    app.level = 0
    app.timerDelay = 60

    #################    Level Dictionaries ####################################

    app.enemyDictionary = {0: [], 1: []}
    app.obstacleDictionary = {0: [], 1:[]}
    ####   Enemies 
    # Level 0
    app.enemyDictionary[0].append(Enemy("red", "wrapped",
        [(60,60),(840,60)],15))
    app.enemyDictionary[0].append(Enemy("yellow", "wrapped",
        [(120,480),(300, 480),(300,540),(120,540)],15))
    #app.enemyDictionary[0].append(Enemy("Blue","wrapped",[(41,343),(537,343)],8))
    #app.enemyDictionary[0].append(Enemy("green", "wrapped",
    #    [(60,540),(840,540)],10))
    app.enemyDictionary[0].append(Enemy("Blue", "wrapped", [(480, 540), (540, 540), (600, 540), (660, 540), (660, 480), (660, 420), (660, 360), (660, 300), (660, 240), (720, 240), (780, 240), (780, 180), (780, 120), (780, 60), (720, 60), (660, 60), (600, 60), (540, 60), (480, 60)], 15))
    ####  Obstacles [shape, [coordinates], color]
    app.obstacleDictionary[0].append(rectangle(150,150,750,210,"blue"))
    app.obstacleDictionary[0].append(rectangle(390,270,630,510,"green"))

    app.obstacleDictionary[0].append(rectangle(0,0,app.width,30,"grey"))
    app.obstacleDictionary[0].append(rectangle(0,app.height-30,app.width,app.height,"grey"))
    app.obstacleDictionary[0].append(rectangle(0,30,30,app.height-30,"grey"))
    app.obstacleDictionary[0].append(rectangle(app.width-30,30,app.width,app.height-30,"grey"))



def determineVisionCones(app):                        
    playerDetectSet = set()
    app.player.isDetected = False
    for enemy in app.enemyDictionary[app.level]:
        playerDetectSet.add(enemy.castVision(app))
    if True in playerDetectSet:
        app.player.isDetected = True
    else:
        app.player.isDetected = False

def drawVisionCones(app, canvas):
    for enemy in app.enemyDictionary[app.level]:
        x1,y1 = enemy.position
        for i in range(len(enemy.visionEndpoints)):
            x2,y2 = enemy.visionEndpoints[i]
            canvas.create_line(x1,y1,x2,y2, width = 2, fill = "yellow")    
            

def keyPressed(app, event):
    direction = None
    if event.key == "Up":
        direction = (0,-1)
    elif event.key == "Down":
        direction = (0,1)
    elif event.key == "Right":
        direction = (1,0)
    elif event.key == "Left":
        direction = (-1,0)
    if direction != None:
        app.player.move(direction,app)

def drawObstacles(app, canvas):
    for item in app.obstacleDictionary[app.level]:
        item.draw(canvas)


def redrawAll(app, canvas):
    drawObstacles(app, canvas)
    drawVisionCones(app,canvas)

    for enemy in app.enemyDictionary[app.level]:
        enemy.draw(canvas)
    app.player.draw(canvas)
    for row in range(len(app.gridPoints)):
        for col in range(len(app.gridPoints[0])):
            x,y = app.gridPoints[row][col]
            canvas.create_oval(x-5,y-5,x+5,y+5,fill = "red")
runApp(width=900, height=600)