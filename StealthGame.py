from cmu_112_graphics import *
import random
import math


#################################        Math Helpers           #######################################

def getDistance(x0,y0,x1,y1):
    return ((x0-x1)**2+(y0-y1)**2)**0.5

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
    return result

def turnAngle(faceAngle, targetAngle):
    resAngle = targetAngle-faceAngle
    if resAngle <0:
        resAngle = resAngle+2*math.pi
    if resAngle>=math.pi:
        resAngle = -1*(2*math.pi-resAngle)
    return resAngle

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

#######################################################################################################

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
    
    def move(self, direction):
        x,y = self.position
        dx, dy = direction
        dx *= self.speed
        dy *= self.speed
        x+=dx
        y+=dy
        self.position = x,y

    def draw(self,canvas):
        x0 = self.position[0]-self.radius
        y0 = self.position[1]-self.radius
        x1 = self.position[0]+self.radius
        y1 = self.position[1]+self.radius
        canvas.create_oval(x0,y0,x1,y1,fill=self.fill)

class Player(Entity):
    def __init__(self, fill,speed):
        super().__init__(fill,speed)
        self.position = (200,200)
        self.stealthed = True

class Enemy(Entity):
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
        self.turnSpeed = math.pi/180 * 10
        self.turnAngle = 0
        self.turnComplete = False
        self.turnCount = 0
        self.rawTurnAngle = 0
        self.chaseMoveDone = True
        self.LKPlayerPos = (0,0)
        self.LKPlayerSpeed = (0,0)

        x1,y1 = self.position
        x2,y2 = self.path[1]
        self.faceAngle = 0
        self.visionEndpoints = []
    def behave(self,app):
        if self.state == "patrolling":
            self.followPath(app)
        elif self.state == "chasing":
            self.chase(app)
    def moveRandomly(self):
        dx = random.randint(-1,1)
        dy = random.randint(-1,1)
        direction = dx,dy
        self.move(direction)
    def castVision(self,app):
        self.visionEndpoints = []
        numLines = 40
        visionLength = 100
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
        x2,y2 = self.path[nextPointIndex]
        self.rawTurnAngle = getAngleBetweenTwoPoints(x1,y1,x2,y2)
        self.turnAngle = turnAngle(self.faceAngle, self.rawTurnAngle)
        self.turnAngleUnknown = False

    def turn(self,dAngle):
        if self.rawTurnAngle < 0:
            self.rawTurnAngle += 2*math.pi
        if self.faceAngle < 0:
            self.faceAngle += 2*math.pi
        self.faceAngle += dAngle
        turnAngleModded = self.turnAngle % (2*math.pi)
        self.faceAngle %= (2*math.pi)
        self.rawTurnAngle %= (2*math.pi)
        if abs(self.rawTurnAngle - self.faceAngle) <= 0.1:
            self.turnComplete = True
    
    def move(self, px, py, distance):
        x,y = self.position
        if distance <= self.speed:
                movement = distance
        else:
            movement = self.speed
        xDist = px-x
        yDist = py-y
        cos = xDist/distance
        sin = yDist/distance

        dx = cos*movement
        dy = sin*movement

        x+= dx
        y+= dy
        self.position = x,y

        
    
    ############################# Behavioral functions #########################

    def followPath(self, app):
        if self.castVision(app):
            self.state="chasing"
            self.chaseCount = 0
            return
        point = self.path[self.currentPointIndex]
        x,y = self.position
        px, py = point
        maxDistance = 10
        distance = getDistance(x,y,px,py)
        if distance <= maxDistance:
            if(self.turnAngleUnknown):
                self.determineTurnAngle()
            elif(not self.turnComplete):
                if abs(self.turnAngle) <= abs(self.turnSpeed):
                    dAngle = abs(self.turnAngle-self.faceAngle)
                else:
                    dAngle = self.turnSpeed
                if self.turnAngle != 0:
                    if dAngle/self.turnAngle <= 0:
                        dAngle *= -1
                self.turn(dAngle)
            else:
                self.currentPointIndex += self.dPath
                if self.pathType == "looped":
                    self.currentPointIndex = self.currentPointIndex%len(self.path)
                elif ((self.currentPointIndex == len(self.path)-1 or 
                self.currentPointIndex == 0) and self.pathType == "wrapped"):
                    self.dPath *= -1
        else:
            self.turnAngleUnknown = True
            self.turnComplete = False
            self.move(px, py, distance)
        

    def chase(self, app):
        if self.castVision(app):
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
                self.move(x2,y2, distance)
            self.chaseCount += 1
        
def timerFired(app):
    determineVisionCones(app)
    for enemy in app.enemyDictionary[app.level]:
        enemy.behave(app)


def mousePressed(app, event):
    print(event.x, event.y)

def appStarted(app):
    app.player = Player("blue",10)
    app.level = 0
    app.timerDelay = 60

    #################    Level Dictionaries ####################################

    app.enemyDictionary = {0: [], 1: []}
    app.obstacleDictionary = {0: [], 1:[]}
    ####   Enemies 
    # Level 0
    app.enemyDictionary[0].append(Enemy("red", "looped",
        [(50,47), (303,47), (502,191), (289, 335), (62, 351)],8))
    #app.enemyDictionary[0].append(Enemy("red", "looped",
    #    [(41,33),(537, 33)],8))
    #app.enemyDictionary[0].append(Enemy("Blue","wrapped",[(41,343),(537,343)],8))
    app.enemyDictionary[0].append(Enemy("green", "wrapped",
        [(114,89),(320,180),(143,264),(338,358),(498,231),(408,164),(506,79)],
            8))

    ####  Obstacles [shape, [coordinates], color]
    app.obstacleDictionary[0].append(rectangle(50,50,200,200,"blue"))
    app.obstacleDictionary[0].append(rectangle(250,10,350,100,"green"))




def determineVisionCones(app):                        
    playerDetectSet = set()
    app.player.isDetected = False
    for enemy in app.enemyDictionary[app.level]:
        playerDetectSet.add(enemy.castVision(app))
    if True in playerDetectSet:
        app.player.isDetected = True
    else:
        app.player.isDetected = False
    if app.player.isDetected:
        app.player.fill = "green"
    else:
        app.player.fill = "blue"

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
        app.player.move(direction)

def drawObstacles(app, canvas):
    for item in app.obstacleDictionary[app.level]:
        item.draw(canvas)


def redrawAll(app, canvas):
    drawObstacles(app, canvas)
    drawVisionCones(app,canvas)

    for enemy in app.enemyDictionary[app.level]:
        enemy.draw(canvas)
    app.player.draw(canvas)
runApp(width=600, height=400)