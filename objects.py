import pygame as pg 


class Sprite():
    def __init__(self, dct:dict):
        self.id = dct["id"] if "id" in dct else None #object id
        self.imageat = dct["imageat"] if "imageat" in dct else None #position of image on sprite sheet
        self.box = dct["box"] if "box" in dct else print("no box defined") #box for physics interactions
        self.collisions = dct["collision"] if "collision" in dct else False #sets wether the objects has interactions
        self.oncollision = dct["oncollision"]  if "oncollision" in dct else dict()
        self.solid = dct["solid"] if "solid" in dct else False #whether object is solid
        self.friction = dct["friction"] if "friction" in dct else 0.0 #friction an object exerts on a player, 

        self.instances = [] #all instances of this exact object
        self.pos = [0.0,0.0]

    def collision(self, instance:list):
        print("collision: ", instance)

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

    def render(self, screen, ss):
        for instance in self.instances:
            screen.blit(ss.image_at(self.imageat), tuple(map(lambda x, y: x - y/2,[instance[0]*self.box[0] , screen.get_height() -(instance[1])*self.box[1]], self.box)))

class Player(Sprite):
    def __init__(self, dct:dict, assetdir:str):
        super().__init__(dct)
        self.image = pg.image.load(assetdir + dct["image"]).convert_alpha()
        self.maxspeed = dct["maxspeed"]
        self.maxjump = dct["maxjump"]
        self.acc = dct["acceleration"]
        self.pos = dct["start"]
        self.vel = [0.0,0.0]
        self.jumpstrength = 0.0
        self.jumps = 0
    
    def inputHandler(self):
        keys = pg.key.get_pressed()
        if keys[pg.K_d]:
            print("right")
            self.vel[0] = min(self.vel[0] + self.acc*1/60.0, self.maxspeed)
        if keys[pg.K_a]:
            print("left")
            self.vel[0] = max(self.vel[0] - self.acc*1/60.0, -self.maxspeed)
        if keys[pg.K_w]:
            print("up")
        if keys[pg.K_s]:
            print("down")
        if keys[pg.K_SPACE]:
            print("space")
            self.jumpstrength = min(self.maxjump , self.jumpstrength + 8.0)

    def jump(self):
        if self.jumps < 2: 
            self.vel[1] += self.jumpstrength
            print(self.jumpstrength)
            self.jumpstrength *= 0.4
            self.jumps +=1

    def collision(self, side:str, colobject:Sprite, instance:list):
        print("player collision", side)
        if side == "l":
            print("left")
            if self.vel[0] < 0.0: self.vel[0] = 0.0
        elif side == "r":
            print("right")
            if self.vel[0] > 0.0: self.vel[0] = 0.0
        elif side == "t":
            print("top")
        elif side == "b":
            if self.vel[1]<0.0 : self.vel[1] = 0.0
            if self.vel[0] >= 0.1 or self.vel[0] <= -0.1: self.vel[0] *= (abs(abs(self.vel[0])-colobject.friction * 1/60.0))/abs(self.vel[0])
            else: self.vel[0] = 0.0
            self.pos[1] = instance[1]*32+(colobject.box[1]+self.box[1])/2
            self.jumps = 0
        
        
    def update(self, dt:float, physics:dict):
        self.vel[1] -= physics["gravity"]*dt
        self.pos[0] += self.vel[0]*dt
        self.pos[1] += self.vel[1]*dt

    def render(self, screen):
        screen.blit(self.image, (int(self.pos[0]-self.box[0]/2), int(screen.get_height() - self.pos[1]-self.box[1]/2)))

class spritesheet(object):
    def __init__(self, filename):
        try:
            self.sheet = pg.image.load(filename).convert_alpha()
        except pg.error:
            print ('Unable to load spritesheet image:', filename)
            raise (SystemExit)
    # Load a specific image from a specific rectangle
    def image_at(self, rectangle, colorkey = None):
        "Loads image from x,y,x+offset,y+offset"
        rect = pg.Rect(rectangle)
        image = pg.Surface(rect.size).convert()
        image.blit(self.sheet, (0, 0), rect)
        if colorkey is not None:
            if colorkey is -1:
                colorkey = image.get_at((0,0))
            image.set_colorkey(colorkey, pg.RLEACCEL)
        return image
    # Load a whole bunch of images and return them as a list
    def images_at(self, rects, colorkey = None):
        "Loads multiple images, supply a list of coordinates" 
        return [self.image_at(rect, colorkey) for rect in rects]
    # Load a whole strip of images
    def load_strip(self, rect, image_count, colorkey = None):
        "Loads a strip of images and returns them as a list"
        tups = [(rect[0]+rect[2]*x, rect[1], rect[2], rect[3])
                for x in range(image_count)]
        return self.images_at(tups, colorkey)

class SpriteStripAnim(object):
    """sprite strip animator
    
    This class provides an iterator (iter() and next() methods), and a
    __add__() method for joining strips which comes in handy when a
    strip wraps to the next row.
    """
    def __init__(self, filename, rect, count, colorkey=None, loop=False, frames=1):
        """construct a SpriteStripAnim
        
        filename, rect, count, and colorkey are the same arguments used
        by spritesheet.load_strip.
        
        loop is a boolean that, when True, causes the next() method to
        loop. If False, the terminal case raises StopIteration.
        
        frames is the number of ticks to return the same image before
        the iterator advances to the next image.
        """
        self.filename = filename
        ss = spritesheet(filename)
        self.images = ss.load_strip(rect, count, colorkey)
        self.i = 0
        self.loop = loop
        self.frames = frames
        self.f = frames
    def iter(self):
        self.i = 0
        self.f = self.frames
        return self
    def next(self):
        if self.i >= len(self.images):
            if not self.loop:
                raise StopIteration
            else:
                self.i = 0
        image = self.images[self.i]
        self.f -= 1
        if self.f == 0:
            self.i += 1
            self.f = self.frames
        return image
    def __add__(self, ss):
        self.images.extend(ss.images)
        return self
