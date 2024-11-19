#PROGRAM BY ANDREW CHURCH - test?
import pygame,os,json


# 5/8/23 - FIXING THE SPRITESHEETS
# the way spritesheets work right now is that the loaded images are stored in the spritesheet object upon creation
# this is not optimized, as that means each character will have an new instance of all the images again
# to negate this, there is going to be a dict called "all loaded spritesheets" that all sprites have by default, which contains a dictionary for all the character files loaded 
all_loaded_spritesheets = {}
all_loaded_images = {}


    
#5/8/23 - DEFINING THING TO LOAD ALL IMAGES
def get_image(sheet,
                  wh:tuple,
                  xy:tuple,
                  scale:float=1.0,
                  colorkey:tuple=(0,0,0)):
        #making empty surface
        output = pygame.Surface((wh[0],wh[1])).convert_alpha()
        output.fill(colorkey)
        #outputting parts of the image onto the surface
        output.blit(sheet,(0,0),(xy[0],xy[1],wh[0],wh[1]))
        #scaling
        output = pygame.transform.scale(output,(wh[0]*scale,wh[1]*scale)).convert_alpha()
        #"greenscreen"ing
        output.set_colorkey(colorkey)
        #output
        return output

def generate_sprite(data):
    spritesheet=[]
    raw=pygame.image.load(data["NAME"]+".png").convert_alpha()
    #LOADING ALL SPRITE IMAGES
    for row in range(data["ROWS/COLUMNS"][0]):
        #it's easier for me, screw off.
        for column in range(data["ROWS/COLUMNS"][1]):
            cur_img = get_image(sheet=raw,wh=data["TILE_SIZE"],
                    xy=(data["TILE_SIZE"][0]*column,data["TILE_SIZE"][1]*row),
                    scale=data["scale"],colorkey=data["colorkey"],).convert()
            cur_img = pygame.transform.flip(cur_img,flip_x=data['flipx'],flip_y=data['flipy'])
            if data['alpha'] != None and data['alpha'] != 255: cur_img.set_alpha(data['alpha'])
            if data['rotate'] != None: cur_img = pygame.transform.rotate(cur_img,data['rotate']).convert_alpha()
            spritesheet.append(cur_img)
    return spritesheet

def generate_masks(spritesheet):
    masks = []
    for sprite in spritesheet:
        masks.append(pygame.mask.from_surface(sprite))
    return masks

#06/01/2023 - USING ANIM_LOADLIST TO FIND OUT WHAT TO LOAD
with open("./data/anim_loadlist.json","r") as raw:
    anim_loadlist = json.load(raw)
#12/15/2023 - TAKING DEFAULT FILE
with open("./images/default.json") as raw:
    default = json.load(raw)


#06/01/2023 - REVAMP OF OLD CODE - LOADING THE ANIM LOADLIST
for directory,filelist in anim_loadlist.items():
    #There is no longer a break if there's no json, as the list contains all the json files needed without any scraping
    for filename in filelist:
        with open(directory+filename+".json") as raw:
            current_file = default.copy()
            current_file.update(json.load(raw))

        #generating spritesheet
        spritesheet = generate_sprite(current_file)
        masksheet = generate_masks(spritesheet)
        #adding to main directory, generating a spritesheet
        all_loaded_spritesheets[filename] = (current_file,spritesheet,masksheet)


        #loading animation files if existent
        if current_file["ANIM"] is not None:
            with open(str(directory)+"anim/"+str(current_file["ANIM"]),"r") as raw:
                anim_file = json.load(raw)
                all_loaded_spritesheets[filename][0]["anim"] = anim_file
            #5/25/23 - FIXING ANIMATION FPSes"
            for animation in anim_file.keys():
                anim_file[animation]["FPS"] = 60/anim_file[animation]["FPS"]
        #default image
        else:
            with open("./images/characters/anim/default.json","r") as raw:
                anim_file = json.load(raw)
                all_loaded_spritesheets[filename][0]["anim"] = anim_file
            #5/25/23 - FIXING ANIMATION FPSes"
            for animation in anim_file.keys():
                anim_file[animation]["FPS"] = 60/anim_file[animation]["FPS"]

