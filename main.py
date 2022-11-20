from cmu_112_graphics import *

#Sprite for pitcher >> Done 
#Setup different pitches >>

def appStarted(app): 
    #Pitcher sprites
    app.image = app.loadImage("pitcherSprites.png")
    app.imgWidth = app.image.width
    app.imgHeight = app.image.height

    spritestrip = app.image
    app.sprites = [ ]
    for i in range(6):
        sprite = spritestrip.crop((176*i, 0, 175*(i+1), 158))
        app.sprites.append(sprite)
    app.spriteCounter = 0

    #Pitches
    app.ballCx, app.ballCy = app.width * 26/39, app.height * 7/9
    app.r = 7
    app.fastballDx = -20
    app.pitcher = False
    app.throwBall = False

def keyPressed(app, event):
    if event.key == "p":
        app.pitcher = True

def timerFired(app):
    #Updates pitcher sprites
    if app.pitcher:
        app.spriteCounter = (1 + app.spriteCounter)
        if app.spriteCounter == 4:
            app.throwBall = True

        elif app.spriteCounter == 6:
            app.pitcher = False
            app.spriteCounter = 0
    
    if app.throwBall:
        app.ballCx += app.fastballDx 
        
def redrawAll(app, canvas):
    #Background field
    canvas.create_rectangle(0,0, app.width, app.height, fill = "SkyBlue2")
    canvas.create_rectangle(0, app.height * 8/9, app.width, app.height, fill = "green", outline = "green")

    #Print sprites of pitcher
    sprite = app.sprites[app.spriteCounter]
    canvas.create_image(app.width * 6/8, app.height * 7/9, image=ImageTk.PhotoImage(sprite))

    #Ball
    if app.throwBall:
        canvas.create_oval(app.ballCx - app.r, app.ballCy - app.r, app.ballCx + app.r, app.ballCy + app.r, fill = "white")

runApp(width=1200, height=600)