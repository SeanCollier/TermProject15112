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
    elif dx>0:
        if dy>0:
            result = math.atan(dy/dx)
        else:
            result = -math.atan(dy/dx)
    else:
        if dy>=0:
            result = math.pi-math.atan(-dy/dx)
        else:
            result = math.pi+math.atan(dy/dx)
    return result

def determineTurnAngle(faceAngle, targetAngle):
    resAngle = faceAngle-targetAngle
    if abs(resAngle)>=math.pi/2:
        resAngle = -1*(2*math.pi-resAngle)
    return resAngle

#######################################################################################################

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

class Enemy(Entity):
    def __init__(self,fill, pathType, path,speed):
        super().__init__(fill,speed)
        self.face = 0
        self.path = path
        self.pathType = pathType
        self.isMoving = False
        self.currentPointIndex = 0
        self.position = path[0]
        self.dPath = 1
        self.turnAngleUnknown = True
        self.turnFrames = 8
        self.turnAngle = 0
        self.turnComplete = False
        self.turnCount=0
        x1,y1 = self.position
        x2,y2 = self.path[1]
        self.faceAngle = getAngleBetweenTwoPoints(x1,y1,x2,y2)
    def moveRandomly(self):
        dx = random.randint(-1,1)
        dy = random.randint(-1,1)
        direction = dx,dy
        self.move(direction)
    def determineTurnAngle(self):
        x1,y1 = self.position
        tempDPath = self.dPath
        nextPointIndex = self.currentPointIndex + tempDPath
        print(f"currIndex: {self.currentPointIndex}, lenPath: {len(self.path)}")
        if self.pathType == "wrapped":
            if self.currentPointIndex == 0:
                nextPointIndex = 1
            elif self.currentPointIndex == len(self.path)-1:
                nextPointIndex = len(self.path)-2        
        if self.pathType == "looped" and self.currentPointIndex == len(self.path)-1:
            nextPointIndex = 0
        print(f"nextIndex:{nextPointIndex}")
        x2,y2 = self.path[nextPointIndex]
        rawTurnAngle = getAngleBetweenTwoPoints(x1,y1,x2,y2)
        print(f"Enemy: {self.fill}, faceAngle, rawAngle: {self.faceAngle},{rawTurnAngle}")
        self.turnAngle = determineTurnAngle(self.faceAngle, rawTurnAngle)
        self.turnAngleUnknown = False
    def turn(self,dAngle):
        if(self.turnCount >= self.turnFrames):
            self.turnCount=0
            self.turnComplete = True
            return
        else:
            self.turnCount += 1
            self.faceAngle += dAngle
            self.faceAngle %= 2*math.pi

    def followPath(self):
        point = self.path[self.currentPointIndex]
        x,y = self.position
        px, py = point
        maxDistance = 10
        distance = getDistance(x,y,px,py)
        if distance <= maxDistance:
            if(self.turnAngleUnknown):
                self.determineTurnAngle()
            elif(not self.turnComplete):
                dAngle = self.turnAngle/self.turnFrames
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

        
        
        
def timerFired(app):
    for enemy in app.enemies:
        enemy.followPath()


def mousePressed(app, event):
    print(event.x, event.y)

def appStarted(app):
    app.player = Player("blue",10)
    app.timerDelay = 50
    app.enemies = []
    app.enemies.append(Enemy("red", "looped",
        [(50,47), (303,47), (502,191), (289, 335), (62, 351)],8))
    app.enemies.append(Enemy("green", "wrapped",
        [(114,89),(320,180),(143,264),(338,358),(498,231),(408,164),(506,79)],
            8))
def drawVisionCones(app,canvas):
    numLines = 40
    visionLength = 100
    anglePerLine = math.pi/(4*numLines)
    for enemy in app.enemies:
        startAngle = enemy.faceAngle-math.pi/8
        for i in range(numLines):
            x1, y1 = enemy.position
            newAngle = startAngle+anglePerLine*i
            x2 = x1+visionLength*math.cos(newAngle)
            y2=y1+visionLength*math.sin(newAngle)
            canvas.create_line(x1,y1,x2,y2,width = 2, fill = "yellow")
            

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

def redrawAll(app, canvas):
    drawVisionCones(app,canvas)

    for enemy in app.enemies:
        enemy.draw(canvas)
        app.player.draw(canvas)
runApp(width=600, height=400)