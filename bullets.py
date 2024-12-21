#Program by Andrew Church 5/26/23
import pygame,audio,tools,random, math,anim
import gameplay_log as log
from anim import AutoImage as AImg
from math import sin,cos,radians,degrees,atan2

# from enemies import Template as enemytemplate

class BulletRAW(pygame.sprite.Sprite):
    # The basic host bullet
    # other bullet upgrades and such will use this bullet asset
    # then the hosts of this entity will track bullet placement and such
    # so for instance, TripleBullet spawns three of these and keeps track of them

    #DEFAULT IMAGE - rendered by pygame draw function
    image = pygame.Surface((16, 16), pygame.SRCALPHA)
    pygame.draw.circle(image, "black", (8, 8), 8)
    pygame.draw.circle(image, "white", (8, 8), 6)
    screen_rect = pygame.Rect(0,0,pygame.display.play_dimensions[0],pygame.display.play_dimensions[1])

    def __init__(self, sprite_groups, dmg=1, speed=10, angle=0, start_pos:tuple = (0,0),texture = None, angle_isradians = False, **kwargs):
        pygame.sprite.Sprite.__init__(self)
        self.sprite_groups = sprite_groups
        # setting the image
        self.aimg = AImg(host=self,name=texture,current_anim='idle',force_surf = BulletRAW.image,resize=kwargs['resize'] if 'resize' in kwargs.keys() else None) 
        # setting info 
        self.dmg = dmg
        self.health = 1 #the enemy will know how much to damage itself based off dmg value, so there's no need for more health because thats more code loops
        self.speed = speed
        self.angle = angle
        self.angle_isradians = angle_isradians #this is a flag where if it's true it doesn't convert the angle to radians
        if not angle_isradians:
            self.angle = radians(self.angle)
        # figuring out what to move based on angle

        self.move_vals_raw = (cos(self.angle),sin(self.angle))
        self.move_vals = self.move_vals_raw[0]*speed,self.move_vals_raw[1]*speed
        # placing self
        self.start_pos = start_pos
        self.rect.center = start_pos

        #updating log that a bullet was shot
        log.log_zone["shots"] += 1
    
    def update(self):
        self.aimg.update()
        # updating
        if not self.on_screen() or self.health <= 0:
            self.kill()
        # moving
        self.rect.x += self.move_vals[0]
        self.rect.y += self.move_vals[1]

    def hurt(self):
        self.health -= 1
        
    def on_collide(self,collide_type,collided):
        ...

    def on_screen(self) -> bool:
        return pygame.display.play_rect.colliderect(self.rect)

    def kill(self):
        pygame.sprite.Sprite.kill(self)
        # Bullet.count = Bullet.count - 1 if Bullet.count > 0 else 0 
        if self.health <= 0:
            for i in range(5):self.sprite_groups[0].add(BulletParticle(self.rect.center))
            #updating the 'hits' counter. this means that the accuracy is different from the kills
            log.log_zone['hits'] += 1
            # audio.play_sound("smallboom0.wav")



# NOTE there is a lot of repeating code here
# there are a lot of spots where I am copying all of defaultbullet.shoot even though I could make it a function
# however these little variations make it tricky and I am not overengineering this when I have a job to do.
        

class DefaultBullet():
    spawned = [ ]
    enemylist = [ ] 
    enemy_parent_class = None # the game sets this after everything is set up and done, because this file can't import enemies 
    icon="icon_dmgup.png"
    def shoot(player,sprite_groups) -> bool:
        # if the player hasn't run out of bullets
        DefaultBullet.update_size_info()
        if len(DefaultBullet.spawned) < player.bullet_max:
            #it spawns the bullet as requested, and logs it
            itm = BulletRAW(sprite_groups=sprite_groups,dmg=player.bullet_dmg,speed=15,angle=270,start_pos=player.rect.center,)
            sprite_groups[1].add(itm)
            DefaultBullet.spawned.append(itm)
            return True
        else:
            return False


    def update_size_info():
        # checking for living entities and updates the spawned list for it
        newspawned = [ ] 
        for itm in DefaultBullet.spawned:
            if itm.alive():
                newspawned.append(itm)
        DefaultBullet.spawned = newspawned

    def update_enemylist(group:pygame.sprite.Group):
        newenemylist = []
        for itm in group:
            if DefaultBullet.enemy_parent_class in type(itm).__bases__:
                newenemylist.append(itm)
            else:
                ...
                # print(type(itm).__bases__)
        DefaultBullet.enemylist = newenemylist




