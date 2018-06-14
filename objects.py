import pygame as pg 
from math import ceil


class Sprite():
    def __init__(self, dct:dict, assetdir = "", ss = None):
        self.id = dct["id"] if "id" in dct else None #object id
        if "imageat" in dct:
            self.image = ss.image_at(dct["imageat"]) #position of image on sprite sheet
        elif "image" in dct:
            print(assetdir+dct["image"])
            self.image = pg.image.load(assetdir+dct["image"])
        self.box = dct["box"] if "box" in dct else print("no box defined") #box for physics interactions
        self.collisions = dct["collision"] if "collision" in dct else False #sets wether the objects has interactions
        self.oncollision = dct["oncollision"]  if "oncollision" in dct and dct["oncollision"] != None  else dict()
        self.solid = dct["solid"] if "solid" in dct else False #whether object is solid
        self.passthrough = dct["passthrough"] if "passthrough" in dct else True
        self.friction = dct["friction"] if "friction" in dct else 0.0 #friction an object exerts on a player, 
        self.non = 0

        self.instances = [] #all instances of this exact object
        self.pos = [0.0,0.0]

    def collision(self, instance:list):
        #print("collision: ", instance)
        self.non = False


    def detectCollision(self, objects:list, game):
        for x in objects:
            if self.collisions:
                colval = list(map(lambda x,y: (x+y)/2, x.box, self.box))
                for instance in self.instances:
                    cen = list(map(lambda x: x*32, instance))
                    dist = list(map(lambda x, y: abs(x-y), cen, x.pos))
                    if dist[0] < colval[0] and dist[1]<colval[1]:
                        if "loadlevel" in self.oncollision: game.loadLevel(game.levelList.index(self.oncollision["loadlevel"]))
                        if dist[0]/colval[0] > dist[1]/colval[1]: 
                            #print("x collision")
                            if cen[0]>x.pos[0]:
                                #right collision
                                x.collision("r", self, instance)
                            else:
                                #left collision
                                x.collision("l", self, instance)
                            #self.collision(instance)
                        else:
                            #print("y collision")
                            if cen[1]>x.pos[1]:
                                #top collision
                                x.collision("t", self, instance)
                            else:
                                #bottom collision
                                x.collision("b", self, instance)
                            #self.collision(instance)

    def render(self, screen, ss, camerapos):
        for instance in self.instances:
            pos = [ instance[0]*32-camerapos[0] , 
                    screen.get_height() -(instance[1]*32-camerapos[1])]
            screen.blit(self.image, tuple(map(lambda x, y: x - y/2, pos, self.box)))
            #pos = [ instance[0]*self.box[0]-camerapos[0] , 
            #        screen.get_height() -(instance[1]*self.box[1]-camerapos[1])]
            #screen.blit(self.image, tuple(map(lambda x, y: x - y/2, pos, self.box)))

class Player(Sprite):
    def __init__(self, dct:dict, assetdir:str):
        super().__init__(dct, assetdir=assetdir)
        animdct = dct["animation"] if "animation" in dct else False
        if animdct["use"]:
            self.animations = dict()
            self.setup_animations(animdct["animations"], assetdir)
        else: 
            self.image = pg.image.load(assetdir + dct["image"]).convert_alpha()
        self.maxspeed = dct["maxspeed"]
        self.maxjump = dct["maxjump"]
        self.acc = dct["acceleration"]
        self.pos = dct["start"]
        self.vel = [0.0,0.0]
        self.jumpstrength = 0.0
        self.jumps = 0
        self.move = list()
        self.pressed = False

    def setup_animations(self, dct, assetdir):
        print(dct)
        for key, val in dct.items():
            print(key, val)
            self.animations[key] = [
                spriteAnim(assetdir+val["file"],
                    val["rect"],
                    val["frames"],
                    loop = val["loop"] if "loop" in val else True),
                0.0, #time since last frame update
                1.0/(val["frames"]) #time for every frame update
                ]
        
        self.image = self.animations["s"][0].next()

    def inputHandler(self):
        self.move = []
        keys = pg.key.get_pressed()
        if keys[pg.K_d]:
            #print("right")
            self.move.append("r")
        if keys[pg.K_a]:
            #print("left")
            self.move.append("l")
        #if keys[pg.K_w]:
            #print("up")
        #if keys[pg.K_s]:
            #print("down")
        if keys[pg.K_SPACE]:
            #print("space")
            self.pressed = True
            self.move.append("jch")
            
        if not keys[pg.K_SPACE] and self.pressed:
            self.pressed = False
            self.move.append("j")

    def jump(self):
        if self.jumps < 2: 
            self.vel[1] += self.jumpstrength
            print(self.jumpstrength)
            self.jumpstrength *= 0.35
            self.jumps +=1

    def collision(self, side:str, colobject:Sprite, instance:list):
        if side == "l":
            #print("left")
            if self.vel[0] < 0.0 and colobject.solid: 
                self.vel[0] = 0.0
                self.pos[0] = instance[0]*32+(colobject.box[1] + self.box[0])/2
        elif side == "r":
            #print("right")
            if self.vel[0] > 0.0 and colobject.solid: 
                self.vel[0] = 0.0
                self.pos[0] = instance[0]*32+(colobject.box[1]-self.box[0])/2
        elif side == "t":
            #print("top")
            if not colobject.passthrough:
                if self.vel[1]>0.0 : self.vel[1] = 0.0
                self.pos[1] = instance[1]*32-(colobject.box[1]+self.box[1])/2
        elif side == "b":
            if colobject.solid: 
                if self.vel[1]<0.0 : self.vel[1] = 0.0
                self.move.append({"f":colobject.friction})
                self.pos[1] = instance[1]*32+(colobject.box[1]+self.box[1])/2
                self.jumps = 0
        
        
    def update(self, dt:float, physics:dict):
        

        for x in self.move:
            if x == "r":
                self.vel[0] = min(self.vel[0] + self.acc*dt, self.maxspeed)

                if (self.animations["r"][1] > self.animations["r"][2]) and (-1<self.vel[1]<1):
                    self.image = self.animations["r"][0].next()
                    self.animations["r"][1] == 0.0
                    
                else: 
                    self.animations["r"][1] += dt

            elif x == "l":
                self.vel[0] = max(self.vel[0] - self.acc*dt, -self.maxspeed)

                if self.animations["l"][1] > self.animations["l"][2] and -1<self.vel[1]<1:
                    self.image = self.animations["l"][0].next()
                    self.animations["l"][1] == 0.0
                else: 
                    self.animations["l"][1] += dt

            elif "f" in x:
                if self.vel[0] >= 0.2 or self.vel[0] <= -0.2: 
                    self.vel[0] *= (abs(abs(self.vel[0])-max(1, abs(self.vel[0])/40)*x["f"] * dt))/abs(self.vel[0])
                else: 
                    self.vel[0] = 0.0
                #self.image = self.animations["s"][0].next()
            elif x=="jch":
                if self.vel[1] > 0.1:
                     self.jumpstrength = min(self.maxjump , self.jumpstrength + 200.0*dt)
                else:
                    self.jumpstrength = min(self.maxjump , self.jumpstrength + 400.0*dt)

            elif x=="j":
                self.jump()
                self.image = self.animations["u"][0].next()
            
            if not "jch" in self.move:
                self.jumpstrength = max (0, self.jumpstrength - 10*dt)
        #update dynamic animations    
        if (-0.5 <self.vel[0]< 0.5) and (-0.5<self.vel[1]<0.5):
            self.image = self.animations["s"][0].next()

        if self.vel[1] < -0.5:
            self.image = self.animations["d"][0].next()
        
        #standard equations of motion
        self.vel[1] -= physics["gravity"]*dt
        self.pos[0] += self.vel[0]*dt
        self.pos[1] += self.vel[1]*dt

 
        

    def render(self, screen, camerapos):
        screen.blit(self.image, (int(self.pos[0]-self.box[0]/2- camerapos[0]), int(screen.get_height() -(self.pos[1]-camerapos[1])-self.box[1]/2)))

