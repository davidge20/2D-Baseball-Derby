from cmu_112_graphics import *
from random import *
from math import *

#Sprite sheets for "pitcherSprites.png" and "battingSprites.png" from
#https://www.deviantart.com/kingnoel/art/DK-Superstar-Baseball-MLSS-Style-Sprite-Sheet-512492203

#TODO: 
#Setup variety of different pitches based on randomness
#Implement strikes vs balls
#i.e power swing vs contact swing
#Setup power of swing based on type of swing
#Adds biases to pitcher based on the pitches thrown and sees which
#pitches the batter is hitting

class Pitch:
    def __init__(self, name, dx, d2x, dy, d2y, mass, chance):
        self.name = name
        self.dx = dx
        self.d2x = d2x
        self.dy = dy
        self.d2y = d2y
        self.mass = mass
        self.chance = chance

    def reset(self, dx, d2x, dy, d2y):
        self.dx = dx
        self.d2x = d2x
        self.dy = dy
        self.d2y = d2y      

    def __repr__(self):
        return self.name

class Bat:
    def __init__(self, name, mass, length):
        self.name = name
        self.mass = mass
        self.length = length

#Probabiltiy of ball being hit based on bat length
    def probabilityOfContact(self, app):
        num = randrange(1,100)
        cutoff = self.length
        if num < cutoff:
            return True
        else:
            return False