# for v in all_loaded_spritesheets.values():
#     for val in v:
#         print(val,end='\n--------')
#     print("\n"*20)

#06/01/2023 - LOADING NON-ANIMATED IMAGES
with open("./data/img_loadlist.json","r") as raw:
    img_loadlist = json.load(raw)
for directory,filelist in img_loadlist.items():
    #06/22/2023 - RESIZING IMAGES
    # The last index of the loadlist will be 'resize', with each index being [imagename, [width,height]]
    if directory == "resize":
        for filename in filelist:
            all_loaded_images[str(filename[0])] = pygame.transform.scale(all_loaded_images[str(filename[0])],filename[1])
        continue
    for filename in filelist:
        all_loaded_images[str(filename)] = pygame.image.load(directory+filename).convert_alpha()

#ADDING EXTRA COLORS
all_loaded_images['black'] = pygame.Surface((10,10))
all_loaded_images['black'].fill("#000000")

all_loaded_images['greenblock'] = pygame.Surface((5,5))
pygame.draw.rect(all_loaded_images['greenblock'],color=(0,128,0),rect=pygame.Rect(0,0,5,5))
pygame.draw.rect(all_loaded_images['greenblock'],color=(0,255,0),rect=pygame.Rect(1,1,3,3))

all_loaded_images['redblock'] = pygame.Surface((5,5))
pygame.draw.rect(all_loaded_images['redblock'],color=(128,0,0),rect=pygame.Rect(0,0,5,5))
pygame.draw.rect(all_loaded_images['redblock'],color=(255,0,0),rect=pygame.Rect(1,1,3,3))

all_loaded_images['bwblock'] = pygame.Surface((5,5))
pygame.draw.rect(all_loaded_images['bwblock'],color=(0,0,0),rect=pygame.Rect(0,0,5,5))
pygame.draw.rect(all_loaded_images['bwblock'],color=(255,255,255),rect=pygame.Rect(1,1,3,3))


NONE = pygame.Surface((10,10)).convert_alpha()
NONE.fill(pygame.Color(0,0,0,0))

all_loaded_images["NONE"] = NONE

"""
#5/8/23 - LOADING IN ALL IMAGES WITH DATA
jsonlist = os.listdir("./images/characters")
for item in jsonlist:
    #breaking if not json, OR if the "anim" keyword is detected
    if ".json" not in item or "anim" in item: continue
    #going through with everything
    with open("./images/characters/"+str(item),"r") as raw:
        file = json.load(raw)
    #adding to the main dictionary
    all_loaded_spritesheets[item] = (file,generate_sprite(file))
    #5/11/23 - LOADING ANIMATION FILES IF EXISTANT
    if file["ANIM"] is not None:
        with open("./images/characters/"+str(file["ANIM"]),"r") as raw:
            anim_file = json.load(raw)
            all_loaded_spritesheets[item][0]["anim"] = anim_file
        #5/25/23 - FIXING ANIMATION FPSes"
        for animation in anim_file.keys():
            anim_file[animation]["FPS"] = 60/anim_file[animation]["FPS"]
"""


