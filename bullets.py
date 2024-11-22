#Program by Andrew Church 5/26/23
import pygame,audio,tools,random, math
from anim import AutoImage as AImg
from tools import world_log as wl
from math import sin,cos,radians,degrees,atan2
# from enemies import Template as enemytemplate

class BulletRAW(pygame.sprite.Sprite):
    # The basic host bullet
    # other bullet upgrades and such will use this bullet asset
    # then the hosts of this entity will track bullet placement and such
    # so for instance, TripleBullet spawns three of these and keeps track of them

    #DEFAULT IMAGE - rendered by pygame draw function
    image = pygame.Surface((10, 10), pygame.SRCALPHA)
    pygame.draw.circle(image, "black", (5, 5), 5)
    pygame.draw.circle(image, "white", (5, 5), 4)
    screen_rect = pygame.Rect(0,0,pygame.display.play_dimensions[0],pygame.display.play_dimensions[1])

    def __init__(self, sprite_groups, dmg=1, speed=10, angle=0, start_pos:tuple = (0,0),texture = None, angle_isradians = False, **kwargs):
        pygame.sprite.Sprite.__init__(self)
        self.sprite_groups = sprite_groups
        # setting the image
        self.aimg = AImg(host=self,name=texture,current_anim='idle',force_surf = BulletRAW.image) 
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
            wl['hits'] += 1
            # audio.play_sound("smallboom0.wav")



# NOTE there is a lot of repeating code here
# there are a lot of spots where I am copying all of defaultbullet.shoot even though I could make it a function
# however these little variations make it tricky and I am not overengineering this when I have a job to do.
        

class DefaultBullet():
    spawned = [ ]
    enemylist = [ ] 
    enemy_parent_class = None # the game sets this after everything is set up and done, because this file can't import enemies 
    
    def shoot(player,sprite_groups) -> bool:
        # if the player hasn't run out of bullets
        DefaultBullet.update_size_info()
        if len(DefaultBullet.spawned) < player.bullet_max:
            #it spawns the bullet as requested, and logs it
            itm = BulletRAW(sprite_groups=sprite_groups,dmg=player.bullet_dmg,speed=15,angle=270,start_pos=player.rect.center)
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
    def shoot(player,sprite_groups):
        # if the player hasn't run out of bullets
        DefaultBullet.update_size_info()
        if len(DefaultBullet.spawned) < (player.bullet_max*3): #bullet max is tripled since youre sending out three times as many bullets
            #it spawns the bullet as requested, and logs it
            for i in (250,270,290):
                itm = BulletRAW(sprite_groups=sprite_groups,dmg=player.bullet_dmg,speed=15,angle=i,start_pos=player.rect.center)
                sprite_groups[1].add(itm)
                DefaultBullet.spawned.append(itm)
            return True
        else:
            return False

class RocketMissile(DefaultBullet):
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
            itm = BulletRAW(sprite_groups=sprite_groups,dmg=player.bullet_dmg,speed=15,angle=angle,start_pos=player.rect.center,angle_isradians = (pick!=None))
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
    # a slow moving, bigger bullet
    def shoot(player,sprite_groups) -> bool:
        # if the player hasn't run out of bullets
        DefaultBullet.update_size_info()
        if len(DefaultBullet.spawned) < player.bullet_max:
            #it spawns the bullet as requested, and logs it
            itm = BulletRAW(sprite_groups=sprite_groups,dmg=player.bullet_dmg,speed=15,angle=270,start_pos=player.rect.center)
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
    "triple":TripleBullet,
    "rocket":RocketMissile,
    "bomb":BombMissile,
    "wide":WideShot
}
