import pygame,anim,random,score,bullets,tools,json,bosses
from audio import play_sound as ps
from emblems import Emblem as Em
from math import sin,cos,atan2,degrees
from anim import AutoImage as AImg
from player import Player
from bullets import Coin,Confetti,HurtBullet,WarningSign,Laser
# from tools import world_log as wl
import gameplay_log as log



""" JUST A LITTLE TYPE-UP OF LOOKING AT THIS. AS OF 2024/12/08
I do NOT LIKE the way I did this.
Why is there a dictionary for everything???
There's no need for this, this is bad code!!!
ESPECIALLY info, they should just be NORMAL VARIABLES.
I NEED to fix this"""

class Template(pygame.sprite.Sprite):
    #default image if unchanged
    image = pygame.Surface((30, 30), pygame.SRCALPHA)
    pygame.draw.circle(image, "red", (15, 15), 15)

    def __init__(self,kwargs:dict):
        pygame.sprite.Sprite.__init__(self)
        self.idle={ #information about the idle state
            "offset":kwargs['offset'],
            "full":[(kwargs['pos'][0]+kwargs['offset'][0]),(kwargs['pos'][1]+kwargs['offset'][1])] # current position in idle
        }
        # setting basic info but it's not a crappy dictionary now
        self.health = kwargs['difficulty']//1
        self.difficulty = kwargs['difficulty']
        self.score = 100
        self.dead = False
        self.state = "enter"
        self.in_atk = False
        self.bullet_texture = kwargs['bullet_texture'] if 'bullet_texture' in kwargs.keys() else "bullet_def"
        self.maxhealth = self.health 
        self.healthbar_pos = "dynamic_bottom"

        self.timers = { #counters to use to check how long something is there for
            "exist":0,
            "in_state":0
        }
        self.states = { #states the enemy can be in at any time
            "enter":self.state_enter,
            "idle":self.state_idle,
            "attack":self.state_attack,
            "return":self.state_return,
        }
        self.atk_basic = {
            "shoot_chance":(10 - self.difficulty if self.difficulty<=9 else 1),
            "start_shoot_chance":(5 - self.difficulty if self.difficulty<4 else 1),
            "trip":kwargs['trip'],
            }
    
        # print(self.difficulty)
        
        
        #image values, including spritesheets
        self.aimg = AImg(host=self,name = kwargs['skin'] if 'skin' in kwargs.keys() else None, current_anim = 'idle')
        self.rect.center = self.idle["full"]


        #entrance
        self.entrance_points = kwargs['entrance_points'] 
        if self.entrance_points is not None:
            self.follow = tools.MovingPoints(
                self.entrance_points[0],
                self.entrance_points,
                speed=kwargs['entrance_speed'],
                final_pos=self.idle['full'],)
        else:
            self.follow = None

        #extras
        self.sprites = kwargs['sprites']
        self.player = kwargs['player']
        # self.is_demo = kwargs['is_demo']

    def update(self): #this should be run the same no matter what
        self.aimg.update()
        #updating timers
        self.timers['exist'] += 1
        self.timers['in_state'] += 1

        #updating state
        self.states[self.state]()

        #checking for utter murder
        self.check_dead()


    ##########STATE FUNCTIONS################
    def state_enter(self,start=False):
        if self.follow is None:
            self.state = 'idle'
        else:
            self.follow.update()
            self.rect.center = self.follow.pos
            if self.follow.finished:
                self.state = 'idle'
            #shooting based off the follow values
            if self.follow.trip and self.follow.cur_target in self.atk_basic["trip"]:
                if random.randint(0,5)>self.atk_basic['start_shoot_chance']:
                    self.shoot(type="point",info=(self.rect.center,self.player.rect.center))
                self.follow.trip = False
    def state_idle(self,start=False):
        if start:
            self.change_anim('idle')
        self.rect.center = self.idle["full"]
    def state_attack(self,start=False):
        self.state = 'idle'
    def state_return(self,start=False):
        if start:
            #figuring out where to go
            self.follow = tools.MovingPoint(self.rect.center,self.idle['full'],speed=15,check_finished=True)
        elif not self.follow.finished:
            #going there
            self.follow.update()
            self.rect.center=self.follow.position
        elif self.follow.finished:
            #done going there
            self.change_state('idle')
        


    #############SPECIAL###############
    def change_anim(self,animation):
        self.aimg.change_anim(anim=animation)

    def change_state(self,state):
        self.timers['in_state'] = 0 
        self.state = state
        self.states[self.state](start=True) #the start value initializes a variable that has to be started up first

    def kill(self,reason=None,play_sound = True) -> int:
        if reason == "health":
            #COIN CODE
            self.sprites[2].add(Coin(pos=self.rect.center,floor=self.player.bar[1],value=self.difficulty,player=self.player))
            #UPDATING THE KILL COUNT
            log.log_zone['kills'] += 1
            #playing a sound because
            ps("dead.mp3")
        else:
            log.log_zone['got_away'] += 1
            ...
        #KILLING THE SPRITE ANYWAYS
        pygame.sprite.Sprite.kill(self)
        self.dead = True
        return self.timers['exist']

    def check_dead(self):
        #checking for death
        self.dead = (self.health <= 0)
        if self.dead:
            self.kill(reason="health")

    def on_collide(self,
                   collide_type:int, #the collide_type refers to the sprite group numbers. 0 for universal (not used), 1 for other player elements, 2 for enemies
                   collided:pygame.sprite.Sprite,
                   ):
        #5/26/23 - Updating health shizznit if interaction with "player type" class
        # if collide_type == 1 or collide_type == 3:
        #     self.health -= 1
        #if colliding with an enemy, either hurt or bounce based on positioning
        if type(collided) == Player :
            if ((self.rect.centery) > collided.rect.bottom-collided.movement[0]): 
                #bouncing the player up
                collided.bounce()
                #making the player invincible for six frames to prevent accidental damage
                collided.invincibility_counter = 18
            else:
                collided.hurt()
            #damaging the enemy either way
            self.hurt()
        elif collide_type == 1:
            #I SAID damaging the enemy either way
            self.hurt(collided.dmg)
            collided.hurt()

    def hurt(self,damage=1):
        self.health -= damage
        self.change_anim("hurt")
        # self.sprites[0].add(Em(im='die',coord=self.rect.center,isCenter=True,animation_killonloop=True))

    def formationUpdate(self,
        new_pos:tuple #location of the formation, not including offset
        ):
        #following formation
        self.idle['full'] = [
            (new_pos[0] + self.idle["offset"][0]),
            (new_pos[1] + self.idle["offset"][1])]
        
    def shoot(self,type:str="point",spd:int=7,info:tuple=((0,0),(100,100)), shoot_if_below:bool=False):
        bullet=None
        if (shoot_if_below) or (type != 'point') or (info[0][1] < info[1][1]-50):
            bullet = HurtBullet(type=type,spd=spd,info=info,texture=self.bullet_texture)
            # self.sprites[0].add(bullet)
            self.sprites[2].add(bullet)
        return bullet