class TripleBullet(DefaultBullet):
    icon="icon_tripleshot.png"
    angles = (250,270,290)
    images = ("triple_shot-1.png","triple_shot-2.png","triple_shot-3.png")
    def shoot(player,sprite_groups):
        # if the player hasn't run out of bullets
        DefaultBullet.update_size_info()
        if len(DefaultBullet.spawned) < (player.bullet_max*3): #bullet max is tripled since youre sending out three times as many bullets
            #it spawns the bullet as requested, and logs it
            for i in range(3):
                itm = BulletRAW(sprite_groups=sprite_groups,dmg=player.bullet_dmg,speed=15,angle=TripleBullet.angles[i],start_pos=player.rect.center,)
                sprite_groups[1].add(itm)
                DefaultBullet.spawned.append(itm)
            return True
        else:
            return False

class RocketMissile(DefaultBullet):
    icon="icon_rocketshot.png"

    def shoot(player,sprite_groups):
        # indexes enemies
        DefaultBullet.update_enemylist(sprite_groups[2])
        # acts as a normal bullet with no target
        pick = None
        angle = 270
        if len(DefaultBullet.enemylist) > 0:
            pick = random.choice(DefaultBullet.enemylist)
            angle = atan2(pick.rect.centery - player.rect.centery, pick.rect.centerx - player.rect.centerx)
            
        # if the player hasn't run out of bullets
        DefaultBullet.update_size_info()
        if len(DefaultBullet.spawned) < player.bullet_max:
            #it spawns the bullet as requested, and logs it
            itm = BulletRAW(sprite_groups=sprite_groups,dmg=player.bullet_dmg,speed=15,angle=angle,start_pos=player.rect.center,angle_isradians = (pick!=None),)
            sprite_groups[1].add(itm)
            DefaultBullet.spawned.append(itm)
            return True
        else:
            return False


    def update_size_info():
        # checking for living entities and updates the spawned list for it
        newspawned = [ ] 
        for itm in DefaultBullet.spawned:
            if itm.alive():
                newspawned.append(itm)
        DefaultBullet.spawned = newspawned

   
        

class BombMissile(DefaultBullet):
    ...


class WideShot(DefaultBullet):
    icon="icon_wideshot.png"
    
    # a slow moving, bigger bullet
    def shoot(player,sprite_groups) -> bool:
        # if the player hasn't run out of bullets
        DefaultBullet.update_size_info()
        if len(DefaultBullet.spawned) < player.bullet_max:
            #it spawns the bullet as requested, and logs it
            itm = BulletRAW(sprite_groups=sprite_groups,dmg=player.bullet_dmg,speed=5,angle=270,start_pos=player.rect.center,)
            sprite_groups[1].add(itm)
            DefaultBullet.spawned.append(itm)
            return True
        else:
            return False



class Item(pygame.sprite.Sprite):
    def __init__(self):...


def emptyBulletMax():
    return


class BulletParticle(pygame.sprite.Sprite):
    def __init__(self,pos:tuple = (0,0),texture="bwblock"):
        pygame.sprite.Sprite.__init__(self)
        self.aimg = AImg(host=self,name=texture,current_anim='idle')
        self.rect.center = pos
        self.gravity_info = [
            random.uniform(-5,5), #x movement
            random.uniform(-5,-1), #y gravity
        ]
        self.duration = 0 

    def update(self):
        #moving x
        self.rect.x += self.gravity_info[0]
        #moving y
        self.rect.y += self.gravity_info[1]
        #changing x gravity
        self.gravity_info[0] = round(self.gravity_info[0]*0.98,5) if abs(self.gravity_info[0]) > 0.001 else 0
        #changing y gravity
        self.gravity_info[1] = self.gravity_info[1]+0.5 if self.gravity_info[1] < 7 else 7
        #updating duration information
        self.duration += 1
        #autokill
        if self.duration > 15:
            self.kill()



LOADED = {
    "default":DefaultBullet,
    "tripleshot":TripleBullet,
    "rocket":RocketMissile,
    "bomb":BombMissile,
    "wide":WideShot
}




# OTHER BULLETS NOT USED FROM A PLAYER -- THESE ARE CLASSIFIED AS BULLETS IN MY EYES

