#Code by Andrew Church
import pygame,text,math,random,anim
from tools import MovingPoint as MP

#07/30/2023 - ADDING EMBLEM SPRITES
# These are going to be little sprites that are able to just show a normal ass surface with the ability to move from place to place
# This is mostly going to be used for the border, along with the level icons and scores and stuff.
class Emblem(pygame.sprite.Sprite):
    def __init__(self,
    im:str=None,coord:tuple=(0,0), isCenter:bool=False,
    animation_killonloop:bool=False,
    pattern:str=None,
    force_surf:pygame.Surface=None,
    resize=None,current_anim="idle",hide:bool=False, **kwargs
    ):
        pygame.sprite.Sprite.__init__(self)
        
        self.orig_coord = coord[:] #an original coordinate to go to when hidden, most likely
        self.coord = coord[:]
        self.coord_dest = coord[:] #where the coordinate is currently moving to. TWEENING

        #TWEEN INFORMATION
        self.tweens = {
            "move":[], #current position, target position, speed, wait, done, movingpoint, isCenter
            "rotate":[], #current angle, target angle, speed, wait, done
        }

        self.pattern = pattern #None = Not playing, then anything else is an animation playing
        self.pattern_f = 0 #frames in a pattern
        self.pattern_offset = [0,0] #what pattern affects

        self.aimg = anim.AutoImage(host=self,name=im,force_surf=force_surf,resize=resize,current_anim=current_anim)
        self.animation_killonloop = animation_killonloop

        self.rect = self.image.get_rect() #finally setting rect
        self.rect.topleft = self.coord
        self.dead = False
        self.hide = hide


        if isCenter:
            self.change_pos(coord,isCenter=True)

    def update(self):
        if self.pattern is not None: self.pattern_f += 1; self.play_pattern()
        self.rect.topleft = self.coord[0]+self.pattern_offset[0],self.coord[1]+self.pattern_offset[1]
        self.aimg.update()

        #checking for kill condition
        if self.animation_killonloop and self.aimg.spritesheet != None and self.aimg.spritesheet.looped:
            self.kill()

        #updating the tweens
        if len(self.tweens['move']) > 5 and not self.tweens['move'][4]:
            self.tween_pos()

        #what the hell
        # print(self.rect.center)

    
    def play_pattern(self):
        if self.pattern == "sine":
            self.pattern_offset[1] = math.sin(self.pattern_f/10)*10
        if self.pattern == "jagged":
            self.pattern_offset[0] = random.randint(-2,2)
            self.pattern_offset[1] = random.randint(-2,2)
    


    #instantly changing the position
    def change_pos(self,pos:tuple,isCenter:bool=False):
        if isCenter:
            self.rect.center = pos
            self.coord = self.rect.topleft
        else:
            self.coord = pos


    def reset_coord(self):
        self.coord = self.orig_coord[:]

    def update_number(self,number,rect=True):
        ...

    def kill(self):
        pygame.sprite.Sprite.kill(self)
        self.dead=True
        

    def add_tween_pos(self,cur_pos:tuple,target_pos:tuple,speed:float,started:bool=False,isCenter:bool=False):
        #adding a tween effect based on the current position
        self.tweens['move'] = [cur_pos,target_pos,speed,started,False,None,isCenter]
        self.tweens['move'][5] = (MP(pointA=cur_pos,pointB=target_pos,speed=speed,ignore_speed=False,check_finished=True))


    def tween_pos(self) :
        #exiting if being held
        if (not self.tweens['move'][3]) or (self.tweens['move'][4]):return
        move = self.tweens['move'][5]
        #updating movement
        move.update()
        move.speed = self.tweens['move'][2]
        self.change_pos(pos = move.position, isCenter = self.tweens['move'][6])
        #finishing
        if move.finished:
            self.tweens['move'][4] = True
            self.change_pos(pos = self.tweens['move'][1][:], isCenter = self.tweens['move'][6])

        
        
    
