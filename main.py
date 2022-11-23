from cmu_112_graphics import *
from random import *
from math import *

#Sprite sheets for "pitcherSprites.png" and "battingSprites.png" from
#https://www.deviantart.com/kingnoel/art/DK-Superstar-Baseball-MLSS-Style-Sprite-Sheet-512492203

#TODO: 
#Setup variety of different pitches based on randomness
#Implement strikes vs balls
#Setup probabilty of missing the pitch based on the type of swing
#i.e power swing vs contact swing
#Setup power of swing based on type of swing

#Adds biases to pitcher based on the pitches thrown and sees which
#pitches the batter is hitting

class Pitch:
    def __init__(self, name, dx, d2x, dy, d2y, mass):
        self.name = name
        self.dx = dx
        self.d2x = d2x
        self.dy = dy
        self.d2y = d2y
        self.mass = 5

    def reset(self, dx, d2x, dy, d2y):
        self.dx = dx
        self.d2x = d2x
        self.dy = dy
        self.d2y = d2y

class Bat:
#More mass more power
#Higher length leads to higher possibilty of hitting the ball but less power

    def __init__(self, name, mass, length):
        self.name = name
        self.mass = mass
        self.length = length

#Probabiltiy of ball being hit based on bat length
    def probabilityOfContact(self, app):
        num = randrange(1,100)
        cutoff = (self.length)
        if num < cutoff:
            return True
        else:
            return False
    