class A(Template): #swooping
    def __init__(self,**kwargs):
        kwargs['skin'] = "nope_A" # manually setting sprite info now
        Template.__init__(self,kwargs=kwargs)   
        
        #values created for when the opponent attacks you
        self.atk={
            "x":0, #x-momentum
            "y":5, #y-momentum
            "terminal":5+(self.difficulty if self.difficulty<50 else 10), #terminal x-velocity
            'turn_amt':2+(self.difficulty if self.difficulty<50 else 15), #how often the enemy will turn
            'turn_vals':[], #turns x can be on
            'turn_cur':0, #which x-turn A is on.
            "acc":0.5, #acceleration
            "direct":False, #direction going in - True = Right, False = Left
            "shoot_chance":(10 - self.difficulty if self.difficulty<9 else 2)
        }
        self.atk['acc'] = self.atk['terminal']/10 #fixed
        self.in_atk = True
        #generating first turn to see what direction is started on 
        self.atk['turn_vals'].append(random.randint(100,pygame.display.play_dimensions[0]-100))
        self.atk['direct'] = turn = self.idle['full'][0]<self.atk['turn_vals'][0]
        #adding all values to turn on
        for i in range(self.atk['turn_amt']): #i is previous index, i+i is current index.
            #as these are picking the *next* values, the direction is the direct opposite of what it should be
            if turn: 
                self.atk['turn_vals'].append(random.randint(100,self.atk['turn_vals'][i]))
            else:
                self.atk['turn_vals'].append(random.randint(self.atk['turn_vals'][i],pygame.display.play_dimensions[0]-100))
            turn = (not turn)
        del turn


    def state_attack(self,start=False):
        #resetting values to start
        if start:
            self.atk['x'] = 0
            self.atk['turn_cur'] = 0
            self.atk['direct'] = self.idle['full'][0]<self.atk['turn_vals'][0]
            #setting animation
            self.change_anim('attack')

            return
        #changing x and y by x and y velocities
        self.rect.y += self.atk['y']
        self.rect.x += self.atk['x']
        #updating x velocity by acceleration if not reached terminal velocity
        if self.atk['direct']:
            self.atk['x'] += self.atk['acc']
            if abs(self.atk['x']) > self.atk['terminal']:
                self.atk['x'] = self.atk['terminal']
        else:
            self.atk['x'] -= self.atk['acc']
            if abs(self.atk['x']) > self.atk['terminal']:
                self.atk['x'] = self.atk['terminal']*-1
        #checking to turn around to next value
        if abs(self.rect.center[0]-self.atk['turn_vals'][self.atk['turn_cur']]) < self.atk['terminal'] * 2:
            # print("FINISHED:",self.atk['turn_cur'],'OF',len(self.atk['turn_vals']),self.atk['turn_vals'][self.atk['turn_cur']])
            #updating values
            self.atk['turn_cur'] += 1
            self.atk['direct'] = not self.atk['direct']
            #looping back if reached end of turn list
            if self.atk['turn_cur'] >= len(self.atk['turn_vals']):
                self.atk['turn_cur'] = 0
                self.atk['direct'] = self.idle['full'][0]<self.atk['turn_vals'][0] 
            # shooting if needed
            if random.randint(0,self.atk['shoot_chance'])==self.atk['shoot_chance']:
                self.shoot(type="point",info=(self.rect.center,self.player.rect.center))
            
        #resetting when hitting bottom
        if self.rect.top>pygame.display.play_dimensions[1]:
            self.change_state('return')
            return
            
    def state_return(self,start=False):
        if start:
            self.rect.center=(pygame.display.play_dimensions[0]/2,self.rect.height*-1)
            self.follow = tools.MovingPoint(self.rect.center,self.idle['full'],speed=5,check_finished=True)
            return
        
        self.follow.update()
        self.rect.center = self.follow.position

        #calling to update follow's values every 5 or so frames in order to prevent constant unneeded running
        if self.timers['exist'] % 10 == 0:
            self.follow.change_all(self.idle['full'])
        #finishing
        if self.follow.finished:
            self.change_state('idle')

        #ERROR CHECKING - fixing return state
        if self.timers['in_state'] > 120:
            self.change_state('return')
        



            