#Calculate dx and dy the ball after it is hit
    def velocityOfHit(self, app):

        vInitial = app.pitchSpeed
        dT = 0.15 #avg time of bat on ball
        acceleration = 31 #avg bat accel
        fAvg = self.mass * acceleration
        vFinal = ((fAvg * dT) // app.pitch.mass) + vInitial
        velOfBall = (vFinal/(cos(app.launchAngle))) // 4

        velOfBallX = velOfBall * (cos(app.launchAngle)) * 1.25
        velOfBallY = -1 * abs(velOfBall * (sin(app.launchAngle)))
        
        app.pitch.dx = velOfBallX
        app.pitch.dy = velOfBallY

        print(f'velOfBall is {velOfBall}')
        print(f'the velos are {velOfBallX}, {velOfBallY}')
        print(f'---------------')
        return velOfBall

    def __repr__(self):
        return f"{self.name}"

def appStarted(app): 
    #Pitcher sprites
    app.imagePitcher = app.loadImage("pitcherSprites.png")
    app.imageBatter = app.loadImage("battingSprites.png")

    spritestripPitcher = app.imagePitcher
    app.spritesPitcher = [ ]
    for i in range(6):
        sprite = spritestripPitcher.crop((153*i, 0, 150*(i+1), 158))
        app.spritesPitcher.append(sprite)
    app.spritePitcherCounter = 0

    #Batter sprites
    spritestripBatter = app.imageBatter
    app.spritesBatter = [ ]
    for i in range(4):
        sprite = spritestripBatter.crop((190*i, 0, 192*(i+1), 188))
        app.spritesBatter.append(sprite)
    app.spriteBatterCounter = 0

    app.directions = False
    app.currMode = False
    app.modeSelected = None

    #Pitches
    app.ballCx, app.ballCy = app.width * 26/39, app.height * 7/9
    app.r = 7
    app.fastball = Pitch("fastball", -7, 0, 0, 0, 0.145, 33) 
    app.curveball = Pitch("curveball", -7, 0, -6, .12, 0.145, 33)
    app.slider = Pitch("slider", -7, 0, -2 , 0.08, 0.145, 33)
    app.pitchList = [app.fastball, app.curveball, app.slider]
    app.pitch = None
    app.pitchSpeed = None
    app.pitcher = False
    app.throwBall = False
    app.pitcherTime = 3000

    #Batting
    app.pickBat = False
    app.positionAtSwingX, app.positionAtSwingY = 0, 0
    app.launchAngle = None
    app.gravity = 0.0032
    app.batter = False
    app.hitPitch = False
    app.bat = None
    app.freezeBall = False
    app.grassBall = False

    app.strikes = 0
    app.balls = 0
    app.outs = 0
    app.score = 0
    app.scoreAdd = False

    app.timerDelay = 10
    app.spritePitcherDelay = 0
    app.spriteBatterDelay = 0

#Check if ball is hit if batter swings
def contactWithBat(app):
    batCx = app.width * 1/12
    batCy = app.height * 8/11
    batR = app.width//12

    if (batCx < app.ballCx < batCx + batR and 
        batCy - batR < app.ballCy < batCy + batR):
        print("Hit")

        app.pitch.dx = 0
        app.pitch.dy = 0
        app.pitch.d2x = 0
        app.pitch.d2y = 0

        return True
    
    return False

#Finds launch angle
def launchAngle(app):
    batCx = app.width * 1/12
    batR = app.width//36

    left1 = batCx
    left2 = batCx + batR
    left3 = batCx + 2 * batR
    left4 = batCx + 3 * batR

    if left3 <= app.positionAtSwingX <= left4:
        app.launchAngle = randrange(41,60)
    elif left2 <= app.positionAtSwingX < left3:
        app.launchAngle = randrange(25,40)
    elif left1 <= app.positionAtSwingX < left2:
        app.launchAngle = randrange(1,15)

    #Conversion from degrees to radians 
    app.launchAngle = (app.launchAngle * pi)/180

    print(f'the pitch is {app.pitch}')
    print(f'the launch angle is {app.launchAngle}')

#Choose pitch for pitcher
def chooseRandomPitch(app):
    totalPitches = len(app.pitchList)
    randomNum = randint(0, totalPitches - 1)
    app.pitch = app.pitchList[randomNum]

    cy = app.height * 7//9
    max = cy - app.height//20
    min = cy + app.height//20
    app.ballCy = randrange(max, min)

    #resets values
    speed = randrange(-10, -6)
    app.fastball.reset(speed, 0, 0, 0)
    app.curveball.reset(speed,0 , -6, .12)
    app.slider.reset(speed, 0, -3.5 , 0.08)

#Choose pitch for smart pitcher
def chooseSmartPitch(app):
    #Add each pitch to a list, 500(-3), 250(-2), 100(-1), homerun(-4),
    #popout(+1), and ground(+1)
    #Create a dictionary with each pitch and its corresponding value
    #Change the size of the probability of the pitch being thrown

    fastball = app.fastball.chance
    curveball = app.curveball.chance + app.fastball.chance
    max = slider = app.fastball.chance + app.slider.chance + app.curveball.chance
    print(f'chances are {(fastball,curveball, max)}')
    num = randrange(1,max)

    if 1 <= num < fastball:
        app.pitch = app.pitchList[0]
    elif fastball <= num < curveball:
        app.pitch = app.pitchList[1]
    elif curveball <= num <= slider:
        app.pitch = app.pitchList[2]

    #position the pitch
    cy = app.height * 7//9
    max = cy - app.height//20
    min = cy + app.height//20
    app.ballCy = randrange(max, min)

    #resets values
    speed = randrange(-10, -6)
    app.fastball.reset(speed, 0, 0, 0)
    app.curveball.reset(speed,0 , -6, .14)
    app.slider.reset(speed, 0, -3.5 , 0.08)

def keyPressed(app, event):
    if event.key == "e":
        app.currMode = True
        app.modeSelected = "easy"

    if event.key == "h":
        app.currMode = True
        app.modeSelected = "hard"

    if event.key == "p": #Pitcher pitches
        app.ballCx, app.ballCy = app.width * 26/39, app.height * 7/9
        app.hitPitch = False
        app.pitcher = True
        chooseSmartPitch(app)
    
    if event.key == "b": #Batter swings
        app.positionAtSwingX, app.positionAtSwingY = app.ballCx, app.ballCy
        if contactWithBat(app):
            launchAngle(app)
            app.bat.velocityOfHit(app)

            app.throwBall = False
            app.hitPitch = True
            app.batter = True

    #User chooses a bat
    if event.key == "1":
        app.pickBat = True
        app.bat = Bat("slammer", 0.4, 50)

    if event.key == "2":
        app.pickBat = True
        app.bat = Bat("longhead", 0.1, 75)

    if event.key == "c":
        app.directions = True

def timerFired(app):
    #Pitcher auto throws
    if app.directions == True:
        app.pitcherTime -= 10
    if app.pitcherTime <= 0:
        app.ballCx, app.ballCy = app.width * 26/39, app.height * 7/9
        app.hitPitch = False
        app.pitcher = True
        chooseSmartPitch(app)
        app.pitcherTime = 3000

    #Bounce on grass
    grassHeight = app.height * 8/9
    batterPosition = app.width * 1/12
    if app.ballCy >= grassHeight and app.ballCx > batterPosition:
        app.grassBall = True
        app.hitPitch = False
        app.scoreAdd = False

    if app.grassBall:
        app.pitch.dy = -1.5

        app.pitch.d2y += app.gravity
        app.pitch.dy += app.pitch.d2y

        app.ballCx += app.pitch.dx
        app.ballCy += app.pitch.dy
    
    #Score and assign points/outs
    currHeight = app.height * 1/15
    if app.ballCx > app.width * 11/12 or app.ballCy < currHeight:
        app.grassBall = False
        app.freezeBall = True
        app.hitPitch = False

        app.pitch.dx = 0
        app.pitch.dy = 0
        app.pitch.d2x = 0
        app.pitch.d2y = 0

        level1 = app.height * 1/3
        level2 = app.height * 2/3
        grassHeight = app.height * 8/9
        popFlyToHomeRun = app.width * 6/9
        HomeRunToScore = app.width * 11/12

        if app.modeSelected == "easy":
            multiplier = 1
        elif app.modeSelected == "hard":
            multiplier = 3

        pitchIndex = app.pitchList.index(app.pitch)

        if 0 <= app.ballCx < popFlyToHomeRun and app.scoreAdd:
            app.outs += 1
            app.pitch.chance += 2 * multiplier 
            app.scoreAdd = False

            for pitch in app.pitchList:
                if pitch != app.pitch:
                    app.pitch.chance -= 2 * multiplier 

        elif popFlyToHomeRun <= app.ballCx < HomeRunToScore and app.scoreAdd:
            app.score += 1000
            app.pitch.chance -=3 * multiplier
            app.scoreAdd = False

            for pitch in app.pitchList:
                if pitch is not app.pitch:
                    app.pitch.chance += 3 * multiplier 

        elif 0 <= app.ballCy < level1 and app.scoreAdd:
            app.score += 500
            app.pitch.chance -= 2 * multiplier
            app.scoreAdd = False

            for pitch in app.pitchList:
                if pitch is not app.pitch:
                    app.pitch.chance += 2 * multiplier 

        elif level1 <= app.ballCy < level2 and app.scoreAdd:
            app.score += 250
            app.pitch.chance -= 1 * multiplier
            app.scoreAdd = False

            for pitch in app.pitchList:
                if pitch is not app.pitch:
                    app.pitch.chance += 1 * multiplier 

        elif level2 <= app.ballCy < grassHeight and app.scoreAdd:
            app.score += 100
            app.pitch.chance -= 0 * multiplier
            app.scoreAdd = False
        
        if app.pitch.chance <= 0:
            app.pitch.chance = 0

    #Updates pitcher sprites
    if app.pitcher:
        app.spritePitcherDelay += 10
        if app.spritePitcherDelay >= 80:
            app.spritePitcherCounter = (1 + app.spritePitcherCounter)
            app.spritePitcherDelay = 0
            if app.spritePitcherCounter == 4:
                app.throwBall = True

            elif app.spritePitcherCounter == 6:
                app.pitcher = False
                app.spritePitcherCounter = 0

    #Updates batter sprites
    if app.batter:
        app.spriteBatterDelay += 10
        if app.spriteBatterDelay >= 80:
            app.spriteBatterCounter = (1 + app.spriteBatterCounter)
            app.spriteBatterDelay = 0

            if app.spriteBatterCounter == 4:
                app.batter = False
                app.spriteBatterCounter = 0

    #Pitches
    if app.throwBall:
        app.pitchSpeed = 36
        app.ballCx += app.pitch.dx
        app.pitch.dx += app.pitch.d2x
        app.ballCy += app.pitch.dy
        app.pitch.dy += app.pitch.d2y

    #Swings
    if app.hitPitch: 
        app.scoreAdd = True
        # print(f" the ball is at {(app.ballCx, app.ballCy)}")        
        app.pitch.d2y += app.gravity
        app.pitch.dy += app.pitch.d2y

        app.ballCx += app.pitch.dx
        app.ballCy += app.pitch.dy
        
def redrawAll(app, canvas):
    #Background field:
    canvas.create_rectangle(0,0, app.width, app.height, fill = "SkyBlue2")

    #Print sprites of pitcher and batter:
    pitcherSprite = app.spritesPitcher[app.spritePitcherCounter]
    canvas.create_image(app.width * 6/8, app.height * 20/25, 
                                    image=ImageTk.PhotoImage(pitcherSprite))

    batterSprite = app.spritesBatter[app.spriteBatterCounter]
    canvas.create_image(app.width * 1/12, app.height * 8/11, 
                                    image=ImageTk.PhotoImage(batterSprite))

    #Green zone:
    batCx = app.width * 1/12
    batCy = app.height * 8/11
    batR = app.width//12
    canvas.create_arc(batCx - batR, batCy - batR, batCx + batR,
                        batCy + batR, start=270, extent=180, outline = "green", width = 5)

    minibatR = app.width//36
    left2 = batCx + minibatR
    left3 = batCx + 2 * minibatR

    canvas.create_line(left2, batCy - batR, left2, batCy + batR, fill = "blue", width = 3)
    canvas.create_line(left3, batCy - batR, left3, batCy + batR, fill = "blue", width = 3)

    #Hub:
    textX = app.width * 1/10
    textY = app.height * 1/10
    canvas.create_text(textX, textY, text = f"Type of Bat: {app.bat}", font = "Arial 20 bold", fill = "black")
    canvas.create_text(textX, textY * 1.5, text = f"Strikes: {app.strikes}/3", font = "Arial 20 bold", fill = "black")
    canvas.create_text(textX, textY * 2, text = f"Balls: {app.balls}/4", font = "Arial 20 bold", fill = "black")
    canvas.create_text(textX, textY * 2.5, text = f"Outs: {app.outs}/3", font = "Arial 20 bold", fill = "black")
    canvas.create_text(textX, textY * 3, text = f"Score: {app.score}", font = "Arial 20 bold", fill = "black")
    canvas.create_text(textX, textY * 3.5, text = f"Pitcher Time Delay: {app.pitcherTime/1000}", font = "Arial 20 bold", fill = "black")
    canvas.create_text(textX, textY * 4, text = f"Mode: {app.modeSelected}", font = "Arial 20 bold", fill = "black")

    #Grass
    grassHeight = app.height * 8/9
    canvas.create_rectangle(0, grassHeight, app.width, app.height, 
                                            fill = "green", outline = "green")

    #Score Zones
    level1 = app.height * 2/3
    level2 = app.height * 1/3
    x0 = app.width * 11/12
    x1 = app.width

    xMid = (x0 + x1)//2
    yScore1 = (level1 + grassHeight)//2
    yScore2 = (level1 + level2)//2
    yScore3 = (0 + level2)//2

    canvas.create_rectangle(x0, level1, x1, grassHeight , fill = "turquoise1")
    canvas.create_text(xMid, yScore1, text = "100", fill = "black", 
                                        font = "Arial 20 bold")

    canvas.create_rectangle(x0, level2, x1, level1 , fill = "turquoise2")
    canvas.create_text(xMid, yScore2, text = "250", fill = "black", 
                                        font = "Arial 20 bold")

    canvas.create_rectangle(x0, 0, x1, level2 , fill = "turquoise3")
    canvas.create_text(xMid, yScore3, text = "500", fill = "black", 
                                        font = "Arial 20 bold")

    popFlyToHomeRun = app.width * 6/9
    currHeight = app.height * 1/15
    canvas.create_rectangle(0,0,popFlyToHomeRun, currHeight, fill = "red")
    canvas.create_text(popFlyToHomeRun//2,currHeight//2, text = "Pop Out Zone", 
                        fill = "black", font = "Arial 20 bold")
    canvas.create_rectangle(popFlyToHomeRun,0,x0,currHeight, fill = "lime green")
    canvas.create_text((popFlyToHomeRun + x0)//2,currHeight//2, text = "Home Run Zone", 
                        fill = "black", font = "Arial 20 bold")

    #Ball:
    if app.throwBall or app.hitPitch or app.freezeBall or app.grassBall:
        canvas.create_oval(app.ballCx - app.r, app.ballCy - app.r, 
                        app.ballCx + app.r, app.ballCy + app.r, fill = "white")
    
    #MPH:
        canvas.create_text(app.width*4/6, app.height*1/12, text = f"MPH: {app.pitchSpeed}", 
                                anchor = "nw", fill = "black", font = "Arial 30 bold")
        canvas.create_text(app.width*4/6, app.height*2/12, text = f"Pitch: {app.pitch.name}", 
                                anchor = "nw", fill = "black", font = "Arial 30 bold")
    
    #Welcome screen
    if app.pickBat == False or app.currMode == False:
        canvas.create_text(app.width//2, app.height//3, 
        text = "Welcome! Pick a bat!", fill = "black", font = "Arial 30 bold")

        canvas.create_text(app.width//2, app.height//3 * 1.2, 
        text = "Bat 1: Slugger or Bat 2: Longhead", fill = "black", font = "Arial 30 bold")
    
        canvas.create_text(app.width//2, app.height//3 * 1.4, 
        text = "Choose slugger if you are all about the power",
        fill = "black", font = "Arial 20 bold")

        canvas.create_text(app.width//2, app.height//3 * 1.5, 
        text = "Choose longhead for higher accuracy but less power",
        fill = "black", font = "Arial 20 bold")

        canvas.create_text(app.width//2, app.height//3 * 1.7, 
        text = "Press 'e' for a smart pitcher and 'h' for a smarter pitcher",
        fill = "black", font = "Arial 25 bold")
    
    if app.directions == False and app.pickBat == True and app.currMode == True:
        canvas.create_text(app.width//2, app.height * 1/2, 
        text = "Directions: Press on the 'b' key to swing and try to hit the ball as many times before you have 3 outs!", 
        fill = "black", font = "Arial 20 bold")

        canvas.create_text(app.width//2, app.height * 1/2 * 1.2, 
        text = "Press 'c' to begin! Best of luck!", 
        fill = "black", font = "Arial 20 bold")

runApp(width=1200, height=600)