#Calculate the x- and y-vector of the ball after it is hit
    def velocityOfHit(self, app):
        app.launchAngle = 30
        vInitial = app.pitchSpeed
        dT = 0.01
        acceleration = 5
        fAvg = self.mass * acceleration
        vFinal = ((fAvg * dT) // app.pitch.mass) + vInitial
        velOfBall = (vFinal/(cos(app.launchAngle)))

        velOfBallX = velOfBall * (cos(app.launchAngle))
        velOfBallY = velOfBall * (sin(app.launchAngle)) // 10
        
        app.pitch.dx = velOfBallX
        app.pitch.dy = velOfBallY

        app.pitchd2x = 0
        app.ptichd2y = 0

        print(f'velOfBall is {velOfBall}')
        print(f'the velos are {velOfBallX}, {velOfBallY}')

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

    #Pitches
    app.ballCx, app.ballCy = app.width * 26/39, app.height * 7/9
    app.r = 7
    app.fastball = Pitch("fastball", -7, 0, 0, 0, 5) 
    app.curveball = Pitch("curveball", -7,0 , -1.8, 0.1, 5)
    app.slider = Pitch("slider", -7, 0, 0.2 , 0.05, 5)
    app.pitchList = [app.fastball, app.curveball, app.slider]
    app.pitch = None
    app.pitchSpeed = None
    app.pitcher = False
    app.throwBall = False

    #Batting
    app.launchAngle = None
    app.gravity = 0.06
    app.batter = False
    app.hitPitch = False
    app.strikes = 0
    app.balls = 0
    app.outs = 0
    app.bat = None

    app.timerDelay = 10
    app.spritePitcherDelay = 0
    app.spriteBatterDelay = 0

#Check if ball is hit if batter swings
def contactWithBat(app):
    batCx = app.width * 1/12
    batCy = app.height * 8/11
    batR = app.width//12

    if (batCx < app.ballCx < batCx + batR and 
        batCy - batR < app.ballCy < batCy + batR and
        app.bat.probabilityOfContact(app)):
        print("Hit")
        app.throwBall = False
        app.hitPitch = True

        app.pitch.dx = 0
        app.pitch.dy = 0

#Choose pitch for pitcher
def chooseRandomPitch(app):
    totalPitches = len(app.pitchList)
    randomNum = randint(0, totalPitches - 1)
    app.pitch = app.pitchList[randomNum]

    #resets values
    app.fastball.reset(-7, 0, 0, 0)
    app.curveball.reset(-7,0 , -6, .1)
    app.slider.reset(-7, 0, .6 , 0.6)

def keyPressed(app, event):
    if event.key == "p": #Pitcher pitches
        app.ballCx, app.ballCy = app.width * 26/39, app.height * 7/9
        app.hitPitch = False
        app.pitcher = True
        chooseRandomPitch(app)
    
    if event.key == "b": #Batter swings
        contactWithBat(app)
        app.batter = True

#User chooses a bat
    if event.key == "1":
        app.bat = Bat("slammer", 75, 25)

    if event.key == "2":
        app.bat = Bat("longhead", 25, 75)

def timerFired(app):
    #Updates pitcher sprites
    if app.pitcher:
        app.spritePitcherDelay += 10
        if app.spritePitcherDelay >= 80:
            app.spritePitcherCounter = (1 + app.spritePitcherCounter)
            app.spriteBatterDelay = 0
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
        app.pitchSpeed = ((app.pitch.dx)**2 + (app.pitch.dy) ** 2) ** 0.5
        app.ballCx += app.pitch.dx
        app.pitch.dx += app.pitch.d2x

        if app.pitch.name == "slider" and app.ballCx < 1/7 * app.width:
            app.ballCy += app.pitch.dy
            app.pitch.dy += app.pitch.d2y
        elif app.pitch.name != "slider": 
            app.ballCy += app.pitch.dy
            app.pitch.dy += app.pitch.d2y

    #Swings
    if app.hitPitch:
        print("Ball was hit")
        print(f" the ball is at {(app.ballCx, app.ballCy)}")
        app.bat.velocityOfHit(app)
        
        app.pitch.d2y += app.gravity
        app.pitch.dy += app.pitch.d2y

        app.ballCx += app.pitch.dx
        app.ballCy += app.pitch.dy

        print(app.ballCx, app.ballCy)
        
def redrawAll(app, canvas):
    #Background field:
    canvas.create_rectangle(0,0, app.width, app.height, fill = "SkyBlue2")

    #Print sprites of pitcher and batter:
    pitcherSprite = app.spritesPitcher[app.spritePitcherCounter]
    canvas.create_image(app.width * 6/8, app.height * 10/13, 
                                    image=ImageTk.PhotoImage(pitcherSprite))

    batterSprite = app.spritesBatter[app.spriteBatterCounter]
    canvas.create_image(app.width * 1/12, app.height * 8/11, 
                                    image=ImageTk.PhotoImage(batterSprite))

    #Ball:
    if app.throwBall or app.hitPitch:
        canvas.create_oval(app.ballCx - app.r, app.ballCy - app.r, 
                        app.ballCx + app.r, app.ballCy + app.r, fill = "white")

    #MPH:
        canvas.create_text(app.width*4/6, app.height*1/12, text = f"MPH: {app.pitchSpeed}", 
                            anchor = "nw", fill = "black", font = "Arial 30 bold")
        canvas.create_text(app.width*4/6, app.height*2/12, text = f"Pitch: {app.pitch.name}", 
                            anchor = "nw", fill = "black", font = "Arial 30 bold")

    #Green zone:
    batCx = app.width * 1/12
    batCy = app.height * 8/11
    batR = app.width//12
    canvas.create_arc(batCx - batR, batCy - batR, batCx + batR,
                        batCy + batR, start=270, extent=180, outline = "green", width = 5)

    #Hub:
    textX = app.width * 2/12
    textY = app.height * 1/10
    canvas.create_text(textX, textY, text = f"Type of Bat: {app.bat}", font = "Arial 20 bold", fill = "black")
    canvas.create_text(textX, textY * 1.5, text = f"Strikes: {app.strikes}/3", font = "Arial 20 bold", fill = "black")
    canvas.create_text(textX, textY * 2, text = f"Balls: {app.balls}/4", font = "Arial 20 bold", fill = "black")
    canvas.create_text(textX, textY * 2.5, text = f"Outs: {app.outs}/3", font = "Arial 20 bold", fill = "black")

    #Grass
    canvas.create_rectangle(0, app.height * 8/9, app.width, app.height, 
                                            fill = "green", outline = "green")


runApp(width=1200, height=600)