#EXTRA ASSETS -- SPECIAL YIPPEE CONFETTI
class Confetti(pygame.sprite.Sprite):
    #all potential images to be used
    images = []
    for color in ["red","green","blue","purple","orange","pink"]:
        surf = pygame.Surface((10,10))
        pygame.draw.rect(surf,color=color,rect=pygame.Rect(0,0,10,10))
        images.append(surf)
    mask = pygame.mask.from_surface(images[0])
    def __init__(self,pos=(0,0)):
        pygame.sprite.Sprite.__init__(self)
        self.image = random.choice(Confetti.images)
        self.mask = Confetti.mask
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.mask = pygame.mask.from_surface(self.image)
        self.gravity_info = [
            random.randint(-10,10), #x movement
            random.randint(-15,-5), #y gravity
        ]
        self.duration = 0 

    def update(self):
        #moving x
        self.rect.x += self.gravity_info[0]
        #moving y
        self.rect.y += self.gravity_info[1]

        #changing x gravity
        self.gravity_info[0] = round(self.gravity_info[0]*0.98,5) if abs(self.gravity_info[0]) > 0.001 else 0
        #changing y gravity
        self.gravity_info[1] = self.gravity_info[1]+0.5 if self.gravity_info[1] < 7 else 7


        #updating duration information
        self.duration += 1
        #autokill
        if self.duration > 240 or self.rect.top>800:
            self.kill()
        
        
    def on_collide(self,
                   collide_type:int, #the collide_type refers to the sprite group numbers. 0 for universal (not used), 1 for other player elements, 2 for enemies
                   collided:pygame.sprite.Sprite,
                   ):
        #5/26/23 - Updating health shizznit if interaction with "player type" class
        # if collide_type == 1 or collide_type == 3:
        #     self.health -= 1
        #if colliding with an enemy, either hurt or bounce based on positioning
        if type(collided) == Player :
            collided.hurt()
            #damaging the enemy either way
            self.kill()
        elif collide_type == 1:
            #I SAID damaging the enemy either way
            self.kill()
            collided.hurt()
            


#EXTRA ASSETS -- SPECIAL LUMEN LASER
class Laser(pygame.sprite.Sprite):
    def __init__(self,start_pos=(0,0),angle=45,length=1000):
        pygame.sprite.Sprite.__init__(self)
        #laser image code
        self.image = pygame.Surface(pygame.display.play_dimensions,pygame.SRCALPHA).convert_alpha() #a rect that spans the ENTIRE SCREEN, as only the mask is used for collision
        
        #CODE FROM kadir014 on github.io, will change around myself later
        start = pygame.Vector2(start_pos[0],start_pos[1])
        end = start + pygame.Vector2(length,0).rotate(angle)
        pygame.draw.line(self.image,'red',start,end,15)

        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        #duration
        self.duration = 0 
    def update(self):
        #it just sits there for a quarter of a second,lol
        self.duration += 1
        if self.duration > 15:
            self.kill()
    def on_collide(self,
                   collide_type:int, #the collide_type refers to the sprite group numbers. 0 for universal (not used), 1 for other player elements, 2 for enemies
                   collided:pygame.sprite.Sprite,
                   ):
        #5/26/23 - Updating health shizznit if interaction with "player type" class
        # if collide_type == 1 or collide_type == 3:
        #     self.health -= 1
        #if colliding with an enemy, either hurt or bounce based on positioning
        if type(collided) == Player :
            collided.hurt()
        elif collide_type == 1:
            collided.hurt()


#EXTRA ASSETS -- WARNING SIGN
class WarningSign(pygame.sprite.Sprite):
    arrow = anim.all_loaded_images['arrow.png']
    def __init__(self,pos,resize=None,arrow_pos=None,time:int=-1):
        pygame.sprite.Sprite.__init__(self)
        #spritesheet info
        self.aimg = AImg(host=self,name='warning',current_anim='idle')
        self.aimg.spritesheet.all_anim['idle'] = self.aimg.spritesheet.all_anim['idle'].copy()
        self.arrow = WarningSign.arrow.copy()
        self.rect.center = pos 

        self.time = time
        self.timer = 0

        self.arrow_rect = self.arrow.get_rect()
        self.arrow_rect.center = self.rect.center

    def update(self):
        self.aimg.update()
        #timer code
        self.timer += 1
        if self.time > -1 and self.timer > self.time:
            self.kill()

    def update_pos(self,pos):
        self.rect.center = pos
    def update_intensity(self,fps:int):
        self.aimg.spritesheet.all_anim['idle']['FPS'] = 60/fps
        self.update()
        # print('after',fps,self.spriteshet.all_anim['idle']['FPS'])