# 5/8/23 - WHAT DO THE SPRITESHEETS DO?
# the spritesheet class is going to refer to the all_loaded_spritesheets dict and pull from it
# this is a way for all sprites to use the same cookie-cutter layout and hook to them fine
# earlier, it would load the spritesheets and everything, in the class. However, as read above, this would cause repeated loaded images with the creation of each character.
# spritesheet will, now, just know what frames are what. it's better for organization
# EDIT EVERYTHING IN THE JSON FILES ON YOUR OWN. YOU HEAR ME? I SWEAR TO GOD. I HATE YOU ALL.
class Spritesheet():
    def __init__(self,
                 name:str,
                 current_anim:str = None,
                 all_loaded_spritesheets:dict = all_loaded_spritesheets,
                 resize:tuple=None
                 ): #DO NOT CONTAIN EXTENSION IN PATH

        
        #DEFINITIONS
        self.name = name
        self.all_loaded_spritesheets = all_loaded_spritesheets #for external use
        self.all_anim = dict(all_loaded_spritesheets[name][0]["anim"].copy()) #self-explanatory
        self.current_anim = current_anim #current animation played
        self.current_anim_loop = 0 #amount of loops
        self.current_anim_frame = 0 #frame of animation; NOTE THIS IS THE INDEX OF THE all_anim["frames"] TUPLE, NOT SPRITESHEETS
        self.current_anim_frame_len = 0 #length of frame of animation
        self.image_displayed = 0 #the index of self.spritesheet; callback to actual sprite played\\
        self.resize = resize
        self.image = all_loaded_spritesheets[self.name][1][self.image_displayed]
        self.mask = all_loaded_spritesheets[self.name][2][self.image_displayed]
        if self.resize is not None: self.image = pygame.transform.scale(self.image,self.resize)
        self.changed = False #a way to tell if the image was changed, so the image isn't being reset every frame
        self.looped = False #a checker for emblem to tell if an asset should be deleted

    def update(self) -> pygame.Surface: #this will be called every frame in the respective sprite
        #print("---\n",self.current_anim,self.image_displayed,self.current_anim_frame,self.current_anim_frame_len,sep="|")

        #error checking
        if self.current_anim not in self.all_anim.keys() or type(self.all_anim) is None or len(self.all_anim) < 1:
            return
        
        self.current_anim_frame_len += 1
        
        #updating animation frame
        if self.current_anim_frame_len >= self.all_anim[self.current_anim]["FPS"]:
            # print('updated frame')
            self.current_anim_frame+=1
            self.current_anim_frame_len=0
            self.changed = True
            
        #updating animation being played
        if self.current_anim_frame >= len(self.all_anim[self.current_anim]["frames"]):
            # print('updated animation')
            #updating if loop
            self.current_anim_loop += 1
            self.current_anim_frame = 0
            #if the loop is complete
            if self.current_anim_loop >= self.all_anim[self.current_anim]["loop"]:
                # print('animation loop completed')
                self.current_anim_loop = 0
                self.current_anim = self.all_anim[self.current_anim]["return_to"]
            self.looped = True

        #updating the actual current image being used, as a numerical frame
        self.image_displayed = self.all_anim[self.current_anim]["frames"][self.current_anim_frame]

        #changing values if needed to
        if self.changed:
            self.image = all_loaded_spritesheets[self.name][1][self.image_displayed]
            self.mask = all_loaded_spritesheets[self.name][2][self.image_displayed]

            if self.resize is not None: self.image = pygame.transform.scale(self.image,self.resize)
            self.changed = False #resetting

        
    
    def change_anim(self,new:str,overwrite:bool=False):
        #checking for if the animation even exists
        if new not in self.all_anim.keys():return
        #checking for if the animation is "interruptable" - for the record, you are able to add "interruptable" to an animation and mark it False to make no other animation take priority over it
        if "interrupt" in self.all_anim[self.current_anim].keys() and not self.all_anim[self.current_anim]["interrupt"] and not overwrite:return
        #resets all frames, changes current animation
        self.current_anim = new
        self.current_anim_frame = 0
        self.current_anim_frame_len = 0
        self.current_anim_loop = 0 
        #automatically changing the image so it works (only noticeable with low FPS)
        self.image = all_loaded_spritesheets[self.name][1][self.image_displayed]





