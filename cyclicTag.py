from __future__ import division
import pygame, sys
from pygame.locals import *
pygame.init()

""" cyclicTag.py
by Eric J.Parfitt (ejparfitt@gmail.com)

This program was primarily made to demonstrate a "physical" system that
emulates a cyclic tag machine.  However, it also can be used for
generally constructiong "rube-golberg" style constructions made up of
simple parts, namely balls, inclines, seesaws, and ropes.  One advantage
this particular setup might have over others is that all objects move
in clearly discrete steps, which makes it easier to get the exact
behavior one is looking for, perhaps with less trial-and-error.

Version: 1.0 alpha
"""

WIDTH = 1200
HEIGHT = 950

windowSurface = pygame.display.set_mode((WIDTH, HEIGHT), 0, 32)

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BROWN = (150, 75, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
WHITEFILL = 0

STANDARD_BALL_RADIUS = 12.5
STANDARD_BALL_DIAMETER = 2 * STANDARD_BALL_RADIUS
INCLINE_SLOPE = .5
BALL_SPACING = 6
INITIAL_X = 860
INITIAL_Y = 120
BALL0RADIUS = 10
BALL1RADIUS = 12.5
SPACER_BALL_RADIUS = 8

RulePartA = [1]
RulePartB = [1,0,1]

RULE_BALL_NUMBER = 180

clock = pygame.time.Clock()

class AMass():
    
    def __init__ (self, myXCo, myYCo):
        self.xCo = myXCo
        self.yCo = myYCo
        
    def setLocation(self, myXCo, myYco):
        self.xCo = myXCo
        self.yCo = myYCo

class Incline(AMass):
    
    def __init__ (self, myXCo, myYCo, myLength, myIsRightUp):
        AMass.__init__(self, myXCo, myYCo)
        self.length = myLength
        self.isRightUp = myIsRightUp
        self.leftX = myXCo - myLength * INCLINE_SLOPE
        self.rightX = myXCo + myLength * INCLINE_SLOPE
        self.update(myYCo, myLength)
        self.yCo = myYCo
        self.length = myLength
        
    def update(self, myYCo, myLength):
        if self.isRightUp:
            self.leftY = myYCo + myLength * INCLINE_SLOPE / 2
            self.rightY = myYCo - myLength * INCLINE_SLOPE / 2
        else:
            self.leftY = myYCo - myLength * INCLINE_SLOPE / 2
            self.rightY = myYCo + myLength * INCLINE_SLOPE / 2
        self.slope = (self.rightY - self.leftY) / (self.rightX - self.leftX)
        
    def getY(self, x):
        return (self.slope * (x - self.leftX) + self.leftY)
    
    def draw(self):
        pygame.draw.line(windowSurface, BLACK, [self.leftX, self.leftY],
                [self.rightX, self.rightY])

class Seesaw(Incline):
    
    def __init__ (self, myXCo, myYCo, myIsRightUp, myIsBallSwitchable):
        Incline.__init__(self, myXCo, myYCo, 80, myIsRightUp)
        self.isBallSwitchable = myIsBallSwitchable
        
    def rightDown(self):
        if(self.isRightUp):
            self.isRightUp = False
            
    def leftDown(self):
        if(not self.isRightUp):
            self.isRightUp = True
            
    def switch(self):
        self.isSwitched = True
        self.isRightUp = not self.isRightUp
        self.update(self.yCo, self.length)
        
    def draw(self):
        if self.isBallSwitchable:
            color = BLUE
        else:
            color = GREEN
        pygame.draw.line(windowSurface, color, [self.leftX, self.leftY],
                [self.rightX, self.rightY])

class Ball(AMass):

    def __init__ (self, myXCo, myYCo, myRadius, myColor):
        AMass.__init__(self, myXCo, myYCo)
        self.radius = myRadius
        self.standardRadius = STANDARD_BALL_RADIUS
        self.diameter = 2 * self.radius
        self.standardDiameter = STANDARD_BALL_DIAMETER
        self.color = myColor
        
    def fall(self):
        self.yCo += self.standardDiameter
        
    def draw(self):
        if self.color == WHITEFILL:
            pygame.draw.ellipse(windowSurface, BLACK, [self.xCo - self.radius,
                    self.yCo - self.radius, self.diameter, self.diameter], 1)
        else:
            pygame.draw.ellipse(windowSurface, self.color,
                    [self.xCo - self.radius,self.yCo - self.radius,
                    self.diameter, self.diameter])

class Rope():
    
    def __init__ (self, myMassA, myIsRightA, myMassB, myIsRightB):
        self.massA = myMassA
        self.isRightA = myIsRightA
        self.massB = myMassB
        self.isRightB = myIsRightB
        self.update(myMassA, myMassB, self.isRightA, self.isRightB)
        self.isSwitched = False
        
    def update(self, myMassA, myMassB, isRightA, isRightB):
        if isRightA:
            self.sideAX = myMassA.rightX
            self.sideAY = myMassA.rightY
        else:
            self.sideAX = myMassA.leftX
            self.sideAY = myMassA.leftY
        if isRightB:
            self.sideBX = myMassB.rightX
            self.sideBY = myMassB.rightY
        else:
            self.sideBX = myMassB.leftX
            self.sideBY = myMassB.leftY
            
    def draw(self):
        self.update(self.massA, self.massB, self.isRightA, 
                self.isRightB)
        pygame.draw.line(windowSurface, RED, [self.sideAX, self.sideAY],
                [self.sideBX, self.sideBY])

def checkKey():
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

def draw():
    windowSurface.fill(WHITE)
    for seesaw in seesaws:
        seesaw.draw()
    for ball in balls:
        ball.draw()
    for rope in ropes:
        rope.draw()
    for ramp in ramps:
        ramp.draw()
    pygame.display.flip()

def drawGrid():
    breakSize = 100
    length = 1200
    for i in range(13):
        pygame.draw.line(windowSurface, GREEN, [i * breakSize, 0],
                [i * breakSize, length])
        pygame.draw.line(windowSurface, GREEN, [0, i * breakSize], 
                [length, i * breakSize])
    

def update():
    clock.tick(30)
    isBallRight = False
    isBallLeft = False
    for seesaw in seesaws:
        seesaw.isSwitched = False
    for i in range(len(balls)):
        ball = balls[i]
        ballBs = []
        for j in range(len(balls)):
            if not i == j:
                ballBs.append(balls[j])
        foundIncline = False
        
        for ramp in ramps:
            for seesaw in seesaws:
                isFarRight = (ball.xCo >= seesaw.rightX +
                        ball.standardRadius and ball.xCo < seesaw.rightX + 3 *
                        ball.standardRadius and ball.yCo -
                        ball.standardRadius < seesaw.rightY and ball.yCo +
                        ball.standardRadius > seesaw.rightY)
                isFarLeft = (ball.xCo <= seesaw.leftX - ball.standardRadius and
                        ball.xCo > seesaw.leftX - 3 * ball.standardRadius and
                        ball.yCo - ball.standardRadius < seesaw.leftY and
                        ball.yCo + ball.standardRadius > seesaw.leftY)
                if isFarLeft or isFarRight:
                    break
            isOverRamp = ((ball.xCo + ball.radius > ramp.leftX) and
                    (ball.xCo - ball.radius < ramp.rightX))
            isNearRamp = ((ball.yCo >= (ramp.getY(ball.xCo) -
                    3 * ball.standardRadius))and (ball.yCo <
                    (ramp.getY(ball.xCo) - ball.standardRadius)))
            isBallRight = isBallLeft = isRightBallYMatch = isLeftBallYMatch = \
                    False
            for ballB in ballBs:
                if not (isBallRight and isRightBallYMatch):
                    isBallRight = (ballB.xCo >= ball.xCo +
                            ball.standardDiameter and ballB.xCo <
                            ball.xCo + 2 * ball.standardDiameter)
                    isRightBallYMatch =     (ball.yCo <= ballB.yCo +
                            ball.standardDiameter and ball.yCo >= ballB.yCo -
                            ball.standardDiameter)
                    if isBallRight and isRightBallYMatch:
                        rightBall = ballB
                if not (isBallLeft and isLeftBallYMatch):
                    isBallLeft = (ballB.xCo <= ball.xCo - 
                            ball.standardDiameter and ballB.xCo >
                            ball.xCo - 2 * ball.standardDiameter)
                    isLeftBallYMatch = (ball.yCo <= ballB.yCo +
                            ball.standardDiameter and ball.yCo >=
                            ballB.yCo - ball.standardDiameter)          
                    if isBallLeft and isLeftBallYMatch:
                        leftBall = ballB
            if isOverRamp and (ball.yCo == ramp.getY(ball.xCo) -
                               ball.standardRadius):
                foundIncline = True
                if ramp.isRightUp:
                    if isFarRight:
                        ball.xCo = seesaw.rightX + ball.standardRadius 
                    elif isBallLeft and isLeftBallYMatch:
                        ball.xCo = leftBall.xCo + ball.standardDiameter
                    else:
                        ball.xCo -= ball.diameter
                else:
                    if isFarLeft :
                        ball.xCo = seesaw.leftX - ball.standardRadius
                    elif isBallRight and isRightBallYMatch:
                        ball.xCo = rightBall.xCo - ball.standardDiameter
                    else:
                        ball.xCo += ball.diameter
            isOverRamp = ((ball.xCo + ball.radius > ramp.leftX) and
                            (ball.xCo - ball.radius < ramp.rightX))
            isNearRamp = ((ball.yCo >= (ramp.getY(ball.xCo) -
                            3 * ball.standardRadius))and (ball.yCo <
                            (ramp.getY(ball.xCo) - ball.standardRadius)))
            if isNearRamp and isOverRamp:
                ball.yCo = ramp.getY(ball.xCo) - ball.standardRadius
                foundIncline = True
                ball.yCo = ramp.getY(ball.xCo) - ball.standardRadius
                foundIncline = True
            isOverRamp = ((ball.xCo + ball.radius > ramp.leftX) and
                            (ball.xCo - ball.radius < ramp.rightX))                    
            if foundIncline:
                break
        if not isOverRamp:
            foundIncline = False
            for ramp in ramps:
                isOverRamp = ((ball.xCo + ball.radius > ramp.leftX) and
                        (ball.xCo - ball.radius < ramp.rightX))
                isNearRamp = ((ball.yCo >= (ramp.getY(ball.xCo) -
                            3 * ball.standardRadius))and (ball.yCo <
                            (ramp.getY(ball.xCo) - ball.standardRadius)))
                if isOverRamp and isNearRamp:
                    foundIncline = True
    
        foundSeesaw = False
        for seesaw in seesaws:
            if not foundIncline:
                isOverSeesaw = ((ball.xCo + ball.radius > seesaw.leftX) and
                                (ball.xCo - ball.radius < seesaw.rightX))
                isNearSeesaw = ((ball.yCo >= (seesaw.getY(ball.xCo) -
                                3 * ball.standardRadius))and (ball.yCo <
                                (seesaw.getY(ball.xCo) - ball.standardRadius)))
                isRight = ball.xCo >= seesaw.xCo
                if isNearSeesaw and isOverSeesaw:
                    ball.yCo = seesaw.getY(ball.xCo) - ball.standardRadius
                    foundSeesaw = True
                if isOverSeesaw and (ball.yCo == seesaw.getY(ball.xCo) -
                                ball.standardRadius):
                    if isRight:
                        if seesaw.isRightUp:
                            if seesaw.isBallSwitchable:
                                seesaw.switch()
                            else: 
                                ball.xCo -= ball.diameter
                        else:
                            ball.xCo += ball.diameter
                    else:
                        if seesaw.isRightUp:
                            ball.xCo -= ball.diameter
                        else:
                            if seesaw.isBallSwitchable:
                                seesaw.switch()
                            else:
                                ball.xCo += ball.diameter
                    ball.yCo = seesaw.getY(ball.xCo) - ball.standardRadius
                    foundSeesaw = True
                if foundSeesaw:
                    break
        if not (foundIncline or foundSeesaw):
            ball.fall()
    isLoop = True
    while isLoop:
        isLoop = False
        for rope in ropes:
            if rope.isRightA:
                massAX = rope.massA.rightX
                massAY = rope.massA.rightY
            else:
                massAX = rope.massA.leftX
                massAY = rope.massA.leftY
            if rope.isRightB:
                massBX = rope.massB.rightX
                massBY = rope.massB.rightY
            else:
                massBX = rope.massB.leftX
                massBY = rope.massB.leftY
            isAOverB = massAY < massBY
            isLoop = False
            if rope.massA.isSwitched:
                if isAOverB:
                    if rope.isRightA == rope.massA.isRightUp:
                        if rope.isRightB != rope.massB.isRightUp:
                            rope.massB.switch()
                            isLoop = True
                            break
                else:
                    if rope.isRightA != rope.massA.isRightUp:
                        if rope.isRightB == rope.massB.isRightUp:
                            rope.massB.switch()
                            isLoop = True
                            break
            elif rope.massB.isSwitched:
                if isAOverB:
                    if rope.isRightA == rope.massA.isRightUp:
                        if rope.isRightB != rope.massB.isRightUp:
                            rope.massA.switch()
                            isLoop = True
                            break
                else:
                    if rope.isRightA != rope.massA.isRightUp:
                        if rope.isRightB == rope.massB.isRightUp:
                            rope.massA.switch()
                            isLoop = True
                            break
ruleArray = []
ballCount = 0
while(True):
    if ballCount == RULE_BALL_NUMBER:
            break
    for ball in RulePartA:
        if ball == 0:
            color = WHITEFILL
            size = BALL0RADIUS
        else:
            color = BLACK
            size = BALL1RADIUS
        ruleArray.append(Ball(INITIAL_X + ballCount *
                STANDARD_BALL_DIAMETER + BALL_SPACING, INITIAL_Y - ballCount *
                STANDARD_BALL_DIAMETER * INCLINE_SLOPE + BALL_SPACING *
                INCLINE_SLOPE, size, color))
        ballCount += 1
        if ballCount == RULE_BALL_NUMBER:
            break
    if ballCount == RULE_BALL_NUMBER:
            break
    ruleArray.append(Ball(INITIAL_X + ballCount *
            STANDARD_BALL_DIAMETER + BALL_SPACING, INITIAL_Y - ballCount *
            STANDARD_BALL_DIAMETER * INCLINE_SLOPE + BALL_SPACING *
            INCLINE_SLOPE, SPACER_BALL_RADIUS, BLUE))
    ballCount += 1
    if ballCount == RULE_BALL_NUMBER:
            break
    for ball in RulePartB:
        if ball == 0:
            color = WHITEFILL
            size = BALL0RADIUS
        else:
            color = BLACK
            size = BALL1RADIUS
        ruleArray.append(Ball(INITIAL_X + ballCount *
                STANDARD_BALL_DIAMETER + BALL_SPACING, INITIAL_Y - ballCount *
                STANDARD_BALL_DIAMETER * INCLINE_SLOPE + BALL_SPACING *
                INCLINE_SLOPE, size, color))
        ballCount += 1
        if ballCount == RULE_BALL_NUMBER:
            break
    if ballCount == RULE_BALL_NUMBER:
            break
    ruleArray.append(Ball(INITIAL_X + ballCount * STANDARD_BALL_DIAMETER +
            BALL_SPACING, INITIAL_Y - ballCount * STANDARD_BALL_DIAMETER *
            INCLINE_SLOPE + BALL_SPACING * INCLINE_SLOPE, SPACER_BALL_RADIUS,
            BLUE))
    ballCount += 1
    if ballCount == RULE_BALL_NUMBER:
            break

seesaws = [Seesaw(190, 490, True, True), Seesaw(195, 550, True, True),
        Seesaw(295, 675, True, True), Seesaw(400, 730, False, True),
        Seesaw(700, 275, True, False), Seesaw(780, 125, False, True),
        Seesaw(855, 195, True, True), Seesaw(820, 850, False, True)]
balls = [Ball(270, 500, 12.5, BLACK)]
for ball in ruleArray:
    balls.append(ball)
ramps = [Incline(450, 425, 400, True), Incline(260, 610, 50, False), 
        Incline(340, 650, 50, False), Incline(755, 200, 106, True),
        Incline(3110, -975, 4541, True)]
ropes = [Rope(seesaws[0], True, seesaws[1], True),
        Rope(seesaws[2], True, seesaws[4], True),
        Rope(seesaws[3], False, seesaws[5], False),
        Rope(seesaws[5], True, seesaws[6], False),
        Rope(seesaws[0], False, seesaws[7], False),
        Rope(seesaws[4], False, seesaws[7], False)]

windowSurface.fill(WHITE)

while(True):
    draw()
    update()
    checkKey()