class B(Template): #jumpy
    def __init__(self,**kwargs):
        kwargs['skin'] = "nope_B" # manually setting sprite info now
        Template.__init__(self,kwargs=kwargs) 

        self.in_atk = True

        self.atk = {
            "speed":10+((self.difficulty) if (self.difficulty<5) else (5+self.difficulty//10) if (self.difficulty<50) else 20 ) , #where the opponent goes 
            "points":[(random.randint(25,pygame.display.play_dimensions[0]-25),random.randint(25,pygame.display.play_dimensions[1]-50)) for i in range(5+(self.difficulty if self.difficulty<5 else 5))], #where the opponent moves to
            "index":0, #which point the opponent is going to first
            "shoot_chance":(10 - self.difficulty if self.difficulty<6 else 3), #chance of a shot coming out during attack
            "warnings":[] #warning symbols spawned 
        }
        #NOTE - while I would preload the warnings, for some reason that created a bug where they just wouldn't delete. It's not too bad, though. It's just a sprite.
        for point in self.atk['points']:
            warning=WarningSign(point)
            self.atk['warnings'].append(warning)

    def state_attack(self,start=False):

        if start:

            #creating the moving point index, and starting the animations
            self.atk['index'] = 0 
            self.follow = tools.MovingPoint(self.rect.center,self.atk['points'][self.atk['index']],speed=self.atk['speed'],check_finished=True,ignore_speed=True)
            self.change_anim('attack')
            #if the warnings already existed, killing them all
            for warning in self.atk['warnings']:warning.kill()
            #creating the warning signs and adding them to le sprite groups
            if not self.dead:
                self.update_warnings()
            
            return
        #updating position
        self.follow.update()
        self.rect.center=self.follow.position
        #updating follow speed
        self.follow.speed = round(self.follow.speed*0.96,2) if self.follow.speed > 2 else 2
        #updating movement patterns
        if self.follow.finished:
            #deleting the warning for the current position
            if len(self.atk['warnings']) > self.atk['index']:
                self.atk['warnings'][self.atk['index']].kill()
            #updating current index, and adding the next warning to the screen
            self.atk['index'] += 1
            #updating warnings
            self.update_warnings()
            #finishing movement
            if self.atk['index'] >= len(self.atk['points']):
                self.follow=None
                self.atk['index'] = 0
                self.change_state('return')
                
            #updating if not finished
            else: 
                self.follow = tools.MovingPoint(self.rect.center,self.atk['points'][self.atk['index']],speed=self.atk['speed'],check_finished=True,ignore_speed=True)
            # shooting if needed
            if random.randint(0,self.atk['shoot_chance'])==self.atk['shoot_chance']:
                self.shoot(type="point",info=(self.rect.center,self.player.rect.center))



    def state_return(self,start=False):
        if start:
            self.follow = tools.MovingPoint(self.rect.center,self.idle['full'],speed=10,check_finished=True)
            #deleting all the warnings
            for warning in self.atk['warnings']:
                warning.kill()
            return
        #updating movement
        self.follow.update()
        self.rect.center = self.follow.position
        #changing movement every once in a while
        if self.timers['exist']%5==0:
            self.follow.change_all(self.idle['full'])
        #finishing
        if self.follow.finished:
            self.change_state('idle')
        #error checking
        if self.timers['in_state'] >= 120:
            self.change_state('return')     

    def kill(self,reason=None):
        for warning in self.atk['warnings']:
            warning.kill()
        del self.atk['warnings'][:]
        
        Template.kill(self,reason=reason)
        

    #B-SPECIFIC CODE. This will add the next 3 spots as warnings, and make the nearest ones more intensely flash
    def update_warnings(self):
        #adds the current and next 2 warnings to the sprite groups
        for i in range(self.difficulty//3):
            #checking for out of range, and also in range of player
            if self.atk['index']+i < len(self.atk['warnings']) and abs(self.atk['warnings'][self.atk['index'] + i].rect.centery-self.player.rect.centery)<150 :
                warning = self.atk['warnings'][self.atk['index'] + i]
                self.sprites[0].add(warning)
                # self.sprites[4].add(warning)
        #makes the current warning flash aggressively, and the next warning flash faster
        if self.atk['index'] < len(self.atk['warnings']):
            self.atk['warnings'][self.atk['index']].update_intensity(60)

        if self.atk['index']+1 < len(self.atk['warnings']):
            self.atk['warnings'][self.atk['index']+1].update_intensity(15)
            








class C(Template): #turret
    def __init__(self,**kwargs):
        kwargs['skin'] = "nope_C" # manually setting sprite info now
        Template.__init__(self,kwargs=kwargs) 
        self.timer = (480 - (10*self.difficulty)) if (self.difficulty<40) else 80
        self.time = random.randint(0,self.timer//10)
    def state_idle(self,start=False):
        Template.state_idle(self)
        self.time += 1
        if self.time >= self.timer:
            self.change_state('attack')
            self.time = 0
    def state_attack(self,start=False):
        if start:
            self.change_anim("attack") 
            self.shoot(type="point",info=(self.rect.center,self.player.rect.center))
        else:    
            self.change_state('idle')






class D(Template): #special -- uses special value to inherit from that character instead 
    # NOTE THAT THIS WON'T BE NEEDED ANYMORE! ENEMIES AREN'T LIMITED TO ONLY 4 CLASSES BECAUSE THAT WAS A STUPID IDEA!!
    def __init__(self,**kwargs):
        #placeholder value

        Template.__init__(self,kwargs=kwargs)









class Compootr(Template): #special world 3 item
    #Limits for how many can be attacking at once
    atk_count = 0
    atk_max = 2
    def __init__(self,**kwargs):
        kwargs['skin'] = "hack_D" # manually setting sprite info now
        kwargs['bullet_texture'] = "bullet_hack" # manually setting sprite info now
        Template.__init__(self,kwargs=kwargs) 
        self.in_atk = True
        self.atk = {
           "shots":10+(self.difficulty*2 if self.difficulty < 10 else 20),
           "cur_shot":0,
           "return":False,
        }
        
    def update(self):
        Template.update(self)


    def state_attack(self,start:bool=False):
        if start and not self.dead:
            Compootr.atk_count += 1
            if Compootr.atk_count > Compootr.atk_max:
                self.atk['return'] = True
            else:
                self.atk['return'] = False
        elif self.atk['return']:
            Compootr.atk_count = Compootr.atk_count - 1 if Compootr.atk_count > 0 else 0 
            self.change_state('idle')
        else:
            if self.timers["in_state"] < 15:
                #start
                self.rect.y += 10
            elif self.timers["in_state"] > 15 and self.atk['cur_shot'] <= self.atk['shots']:
                #shooting
                self.shoot(type="angle",info=(self.rect.center,30*self.atk['cur_shot']))
                self.atk['cur_shot'] += 1
            else:
                #exit code
                self.rect.y -= 15
                if abs(self.rect.centery - self.idle['full'][1]) < 15:
                    self.atk['cur_shot'] = 0
                    #returning to idle
                    self.atk['return'] = True
                    return
    #special kill code due to the attack limit
    def kill(self,reason=None) -> int:
        Template.kill(self,reason=reason)
        if self.state == 'attack':
            Compootr.atk_count = Compootr.atk_count - 1 if Compootr.atk_count > 0 else 0 


            
        
        


class Jelle(Template): #special jellyfish
    #Limits for attacking
    atk_count = 0
    atk_max = 2
    def __init__(self,**kwargs):
        kwargs['skin'] = "aqua_D" # manually setting sprite info now
        Template.__init__(self,kwargs=kwargs) 
        self.atk_move = None
        self.in_atk=True
        self.atk = {'return':False,'y':0,'trip':False}
    def update(self):
        Template.update(self)
        #keeping the sprite mask locked so it doesn't bounce and accidentally kill the player
        self.mask = self.aimg.spritesheet.all_loaded_spritesheets[self.aimg.spritesheet.name][2][0]

    def state_idle(self,start=False):
        self.rect.center = self.idle['full']

    def state_attack(self,start=False):
        #moving down until instructed to go back up, then returning
        if start:
            self.atk['y'] = 1
            self.atk['trip'] = False
        #going down
        elif not self.atk['trip']:
            self.rect.y += self.atk['y'] 
            self.atk['y'] = self.atk['y'] + 0.25 if self.atk['y'] < 7 else 7
            if self.rect.centery > self.player.rect.centery:
                self.atk['trip'] = True
        #returning
        elif self.atk['trip']:
            self.rect.y += self.atk['y']
            self.atk['y'] -= 0.4
            if self.rect.centery < self.idle['full'][1]:
                self.change_state('idle')

        

    def on_collide(self,
                   collide_type:int, #the collide_type refers to the sprite group numbers. 0 for universal (not used), 1 for other player elements, 2 for enemies
                   collided:pygame.sprite.Sprite,
                   ):
        #if colliding with an enemy, either hurt or bounce based on positioning
        if type(collided) == Player :
            if ((self.rect.centery) > collided.rect.bottom-2*(collided.movement[0])): 
                #bouncing the player up
                collided.bounce()
                #this enemy only takes damage when jumped on!
                self.hurt()
                #making the player invincible for six frames to prevent accidental damage
                collided.invincibility_counter += 6
            elif collided.invincibility_counter < 1 : #(the player cannot be invincible)
                collided.hurt()
                #cutesy animation
                self.change_anim("attack")
        elif collide_type == 1:
            collided.hurt()
            self.change_anim("attack")





class Sammich(Template):
    def __init__(self,**kwargs):
        kwargs['skin'] = "home_D" # manually setting sprite info now
        Template.__init__(self,kwargs=kwargs) 
        self.in_atk = True
        self.atk = {
            'side':0,
            0:pygame.display.play_dimensions[0]*0.01, #left position
            1:pygame.display.play_dimensions[0]*0.99, #right position
            'momentum':0,
            'warning':WarningSign((0,0)),
        }
    def state_attack(self,start=False):
        #homes in on you from the sides, and then lunges at you
        if start and not self.dead:
            self.atk['side'] = random.randint(0,1) #selecting whether COMING FROM the right or left
            self.sprites[0].add(self.atk['warning'])
            # self.sprites[4].add(self.atk['warning'])
            self.atk['warning'].update_pos(self.player.rect.center)
        #homing in
        elif self.timers['in_state'] < 90:
            self.rect.centery = self.player.rect.centery - 10
            self.rect.centerx = self.atk[self.atk['side']]
            self.atk['warning'].update_pos(self.player.rect.center)
        #stopping movement to show you where it's about to aim
        elif self.timers['in_state'] < 120:
            self.rect.center = self.rect.center
        #lunging at player
        elif self.timers['in_state'] < 150:
            self.atk['warning'].kill()
            self.rect.x = self.rect.x - self.atk['momentum'] if self.atk['side'] == 1 else self.rect.x + self.atk['momentum'] if self.atk['side'] == 0 else self.rect.x
            self.atk['momentum'] += 2
        else:
            self.change_state('idle')
            self.atk['momentum'] = 0 

        
    def state_return(self,start=False):
        ...

    def kill(self,reason=None):
        self.atk['warning'].kill()
        Template.kill(self,reason)





class Chaser(Template):
    def __init__(self,**kwargs):
        kwargs['skin'] = "happy_B" # manually setting sprite info now
        Template.__init__(self,kwargs=kwargs) 
        
        self.atk = {}
        self.in_atk = True
        self.atk = {
            'vert':0,
            'horiz':0,
            'REVERSEvert':False,
            'REVERSEhoriz':False,
            'speed':0,
            'angle':0,
            'pos':list(self.rect.center),
            'warning':WarningSign((0,0)),}
    def state_attack(self,start=False):
        if start:
            self.atk['vert'] = 0
            self.atk['horiz'] = 0
            self.atk['REVERSEhoriz'] = False
            self.atk['REVERSEvert'] = False
            self.atk['speed'] = 0 
            self.atk['angle'] = 0
            self.atk['pos'] = list(self.rect.center)
            if not self.dead:
                self.sprites[0].add(self.atk['warning'])
                # self.sprites[4].add(self.atk['warning'])
                self.atk['warning'].update_pos(self.player.rect.center)
        elif self.timers['in_state'] < 120:
            self.atk['angle'] = atan2(self.player.rect.centery-self.rect.centery,self.player.rect.centerx-self.rect.centerx)
            self.image = pygame.transform.rotate(self.image,degrees(self.atk['angle']))
            self.atk['warning'].update_pos(self.player.rect.center)

        elif self.timers['in_state'] < 180:
            #finally deciding where to go, but locking on for a second
            self.atk['speed'] = 25
            self.atk['angle'] = self.atk['angle']
            self.atk['horiz'] = cos(self.atk['angle'])
            self.atk['vert'] = sin(self.atk['angle'])
            self.image = pygame.transform.rotate(self.image,degrees(self.atk['angle']))
            self.atk['warning'].update_intensity(30)

        elif self.timers['in_state'] == 180:
            self.atk['warning'].kill()

        elif self.atk['speed'] > 0:
            #moving, with extra code on for bouncing n shit
            self.atk['pos'][0] += self.atk['horiz'] * self.atk['speed'] * (-1 if self.atk['REVERSEhoriz'] else 1)
            self.atk['pos'][1] += self.atk['vert'] * self.atk['speed'] * (-1 if self.atk['REVERSEvert'] else 1)
            self.rect.center = self.atk['pos']
            self.atk['speed'] -= 0.1
            #bounce collision
            #if too far left
            if self.rect.left < 0:
                if self.atk['horiz'] < 0: #if its going left and goes left by default
                    self.atk['REVERSEhoriz'] = True
                elif self.atk['horiz'] > 0: #if its going left and goes right by default
                    self.atk['REVERSEhoriz'] = False
            #if too far right
            elif self.rect.right > 600:
                if self.atk['horiz'] < 0: #if its going right and goes left by default
                    self.atk['REVERSEhoriz'] = False
                elif self.atk['horiz'] > 0: #if its going right and goes right by default
                    self.atk['REVERSEhoriz'] = True
            #if too far up
            if self.rect.top < 0:
                if self.atk['vert'] < 0: #if its going up and goes up by default
                    self.atk['REVERSEvert'] = True
                elif self.atk['vert'] > 0: #if its going up and goes down by default
                    self.atk['REVERSEvert'] = False
            #if too far down
            elif self.rect.bottom > 800:
                if self.atk['vert'] < 0: #if its going down and goes up by default
                    self.atk['REVERSEvert'] = False
                elif self.atk['vert'] > 0: #if its going down and goes down by default
                    self.atk['REVERSEvert'] = True

        
        else:
            self.change_state('return')

    def kill(self,reason=None):
        Template.kill(self,reason)
        self.atk['warning'].kill()
        





class Yippee(Template):
    #a stupid little enemy that shits confetti at you
    def __init__(self,**kwargs):
        kwargs['skin'] = "happy_D" # manually setting sprite info now
        Template.__init__(self,kwargs=kwargs) 

        self.in_atk = True
        self.atk = {
            "points":[0,1,2],
            "initial_follow":None,
            "initial_x":0,
        }
    def state_attack(self,start=False):
        #selecting initial information
        if start:
            self.atk['points'] = [random.randint(100,400) for i in range((self.difficulty // 2) if self.difficulty<20 else 10)]
            self.atk['initial_follow'] = tools.MovingPoint(self.rect.center,(self.rect.centerx,50),check_finished=True,speed=10)
            self.atk['initial_x'] = random.randint(0,75)
            self.atk['y'] = self.idle['full'][1] + 100
        #going up to the top position
        elif self.timers['in_state'] < 30 and not self.atk['initial_follow'].finished:
            self.atk['initial_follow'].update()
            self.rect.center = self.atk['initial_follow'].position
        #floating around and confetti-ing
        elif len(self.atk['points']) > 0:
            self.rect.center = (  300 + sin(self.timers['in_state']/25 + self.atk['initial_x'])*250  , self.atk['y']  + sin(self.timers['in_state']/10)*10  )
            if abs(self.rect.centerx - self.atk['points'][0]) < 10:
                #confetti time
                for i in range(5):
                    confetti = Confetti(pos=self.rect.center)
                    # self.sprites[0].add(confetti)
                    self.sprites[2].add(confetti)
                self.atk['points'].pop(0)
                #animation
                self.change_anim('attack')
        else:
            self.change_state('return')

    def kill(self,reason=None):
        Template.kill(self,reason=reason,play_sound = False)
        



class Lumen(Template):
    #points at you, and shoots a laser 
    def __init__(self,**kwargs):
        kwargs['skin'] = "vapor_D" # manually setting sprite info now
        Template.__init__(self,kwargs=kwargs) 
        
        self.in_atk = True
        self.atk = {
            'angle':0,
            'laser':None,
            'warning':None,
        }
        
    def state_attack(self,start=False):
        if start and not self.dead:
            if self.atk['warning'] is not None:
                self.atk['warning'].kill()
                del self.atk['warning']
            self.atk['warning'] = WarningSign(self.player.rect.center)
            self.sprites[0].add(self.atk['warning'])
            # self.sprites[4].add(self.atk['warning'])
        elif self.timers['in_state'] < 120:
            #locking on, moving based on where you are
            self.atk['angle'] = atan2(self.player.rect.centery-self.rect.centery,self.player.rect.centerx-self.rect.centerx)
            self.image = pygame.transform.rotate(self.image,degrees(self.atk['angle']))
            if self.atk['warning'] is not None: self.atk['warning'].update_pos(self.player.rect.center)
        elif self.timers['in_state'] < 180:
            #waiting for a second to make it fair
            self.image = pygame.transform.rotate(self.image,degrees(self.atk['angle'])) 
        elif self.timers['in_state'] == 180:
            laser = Laser(start_pos = self.rect.center,angle=degrees(self.atk['angle'])) #shooting the laser
            # self.sprites[0].add(laser)
            self.sprites[2].add(laser)
        else:
            if self.atk['warning'] is not None: self.atk['warning'].kill()
            self.change_state('idle')
        #no matter what, maintaining positioning
        self.rect.center = self.idle['full']
    
    def kill(self,reason=None):
        if type(self.atk['warning']) == WarningSign: self.atk['warning'].kill()
        Template.kill(self,reason=reason)
        



##SAVING ASSETS IN A DICTIONARY TO BE USED LATER
loaded = {
    "A":A,
    "B":B,
    "C":C,
    "D":D,
    'jelle':Jelle,
    'compootr':Compootr,
    'sammich':Sammich,
    'nope':Chaser, #kept to prevent game from crashing
    'chaser':Chaser,
    'yippee':Yippee,
    'lumen':Lumen,
    }

# telling bullets what the enemy template is
bullets.DefaultBullet.enemy_parent_class = Template













def draw_healthbars(group:pygame.sprite.Group,drawto:pygame.Surface):
    width:int=30
    height:int=10
    min_health:int=2
    empty_color:str="#000000"
    full_color="#FF0000"
    
    for sprite in group:
        # setting health type
        if Template in sprite.__class__.__bases__:
            health = sprite.health
            maxhealth = sprite.maxhealth
        elif type(sprite) == bosses.Boss:
            health = sprite.health
            maxhealth = sprite.maxhealth
            width = 300
            height = 15
        else:
            health = 0
            maxhealth = 1
        # if there's less than 2 health, no healthbar is drawn
        if maxhealth < min_health:
            continue
        # making rect and surface
        rect = pygame.Rect(0,0,width,height)
        surface = pygame.Surface((width,height)).convert_alpha()
        surface.set_alpha(192)
        # positioning healthbar
        match sprite.healthbar_pos:
            case 'dynamic_bottom':
                rect.top = sprite.rect.bottom
                rect.centerx = sprite.rect.centerx
            case _:
                rect.center = sprite.healthbar_pos
        # filling the empty color
        surface.fill(empty_color)
        # figuring the width based off the percent
        percent = health/maxhealth
        fullwidth = round(width * percent,0)
        # making a new rect
        fullrect = pygame.Rect(0,0,fullwidth,height)
        surface.fill(full_color,fullrect)

        # drawing
        drawto.blit(surface,rect)

        










class BasicEventItem(Em):
    def __init__(self,im=None,coord=(0,0),isCenter=False,pattern:str="sine"):
        Em.__init__(self,im,coord,isCenter,pattern=pattern)
        self.touched = False
    def on_collide(self,collide_type,collided):
        if collide_type == 1:
            self.touched = True

########OLD