#AUTOIMAGE CLASS
# A LOT of entity classes in this game have to manually check for animations and such, or if it's just using a static image
# However, this class is going to streamline it, by doing all the checking for spritesheets on its own
class AutoImage():
    def __init__(self,
                host = None,
                name:str=None,
                current_anim:str='idle',
                force_surf:pygame.Surface=None,
                resize=None,
                generate_rect:bool=True):
        self.host=host
        self.hashost = host is not None
        self.name = name
        self.spritesheet = None
        self.image = None
        #figuring out what kind of asset to use
        self.type = AutoImage.fetch_info(name=self.name)
        if self.type == 'img':
            self.image = all_loaded_images[self.name]
            if resize is not None: self.image = pygame.transform.scale(self.image,resize)
        elif self.type == 'anim':
            self.spritesheet = Spritesheet(name=self.name,current_anim=current_anim,resize=resize)
            self.image = self.spritesheet.image
        elif force_surf is not None:
            self.image = force_surf
            if resize is not None: self.image = pygame.transform.scale(self.image,resize)
        else:
            self.image = all_loaded_images['placeholder.bmp']
            if resize is not None: self.image = pygame.transform.scale(self.image,resize)
        self.mask = pygame.mask.from_surface(self.image)


        #HOST INFORMATION
        #Now, instead of each and every single sprite managing the image, rect, and mask info, the spritesheet will do it itself!
        if self.hashost:
            self.host.image = self.image
            self.host.mask = self.mask
            if generate_rect:
                self.host.rect = self.image.get_rect()
    
    def update(self):
        if self.spritesheet is not None: 
            self.spritesheet.update()
            self.image = self.spritesheet.image
            self.mask = self.spritesheet.mask

        #setting the host's imge and mask
        if self.hashost:
            self.host.image = self.image
            self.host.mask = self.mask 
    
    def change_anim(self,anim:str,overwrite:bool=False):
        if self.spritesheet is not None:
            self.spritesheet.change_anim(anim,overwrite=overwrite)


    @staticmethod
    def fetch_info(name:str = "placeholder.bmp") -> str:
        #checking to see if the name is an image
        if name in all_loaded_images.keys():
            return 'img'
        elif name in all_loaded_spritesheets.keys():
            return 'anim'
        else:
            return 'err'



#a white flashing effect
#it flashes white what else do you want me to say 
class WhiteFlash(pygame.sprite.Sprite): # asks you for a surface, then draws a surface to it, slowly disappearing
    def __init__(self,surface:pygame.Surface,start_val:float=255,end_val:float=0,spd:float=10.0,img:str=None,color:str="#FFFFFF",isreverse=False):
        pygame.sprite.Sprite.__init__(self)

        self.vals=[start_val,end_val,spd]

        #figuring out the image, whether it be a blank color or a predefined image 
        image = pygame.Surface(surface.get_size()).convert_alpha()
        image.fill(color=color)

        self.autoimage = AutoImage(host=self,name=img,resize=surface.get_size(),force_surf=image)

        #setting the current transparency
        self.image.set_alpha(self.vals[0])
        self.rect=self.image.get_rect()
        #checking for hurt
        self.reverse = isreverse #a checker to see if the flash is going in the opposite direction or not. this doesn't change the amount being subtracted but it changes the kill check
        #checking for finished
        self.finished = False

    def update(self):
        #image hooray
        self.autoimage.update()
        self.image = self.autoimage.image

        #slowing lowering the transparency values
        self.vals[0] -= self.vals[2]
        if (not self.reverse and (self.vals[0] < self.vals[1])) or (self.reverse and (self.vals[0] > self.vals[1])): 
            self.finished=True
            self.kill()

        #setting the alpha
        self.image.set_alpha(self.vals[0])

    def on_collide(self,collide_type:int,collided:pygame.sprite.Sprite):
        if collide_type == 1:
            collided.hurt()
        



#generating enemies based on current world
def generate_enemy_log(world_data:dict) -> pygame.Surface:
    surface = all_loaded_images['enemylog.png'].copy()
    skins = world_data['skins']
    skinskeys = tuple(skins.keys())
    for i in range(len(skinskeys)):
        enemy = AutoImage(name=skins[skinskeys[i]],resize=(60,60)).image
        surface.blit(enemy,(i*75,35))
    return surface