#EXTRA ASSETS -- HURTBULLET
class HurtBullet(pygame.sprite.Sprite):
    #DEFAULT IMAGE - rendered by pygame draw function
    image = pygame.Surface((10, 10), pygame.SRCALPHA)
    pygame.draw.circle(image, "#AA0000", (5, 5), 5)
    pygame.draw.circle(image, "red", (5, 5), 4)
    screen_rect = pygame.Rect(0, 0, 450, 600)

    #limits so the game doesnt lag
    count = 0
    max = 1000

    def __init__(self,type:str="point",spd:int=2,info:tuple=((0,0),(100,100)),texture:str=None,resize:tuple = None):
        #FOR AN ANGLE, the info is (pointa,angle)
        pygame.sprite.Sprite.__init__(self)
        
        #checking for max bullet count
        HurtBullet.count += 1
        self.killonstart = True if HurtBullet.count > HurtBullet.max else False

        #setting number values
        if type == "point":
            self.move = tools.MovingPoint(pointA=info[0],pointB=info[1],speed=spd)
        elif type == "angle":
            self.move = tools.AnglePoint(pointA=info[0],angle=info[1],speed=spd)
        self.health = 1
        
        #setting image
        self.aimg = AImg(host=self,name=texture,current_anim='idle',force_surf = HurtBullet.image,resize = resize)
        self.rect.center = self.move.position
        self.dead = False
        
    def update(self):
        self.move.update()
        self.rect.center = self.move.position
        self.aimg.update()
        if not BulletRAW.on_screen(self) or self.health <= 0 or self.killonstart: 
            self.kill()
            HurtBullet.count = HurtBullet.count - 1 if HurtBullet.count > 0 else 0 
    
    def on_collide(self,collide_type,collided):
        #5/26/23 - This is usually explained elsewhere
        #collision with enemy types
        if type(collided) == Player:
            self.hurt()
            collided.hurt()
    
    def hurt(self):
        self.health -= 1

    def kill(self):
        pygame.sprite.Sprite.kill(self)
        self.dead=True
 

#EXTRA ASSETS -- COIN
class Coin(pygame.sprite.Sprite):
    #The coin is an item spawned when an enemy dies. There are chances that an enemy drops items, but for the most part they drop coins.
    #These coins wager your score, meaning you sacrifice your score for upgrades in the item shop. 
    val_list = (1,5,10,25,50,100)
    def __init__(self,pos:tuple,floor:int,value:int=1,player = None):
        pygame.sprite.Sprite.__init__(self)
        img="1"
        for val in Coin.val_list:
            if value <= val:
                break
            else:
                continue
        else:
            img = str(val)

        # print(img)
        self.aimg = AImg(host=self,name="coin",current_anim=img,resize=(20,20))
        self.value = value

        self.floor = floor
        self.original_v = [random.randint(-2,2),random.randint(-7,-2)]
        self.v = self.original_v.copy()
        self.rect.center = pos
        self.lifespan = 1
        self.bounce = 0 

        self.player = player

    def update(self):
        #image
        self.aimg.update()
        #lifespan
        self.lifespan += 1
        if self.lifespan > 240:
            self.kill()
        #moving
        self.rect.x += self.v[0]
        self.rect.y += self.v[1]
        #updating velocities
        if abs(self.v[0]) > 0.1: self.v[0] *= 0.95
        else: self.v[0] = 0 
        self.v[1] += 0.25
        #bouncing
        if self.rect.y > self.floor:
            if self.v[1] > 0: 
                self.v[1] *= -.25
                self.bounce += 1

        # player magnet code
        if self.player is not None and self.player.perks['magnet']:
            self.rect.x +=( (self.player.rect.centerx-self.rect.centerx) / 25)

    def on_collide(self,collide_type,collided):
        if type(collided) == Player:
            # updating the coins value from player
            collided.coins += self.value
            self.kill()
            # graphical effects
            for i in range(5):
                self.player.sprite_groups[0].add(BulletParticle(pos=self.rect.center,texture="greenblock"))


