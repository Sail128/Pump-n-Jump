import main as mn
import pygame as pg
import numpy as np
import objects as objs
import json as json
from os import walk

width = 720
height = 480
class Game():
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((width,height),pg.DOUBLEBUF|pg.RESIZABLE)
        self.objects = []

    def eventHandler(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False
            if event.type == pg.KEYUP:
                print(event.key)
                if event.key == 27:
                    self.running = False
                if event.key == pg.K_SPACE:
                    self.player.jump()
    
    def setLevelList(self, levels:list() = None):
        try:
            f = []
            for (dirpath, dirnames, filenames) in walk(self.levelDir):
                f.extend(filenames)
            print(f)
            self.levelList = f
        except NameError:
            print("dir was not defined")
            self.levelList = levels

    def setLevelDir(self, dir):
        self.levelDir = dir
            
    def loadLevel(self, level):
        print("level loading")
        levelfile = open(self.levelDir + "/" + self.levelList[level])
        levelDict = json.load(levelfile)
        levelfile.close()
        print(levelDict["player"])
        print(type(levelDict["objects"]))

        self.spriteSheet = objs.spritesheet(levelDict["sprite sheet"])
        self.physics = levelDict["physics"]

        self.player = objs.Player(levelDict["player"], levelDict["assetsDir"])

        for x in levelDict["objects"]:
            self.objects.append(objs.Sprite(x)) 

        map = levelDict["map"]
        map = map[::-1]
        print(map[0])
        for y in range(len(map)):
            for x in range(len(map[y])):
                if map[y][x] != 0:
                    self.objects[map[y][x]-1].instances.append([x,y])


    def start(self):
        self.loadLevel(self.levelList.index("start.json"))

    def close(self):
        pg.quit()

    def run(self):
        self.running = True
        oldtime = pg.time.get_ticks()
        fps = [0.0, 0.0]
        pg.time.wait(10)
        while self.running:
            #handle frame counting limiting and dt
            now = pg.time.get_ticks()
            wait = int(16.666666 - (now-oldtime))
            pg.time.wait(wait)
            now = pg.time.get_ticks()
            dt = (now-oldtime)/1000
            oldtime = now
            fps[0] += 1
            fps[1] += dt
            if fps[1] >= 1.0:
                print("fps: ", fps[0])
                fps[0] = 0.0
                fps[1] = 0.0
            
            #handle all necesarry events
            self.eventHandler()
            self.player.inputHandler()

            #collision detection
            for x in self.objects:
                x.detectCollision([self.player])


            #update player and object states
            self.player.update(dt, self.physics)

            #render everything to the screen
            self.screen.fill((0,20,0))

            self.player.render(self.screen)
            for x in self.objects:
                x.render(self.screen, self.spriteSheet)
            pg.display.flip()
        self.close()