class spritesheet(object):
    def __init__(self, filename:str):
            self.sheet = pg.image.load(filename).convert_alpha()

    #returns image from rectangle(x, y, x+offset, y+offset)
    def image_at(self, rectangle:list):
        
        rect = pg.Rect(rectangle)
        image = pg.Surface(rect.size).convert_alpha()
        image.fill((0,0,0,0))#fill with alpha so every thing is zero
        image.blit(self.sheet, (0, 0), rect , pg.BLEND_RGBA_ADD)#add the rectangle from the sheet to the temp image
        return image

    def images_at(self, rects:list):
        return [self.image_at(rect) for rect in rects]

    def loadStrip(self, rect:list , count:int):
        rects = []
        for x in range(count):
            rects.append((rect[0] + rect[2] * x, 
            rect[1], rect[2], rect[3]))
        return self.images_at(rects)

class spriteAnim(object):
    def __init__(self, filename, rect, count, colorkey=None, loop=False):
        self.filename = filename
        ss = spritesheet(filename)
        self.images = ss.loadStrip(rect, count)
        self.loop = loop
        self.i = 0

    def reset(self):
        #resets the loop
        self.i = 0
        return self

    def next(self):
        if self.i >= len(self.images):
            if self.loop:
                self.i = 0
        image = self.images[self.i]
        self.i += 1
        return image

class Background():
    def __init__(self, dct:dict, assetdir:str):
        self.image = pg.image.load(assetdir + dct["image"]).convert_alpha()
        print(self.image)
        self.distance = dct["distance"] if "distance" in dct else 20
        self.looping = dct["looping"] if "looping" in dct else False
        self.position = dct["position"] if "position" in dct else [0,0]
        self.size = self.image.get_size()
    
    def render(self, screen:pg.Surface, camerapos:list):
        pos = [ self.position[0] - camerapos[0]/self.distance, screen.get_height() -(self.position[1]-camerapos[1]/self.distance +self.size[1])]
        screenwidth = screen.get_width()
        if self.looping:
            # looping is not functional as of jet
            bound = ceil((camerapos[0] + screenwidth - pos[0]) / self.size[0])
            if bound < 0: 
                bound -= ceil(screenwidth/self.size[0])
                upbound = bound + ceil( (camerapos[0] + screenwidth - ( pos[0]+ bound*self.size[0] ) ) / self.size[0] )
                for i in range(bound, upbound+1):
                    screen.blit(self.image, (pos[0] + self.size[0]*i, pos[1]))
            elif bound > 0:
                lowbound = bound - ceil( ( pos[0] + bound*self.size[0] - camerapos[0]) / self.size[0])
                print(lowbound, bound)
                for i in range(lowbound, bound+1):
                    screen.blit(self.image, (pos[0]+ self.size[0]*i, pos[1]) )
        else:
            screen.blit(self.image, pos)