#From the course website
#https://www.cs.cmu.edu/~112/notes/notes-animations-part4.html#spritesheetsWithCropping 

# This demos sprites using Pillow/PIL images
# See here for more details:
# https://pillow.readthedocs.io/en/stable/reference/Image.html

# This uses a spritestrip from this tutorial:
# https://www.codeandweb.com/texturepacker/tutorials/how-to-create-a-sprite-sheet

from cmu_112_graphics import *

def appStarted(app):
    url = 'http://www.cs.cmu.edu/~112/notes/sample-spritestrip.png'
    spritestrip = app.loadImage(url)
    app.sprites = [ ]
    for i in range(6):
        sprite = spritestrip.crop((30+260*i, 30, 230+260*i, 250))
        app.sprites.append(sprite)
    app.spriteCounter = 0

def timerFired(app):
    app.spriteCounter = (1 + app.spriteCounter) % len(app.sprites)

def redrawAll(app, canvas):
    sprite = app.sprites[app.spriteCounter]
    canvas.create_image(200, 200, image=ImageTk.PhotoImage(sprite))

runApp(width=400, height=400)