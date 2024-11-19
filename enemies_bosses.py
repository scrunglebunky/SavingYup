import pygame,random,score
from player import Player
from anim import all_loaded_images as img
from anim import AutoImage as AImg
from emblems import Emblem as Em
from math import sin,atan2,degrees,radians
from bullets import * 
from enemies import Template,HurtBullet,Warning,Confetti,Coin
from tools import MovingPoint
from anim import WhiteFlash
from audio import play_sound as ps
winrect = pygame.display.play_rect

#a boss contains a collection of autoimages and hitboxes in order to check for very specific collision
class Boss():
    #the boss behaves like a puppet master to a bunch of different boss "attributes". it may be as simple as a small png, or as complex as a series of limbs and a head with jaws
    def __init__(self,kwargs:dict):
        self.sprites = kwargs['sprites']
        self.attributes = {
            #a collection of other sprites to be added to the boss: the main body, arms, head maybe?
        }
        self.info = {
            #a series of information pieces on the boss. 
            'health':10,
            "state":"enter",
            'ENDBOSSEVENT':False, #a check to see if the boss state should end
            "phase":0, #this can be a variety of factors but is usually handled specifically by the inheritors of this class, as the amount of phases varies based off boss
            'invincible':False, #a global check for invincibility. each individual asset also has invincibility. 
            'ENDWORLD' : False,
            "LAYERPLAYERINFRONT":False, #draws the player a second time if checked, in front of everything else
        }
        self.atk_info = {
            "when":120, #after how many frames in idle should I attack? 
            'type':0, #what type of attack is being went with
            'types':0, #how many types of attacks there are (0 just means 1 here don't worry)
        }
        self.timers = {
            "total":0,
            "in_state":0,
        }
        self.states = {
            "enter":self.state_enter,
            "idle":self.state_idle,
            "attack":self.state_attack,
            "return":self.state_return,
            "die":self.state_die,
        }

        #various unorganized values
        self.bullets = [] # an unorganized list of bullets, will not be removed when dead, has to be manually removed
        self.bullets_del_list = []
        self.player = kwargs['player']
        self.window = kwargs['window']
        self.boss_state = kwargs['state'] #this is so certain values can be modified                                        
    
    def update(self):
        #timer update
        self.timers['total'] += 1
        self.timers['in_state'] += 1
        #state and health update
        self.states[self.info['state']]()
        if self.info['health'] <= 0 and self.info['state'] != "die":
            self.change_state("die")
        #removing dead bullets
        if self.timers['total'] % 60 == 0:
            self.remove_dead_bullets()
        

    def collision_master(self,collider,collide_type,collided):
        #first value -> attribute that found collision #second value -> type of sprite the attribute collided with #third value -> the actual item
        ...
    def addAttribute(self,name:str,attribute):
        self.attributes[name] = attribute
        self.sprites[2].add(attribute)

    #STATE DEFINITIONS
    #Just like how any enemy will work
    def state_enter(self,start:bool=False):...
    def state_start(self,start:bool=False):...
    def state_idle(self,start:bool=False):...
    def state_attack(self,start:bool=False):...
    def state_return(self,start:bool=False):...
    def state_die(self,start:bool=False):
        #default kill code, to tell the program that the boss is dead
        self.info['ENDBOSSEVENT'] = True
        for attribute in self.attributes.values():
            attribute.kill()
        
    #changing what state is being done
    def change_state(self,state:str):
        self.info['state'] = state
        self.timers['in_state'] = 0 
        self.states[self.info['state']](start=True)
    def hurt(self,amount=1):
        self.info['health'] -= amount

    #removing dead bullets
    def remove_dead_bullets(self):
        #thank you stackoverflow 
        del self.bullets_del_list[:]
        for i in range(len(self.bullets)):
            if self.bullets[i].dead:
                self.bullets_del_list.append(i)
        for i in sorted(self.bullets_del_list,reverse=True):
            del self.bullets[i]

    def shoot(self, type: str="point", spd: int=7, info: tuple=((0,0),(100,100)), shoot_if_below: bool=True, texture:str=None):
        bullet=None
        if (shoot_if_below) or (type != 'point') or (info[0][1] < info[1][1]-50):
            bullet = HurtBullet(type=type,spd=spd,info=info,texture=texture)
            self.sprites[2].add(bullet)
            self.host.bullets.append(bullet)
        return bullet



#a piece of a boss. think of the boss as some sort of hand controlling a bunch of puppets.
class BossAttribute(pygame.sprite.Sprite):
    def __init__(self,host:Boss, sprites:dict, name:str="placeholder", image:str = "placeholder.bmp", pos:tuple = (100,100)):
        #basic initialization
        pygame.sprite.Sprite.__init__(self)
        self.sprites=sprites
        
        #image info
        self.aimg = AImg(host=self,name=image)

        #positioning info
        self.rect.center = pos

        #naming info
        self.host = host
        self.name = name

        #health information
        self.health = 0 
        self.healthAffectGlobal = True
        self.healthProtected = False
    def on_collide(self,collide_type:int,collided:pygame.sprite.Sprite):
        self.host.collision_master(self,collide_type,collided)
    def update(self):
        #graphic update
        self.aimg.update()
    def shoot(self, type: str="point", spd: int=7, info: tuple=((0,0),(100,100)), shoot_if_below: bool=True, texture:str=None):
        bullet=None
        if (shoot_if_below) or (type != 'point') or (info[0][1] < info[1][1]-50):
            bullet = HurtBullet(type=type,spd=spd,info=info,texture=texture)
            self.sprites[2].add(bullet)
            self.host.bullets.append(bullet)
        return bullet

        



#UFO
class UFO(Boss):
    def __init__(self,**kwargs):
        Boss.__init__(self,kwargs=kwargs)

        self.info['health'] = 50

        #setting attack info
        self.atk_info['when'] = random.randint(60,360)
        self.atk_info['pinch'] = False #if the boss is angry
        self.atk_info['types'] = 2 #chad spam, succ, chad kaboom
        #atk1 info
        self.atk_info['1_angle'] = 0 #during the first bullet spam, what angle is done
        #atk2 info
        self.atk_info['2_direction'] = 'l' #is the enemy coming from the left or the right during succ?
        self.atk_info['2_x'] = 0 #x velocity
        self.atk_info['2_y'] = 0 #when the enemy is getting lifted off the ground. 
        self.atk_info['2_state'] = 0 # 0: moving off to one side (l or r) ; 1: slowly speeding to the other side ; 2 - slowing back down and raising back to the 
        self.atk_info['2_swingpoint'] = 0 # 0: moving off to one side (l or r) ; 1: slowly speeding to the other side ; 2 - slowing back down and raising back to the 
        #atk3 info
        self.atk_info['3_move'] = None #tools.MovingPoint to a random position
        self.atk_info['3_bullets'] = [ ] #where all the bullets are stored
        self.atk_info['3_counter'] = 4 #how many points the boss moves to, based on health
        self.atk_info['3_count'] = 0 #what point the boss is currently at
        self.atk_info['3_wait'] = 0 #when the boss waits before moving again
        self.atk_info['3_spd'] = 15 #how fast the boss moves

        #creating
        self.addAttribute(name='body',attribute=BossAttribute(host=self,sprites=self.sprites,image="boss_ufo",name='body',pos=(300,100)))
        self.addAttribute(name='succ',attribute=BossAttribute(host=self,sprites=self.sprites,image="boss_ufo_succ",name='succ'))
        #hiding attributes
        self.attributes['succ'].rect.center = (-1000,-1000)

        #the enemy will begin the enter state now
        self.change_state('enter')

    #generally updating everything, including animations
    def update(self):
        Boss.update(self)
        # for attribute in self.attributes.values():
        #     attribute.update()

    
    #managing collision
    def collision_master(self,collider,collide_type,collided):
        if collider.name == 'body':
            if type(collided) == Player:
                if ((collider.rect.centery) > collided.rect.bottom-collided.movement[0]):
                    #bouncing the player up
                    collided.bounce()
                    #making the player invincible for six frames to prevent accidental damage
                    collided.invincibility_counter = 18
                    #taking damage
                    if self.info['state'] != 'die': self.hurt()
                #killing bullet
                collided.hurt()
            elif collide_type == 1:
                collided.hurt()
                if self.info['state'] != 'die': self.hurt()
        elif collider.name == 'succ':
            if type(collided) == Player:
                collided.movement[0] = -3



    #the whole swaying movement
    def idle_move(self) -> None:
        self.attributes['body'].rect.center = (
                300 + 200*sin(self.timers['in_state']/20),
                200 + 50*sin(self.timers['in_state']/10)
            )



    #idle state, moving from side to side
    def state_idle(self,start:bool=False):
        #figuring out when to attack
        if start:
            self.atk_info['when'] = random.randint(60,300)
        #attacking when time is met
        elif self.timers['in_state'] % self.atk_info['when'] == 0:
            self.change_state('attack')
        #movement
        self.idle_move()


        
    #enter state teehee
    def state_enter(self,start:bool=False):
        if start:
            self.attributes['body'].rect.centerx = winrect.centerx
            self.attributes['body'].rect.centery = -200
        #slowly lowering down to the screen
        elif abs(self.attributes['body'].rect.centery-200) > 25:
            self.attributes['body'].rect.centery = (self.timers['in_state']*3 + 10*sin(self.timers['in_state']/7)) - 200
        #bobbing up and down until enter state finished
        elif self.timers['in_state'] < 360:
            self.attributes['body'].rect.centery = 200 + 10*sin(self.timers['in_state']/10)
        #exit state
        else:
            self.change_state('idle')



    #attack state
    def state_attack(self,start:bool=False):
        #selecting what attack to do
        if start:
            self.atk_info['type'] = random.randint(0,self.atk_info['types'])
            #changing animation
            self.attributes['body'].aimg.change_anim('chad' if (self.atk_info['type'] == 0 or self.atk_info['type'] == 2) else "succ" if self.atk_info['type'] == 1 else 'idle')
            #startup info per attack
            if self.atk_info['type'] == 1:
                self.atk_info['2_direction'] = random.choice(('l','r'))
                # self.atk_info['2_direction'] = 'r' #REMOVE THIS
        
        
        #spinning shoot
        elif self.atk_info['type'] == 0:
            #movement
            self.idle_move()
            #changing angle
            self.atk_info['1_angle'] += 15
            self.attributes['body'].shoot("angle",7,info=(self.attributes['body'].rect.center,self.atk_info['1_angle']))
            #returning (changing animation)
            if self.timers['in_state'] >= 180:
                self.atk_info['type'] = 'leave' #just so code ain't repeated, it moves to the final end statement
        
        #static shoot
        elif self.atk_info['type'] == 2:
            #adding a new spot to move to, if either the first time or
            if (type(self.atk_info['3_move']) != tools.MovingPoint) or (self.atk_info['3_spd'] == 0 and self.atk_info['3_wait'] >= 1):
                self.atk_info['3_move'] = tools.MovingPoint(pointA=self.attributes['body'].rect.center,pointB=(random.randint(0,600),random.randint(0,600)),speed=15,ignore_speed=True,check_finished=False)
                self.atk_info['3_spd'] = self.atk_info['3_move'].speed #how fast the boss moves
                self.atk_info['3_wait'] = 0 #resetting wait itmer
                self.atk_info['3_count'] += 1 #updating counter
                #checking to exit
                if self.atk_info['3_count'] > self.atk_info['3_counter']:
                    self.atk_info['type'] = 'leave' 
                    self.atk_info['3_count'] = 0
            #waiting 
            elif self.atk_info['3_spd'] == 0:
                self.atk_info['3_wait'] += 1
                #doing a shoot spam based on movement
                for i in range(30):
                    self.attributes['body'].shoot(type="angle",spd=7,info=(self.attributes['body'].rect.center,i*15))
            #moving
            else:
                #updating speed
                self.atk_info['3_spd'] = round(self.atk_info['3_spd']*0.925,3) if self.atk_info['3_spd'] > 0.25 else 0
                self.atk_info['3_move'].speed = self.atk_info['3_spd'] 
                #updating movement values
                self.atk_info['3_move'].update()
                self.attributes['body'].rect.center = self.atk_info['3_move'].position




        #succin ya up
        elif self.atk_info['type'] == 1:

            #moving off to the left
            if self.atk_info['2_state'] == 0:
                self.attributes['body'].rect.x += (5 if self.atk_info['2_direction'] == 'r' else -5)
                if self.attributes['body'].rect.right < 0 or self.attributes['body'].rect.left > pygame.display.play_dimensions[0]:
                    #preparing the swing to the left
                    self.atk_info['2_state'] = 1
                    #telling the boss when to swing upwards
                    self.atk_info['2_swingpoint'] = pygame.display.play_dimensions[0]-200 if self.atk_info['2_direction'] == 'l' else 200
                    self.atk_info['2_x'] = 0
                    self.atk_info['2_y'] = -3
                    self.attributes['body'].rect.centery = pygame.display.play_dimensions[1] - 200


            #speeding to the sides
            elif self.atk_info['2_state'] == 1:

                #NOTE - l means it COMES FROM the left, and moves to the right, vice versa with r
                if self.atk_info['2_x'] < 15 and self.atk_info['2_x'] > -15: 
                    self.atk_info['2_x'] += 0.1 if self.atk_info['2_direction'] == 'l' else -0.1
                self.attributes['body'].rect.x += self.atk_info['2_x']

                #swinging upwards up and away wahoo
                if abs(self.attributes['body'].rect.centerx - self.atk_info['2_swingpoint']) < 30:
                    self.atk_info['2_state'] = 2

                #positioning the succinator
                self.attributes['succ'].rect.center = self.attributes['body'].rect.center


            #swinging back up
            elif self.atk_info['2_state'] == 2:
                # print("---------------------SWING BACK")
                #updating velocities
                self.atk_info['2_x'] -= (1.5 if self.atk_info['2_direction'] == 'l' else -1.5)
                self.atk_info['2_y'] += 2
                #moving
                self.attributes['body'].rect.x += self.atk_info['2_x']
                self.attributes['body'].rect.y -= self.atk_info['2_y']
                #checking to finish
                if self.attributes['body'].rect.centery < 300:
                    self.atk_info['type'] = 'finish'
                    self.atk_info['2_x'] = self.atk_info['2_y'] = self.atk_info['2_state'] = self.atk_info['2_swingpoint'] = 0
                
                #succ effect disappearance
                self.attributes['succ'].rect.centerx = self.attributes['body'].rect.centerx
                self.attributes['succ'].rect.centery += self.atk_info['2_y']


                
     
            
        else:
            #changing animation and returning
            self.attributes['body'].aimg.change_anim('idle')
            self.change_state('idle')

        #spazzing out effect
        if self.atk_info['type'] == 0 or self.atk_info['type'] == 2:
            self.attributes['body'].rect.centerx += random.randint(-5,5)
            self.attributes['body'].rect.centery += random.randint(-5,5)
        

    
    #dying state
    def state_die(self,start:bool=False):
        if start:
            self.attributes['body'].aimg.change_anim('dead')

        #jittering around
        self.attributes['body'].rect.centerx += random.randint(-25,25)
        self.attributes['body'].rect.centery += random.randint(-25,25)

        #borders
        if self.attributes['body'].rect.bottom > 600:
            self.attributes['body'].rect.y -= 25

        

        
        #kaboom
        if self.timers['in_state'] % 3 == 0:
            self.sprites[0].add(Em(
                    im='kaboom',
                    coord=(random.randint(0,600),random.randint(0,500)),
                    isCenter=True,
                    animation_killonloop=True,
                    resize=(100,100)
                    ))
            self.sprites[2].add(Coin(pos=self.attributes['body'].rect.center,floor=self.player.bar[1],value=random.choice((0,5))))

            


        #ending
        if self.timers['in_state'] > 240:
            self.info['ENDBOSSEVENT'] = True



    #hurting but with a cute animation
    def hurt(self,amount=1):
        Boss.hurt(self,amount)
        if self.info['health'] % 5 == 0:
            self.attributes['body'].aimg.change_anim(
                'hurt' +  ("CHAD" if (self.info['state'] == 'attack' and (self.atk_info['type'] == 2 or self.atk_info['type'] == 0)) else "SUCC" if (self.info['state'] == 'attack' and self.atk_info['type'] == 1) else "" )
            )








#NOPE
class Nope(Boss):
    def __init__(self,**kwargs):
        Boss.__init__(self,kwargs=kwargs)
        #setting basic info
        self.info['health'] = 100
        self.info['state'] = 'intro'
        self.states['intro'] = self.state_intro
        #adding attributes
        self.addAttribute("intro",attribute=NopeIntro(host=self,sprites=self.sprites))
        self.addAttribute("body",attribute=BossAttribute(host=self,sprites=self.sprites,name="body",image="boss_nope",pos=(-1000,-1000)))
        #attack info
        self.atk_info['type'] = 0 #currently on 1 attack
        self.atk_info['types'] = 1 #2 attacks
        self.atk_info['idle_move'] = tools.MovingPoint(self.attributes['body'].rect.center,self.attributes['body'].rect.center,speed=0)
        self.atk_info['idle_spd'] = 0 
        #attack 2 lockon
        self.atk_info['2_state'] = 0 #0 is locking on, 1 is falling, 2 is collapsing, 3 is rising back up
        self.atk_info['2_x'] = 0 #where the boss is going, locking onto
        self.atk_info['2_wait'] = 0 #waiting at the bottom for a little bit before rising back to the top
        self.atk_info['2_bottom'] = pygame.display.play_dimensions[1]*0.9

        #attack 1 shoot
        #just as a description. the boss shoots a large bullet at you every x frames while also shooting in a bunch of other spots every x frames

    
    def update(self):
        Boss.update(self)
        # for attribute in self.attributes.values():
        #     attribute.update()


    def collision_master(self,collider,collide_type,collided):
        #collision for the decoy, 
        if collider.name == 'intro':
            #hurting player
            if type(collided) == Player:
                collided.hurt()
            #hurting self and bullet
            elif collide_type == 1:
                collider.hurt()
                collided.hurt()
                # if self.info['state'] != 'die': self.hurt()
        #collision for main boss
        if collider.name == 'body':
            if type(collided) == Player:
                if ((collider.rect.centery) > collided.rect.bottom-collided.movement[0]):
                    #bouncing the player up
                    collided.bounce()
                    #making the player invincible for six frames to prevent accidental damage
                    collided.invincibility_counter = 18
                    #taking damage
                    if self.info['state'] != 'die': self.hurt()
                #killing bullet
                collided.hurt()
            elif collide_type == 1:
                collided.hurt()
                self.hurt()
            

    def state_intro(self,start:bool=False):
        ...
        #using this for explanation purposes.
        #the start of the boss has a decoy attribute called 'intro' which is a placeholder nope enemy, and the boss only begins when that happens
        #so for the most part, this empty intro state plays while the decoy nope does all the coding.
        #All that is handled internally is the collision because it has to be to look nice. 
    


    def state_enter(self,start:bool=False):
        if start:
            #explosion when first entering the screen from the decoy
            self.attributes['body'].rect.center = self.attributes['intro'].rect.center
            self.sprites[0].add(Em(im='kaboom',coord=self.attributes['body'].rect.center,isCenter=True,animation_killonloop=True,resize=(350,350)))
        elif self.timers['in_state'] < 60: #change later
            #aggressive jittering
            self.attributes['body'].rect.centery = self.attributes['intro'].rect.centery + 10*sin(self.timers['in_state']/25) + random.randint(-1,1)
            if self.timers['in_state']%2==0:self.attributes['body'].rect.centerx = winrect.centerx + random.randint(-2,2)
        else:
            #changing the state to idle
            self.change_state('idle')



    def state_idle(self,start:bool=False):
        #in the idle state, moving from point to point at random
        if self.atk_info['idle_move'].speed < (0.5 if self.info['health'] > 30 else 5):
            self.atk_info['idle_move'] = tools.MovingPoint(pointA=self.attributes['body'].rect.center,pointB=(random.randint(0,600),random.randint(0,400)),ignore_speed=True,speed=10)
            #shooting
            for i in range(15): self.attributes['body'].shoot(type="angle",spd=7,info=(self.attributes['body'].rect.center,i*24))
            #changing state
            if random.randint(1,10) == 2:
                self.change_state('attack')
        else:
            #updating movement
            self.atk_info['idle_move'].update()
            self.atk_info['idle_move'].speed *= 0.95
            self.attributes['body'].rect.centerx = self.atk_info['idle_move'].position[0]
            self.attributes['body'].rect.centery = self.atk_info['idle_move'].position[1]
            #shaking amount based on health
            self.attributes['body'].rect.centerx += random.randint((-1*(151-self.info['health'])//20),((151-self.info['health'])//20))
            self.attributes['body'].rect.centery += random.randint((-1*(151-self.info['health'])//20),((151-self.info['health'])//20))



    def state_attack(self,start:bool=False):
        if start:
            #picking an attack type to undergo
            self.atk_info['type'] = random.randint(0,self.atk_info['types'])
            #resetting info for attack type 1 - lockon
            if self.atk_info['type'] == 1:
                self.atk_info['2_state'] = 0
                self.attributes['body'].rect.centery = 100
                self.attributes['body'].aimg.change_anim('scream')

            #setting info for attack type 0 - shoot
            elif self.atk_info['type'] == 0:
                self.attributes['body'].aimg.change_anim('scream')



        if self.atk_info['type'] == 0:
            #shooting attack
            if (self.timers['in_state'] % 3 == 0) or (self.info['health'] < 50):
                self.attributes['body'].shoot(type="angle",spd=5,info=(self.attributes['body'].rect.center,self.timers['in_state']*13))
            if (self.timers['in_state'] % 45 == 0) or (self.info['health']<50 and self.timers['in_state'] % 35 == 0):
                self.attributes['body'].shoot(spd=10,info=(self.attributes['body'].rect.center,self.player.rect.center))
                if self.info['health'] < 30:
                    for i in range(5):
                        self.attributes['body'].shoot(spd=random.randint(7,10),info=(self.attributes['body'].rect.center,(self.player.rect.centerx+random.randint(-25,25),self.player.rect.centery+random.randint(-25,25))))

            #jittering
            self.attributes['body'].rect.x += random.randint(-1,1); self.attributes['body'].rect.y += random.randint(-1,1)
            #ending
            if self.timers['in_state'] > 360:
                self.atk_info['type'] = 9999 #this makes the end code run, anything outside of the defined values
        


        elif self.atk_info['type'] == 1:
    
            #following attack 
            if self.atk_info['2_state'] == 0:
                #indicating player the fall
                self.attributes['body'].rect.centerx = self.player.rect.centerx
                if self.timers['in_state'] > 120:
                    self.atk_info['2_state'] = 1
            #waiting to indicate launch
            elif self.atk_info['2_state'] == 1:
                if self.timers['in_state'] > 180:
                    self.atk_info['2_state'] = 2
                    self.attributes['body'].aimg.change_anim('flydown')

            #launching
            elif self.atk_info['2_state'] == 2:
                #going to bounce state if hitting bottom
                if self.attributes['body'].rect.centery > self.atk_info['2_bottom']:
                    self.atk_info['2_state'] = 3
                    self.attributes['body'].aimg.change_anim('bounce')
                    self.atk_info['2_wait'] = 0 
                #flying down if not bounced yet
                else:
                    self.attributes['body'].rect.y += 25
            #bouncing
            elif self.atk_info['2_state'] == 3:
                self.atk_info['2_wait'] += 1
                if self.atk_info['2_wait'] > 60:
                    self.attributes['body'].rect.y -= 5
                if self.attributes['body'].rect.y < 100:
                    self.atk_info['2_state'] = 4
            else:
                self.atk_info['type'] = 9999
            
        
        
        else:
            self.attributes['body'].aimg.change_anim('idle')
            self.change_state('idle')
        
        

    def state_die(self,start:bool=False):
        if start:
            self.attributes['body'].aimg.change_anim("dead")
        
        #shaking in the center
        elif self.timers['in_state'] < 80:
            self.attributes['body'].rect.center = (300,100)
            self.attributes['body'].rect.x += random.randint(-5,5); self.attributes['body'].rect.y += random.randint(-3,3)
            if self.timers['in_state'] % 5 == 0:
                self.sprites[2].add(Coin(pos=self.attributes['body'].rect.center,floor=self.player.bar[1],value=1))


        #exploding
        elif self.timers['in_state'] == 80:
            self.sprites[0].add(Em(
                    im='kaboom',
                    coord=self.attributes['body'].rect.center,
                    isCenter=True,
                    animation_killonloop=True,
                    resize=(450,450)
                    ))
            self.attributes['body'].kill()
            for i in range(100):
                self.sprites[2].add(Coin(pos=self.attributes['body'].rect.center,floor=self.player.bar[1],value=5))


        #finishing
        elif self.timers['in_state'] > 240:
            self.info['ENDBOSSEVENT'] = True




    #taking damage, goofy animation, you know the jizz
    def hurt(self,amount=1):
        Boss.hurt(self,amount)
        if self.info['health'] % 5 == 0 and not self.info['state'] == 'attack':
            self.attributes['body'].aimg.change_anim('hurt')



#DECOY NOPE
class NopeIntro(BossAttribute):
    #The boss decoy, which is used as a cute little intro for a nope that got way too pissed. 
    def __init__(self,host,sprites):
        #setting values
        BossAttribute.__init__(self,host=host,sprites=sprites,name="intro",image="nope_D",pos=(winrect.centerx,-100))
        self.state = 'enter'
        self.health = 5
        self.enter_y_momentum = 5
        self.states = {'enter':self.state_enter,'wait':self.state_wait}



    def update(self):
        #basic update
        BossAttribute.update(self)
        try: self.states[self.state]()
        except ValueError: self.kill()
        


    def state_enter(self):
        #sliding downwards 
        self.rect.centery += self.enter_y_momentum
        self.enter_y_momentum = round(self.enter_y_momentum*0.99,3)
        if self.enter_y_momentum < 1:
            self.state='wait'

    def state_wait(self):
        #doing nothing when sliding
        ...

    def hurt(self):
        #changing the boss state to enter when killed
        self.health -= 1
        if self.health <= 0:
            self.kill()
            self.host.change_state('enter')

        
        

#CRT
class CRT(Boss):
    def __init__(self,**kwargs):
        Boss.__init__(self,kwargs)
        self.states['intro'] = self.state_intro
        self.states['switch'] = self.state_switch
        self.info['health'] = 75
        self.info['controlhealth'] = 75
        self.info['state'] = 'intro'
        #idle attack
        self.atk_info['angle'] = 0
        self.atk_info['wait'] = 360
        self.atk_info['type'] = 0 
        self.atk_info['types'] = 1
        #pinch mode
        self.info['pinch']:bool = False 
        self.info['switch_state'] = 0 
        #attack definitions are now written in the attack state



        #ADDING ATTRIBUTES
        self.addAttribute(name="ctrl",attribute=BossAttribute(host=self,sprites=self.sprites,name="ctrl",image="boss_crt_ctrl",pos=(-1000,-100)))
        self.addAttribute(name="body",attribute=BossAttribute(host=self,sprites=self.sprites,name="body",image="crt.png",pos=(-1000,-1000)))
        self.addAttribute(name="body2",attribute=BossAttribute(host=self,sprites=self.sprites,name="body2",image="crt2.png",pos=(winrect.centerx,-200)))
        self.addAttribute(name="Larm",attribute=BossAttribute(host=self,sprites=self.sprites,name="Larm",image="boss_crt_arm",pos=(-1000,-1000)))
        self.addAttribute(name="Rarm",attribute=BossAttribute(host=self,sprites=self.sprites,name="Rarm",image="boss_crt_armFLIP",pos=(-1000,-1000)))

    
    def collision_master(self,collider,collide_type,collided):
        #damaging the control panel, and changing the state if it dies
        if collider.name == 'ctrl':
            if collide_type == 1 and not self.info['pinch']:
                collided.hurt()
                self.info['controlhealth'] -= 1
                if self.info['controlhealth']%5 == 0:
                    self.attributes['ctrl'].aimg.change_anim('hurt')

                if self.info['controlhealth'] <= 0:
                    self.change_state('switch')

        if collider.name == 'body2' :
            if collide_type == 1 and self.info['pinch'] and self.info['state'] != 'die':
                collided.hurt()
                self.info['health'] -= 1
                if self.info['health']%5 == 0:
                    self.attributes['body2'].aimg.change_anim('hurt')
                if self.info['health'] <= 0:
                    self.change_state('die')

        if collider.name == 'Larm' or collider.name == 'Rarm' :
            if type(collided) == Player:
                collided.hurt()
            if collide_type == 1 and self.info['pinch']:
                collided.hurt()


    def state_intro(self):
        if self.timers['in_state'] == 10:
            self.boss_state.playstate.background.aimg.__init__(host=self.boss_state.playstate.background,name="boss_crt_bg",resize=(600,800),current_anim="0")
        # if self.timers['in_state'] % 30 == 0:
        #     self.sprites[0].add(WhiteFlash(surface=self.window))
        if self.timers['in_state'] == 180:
            self.boss_state.playstate.background.aimg.change_anim('1')
            self.sprites[0].add(WhiteFlash(surface=self.window))
        if self.timers['in_state'] == 210:
            self.boss_state.playstate.background.aimg.change_anim('2')
            self.sprites[0].add(WhiteFlash(surface=self.window,start_val=255,spd=20.0))
        if self.timers['in_state'] > 240:
            self.boss_state.playstate.background.aimg.change_anim('3')
            self.sprites[0].add(WhiteFlash(surface=self.window,spd=2.5))
            self.change_state('idle')


    def state_idle(self,start:bool=False):

        if start:
            #moving attributes to be visible
            self.attributes['ctrl'].rect.center = (winrect.centerx,25)
            self.attributes['body'].rect.center = (winrect.centerx,pygame.display.play_dimensions[1]/2)
            self.attributes['Larm'].rect.left = -10; self.attributes['Larm'].rect.centery = 300;
            self.attributes['Rarm'].rect.right = 610; self.attributes['Rarm'].rect.centery = 300;
            #changing timer
            self.atk_info['wait'] = random.randint(240,360) if not self.info['pinch'] else 120
            
        else:
            if self.timers['in_state'] % 20 == 0: 
                #switching shoot direction
                for i in range(10):
                    angle = 52.5 + 10*sin(self.timers['in_state']/30) + i*20
                    spd = 3 if not self.info['pinch'] else 4
                    self.attributes["ctrl"].shoot("angle",spd=spd,info=((10,0),angle),texture="bullet_hack")
                    self.attributes["ctrl"].shoot("angle",spd=spd,info=((winrect.right-10,0),angle-45),texture="bullet_hack")
                
            #swinging the arms back and forth for no reason
            self.attributes['Larm'].rect.centery = sin(self.timers['in_state']/15)*200 + 300
            self.attributes['Rarm'].rect.centery = sin(self.timers['in_state']/20)*200 + 300

            #starting attack
            if self.timers['in_state'] > self.atk_info['wait']:
                self.change_state('attack')

 
    def state_attack(self,start:bool=False):
        if start:
            #figuring out which attack to go with
            self.sprites[0].add(WhiteFlash(surface=self.window,start_val=128))
            self.atk_info['type'] = random.randint(0,self.atk_info['types'])
            #definitions for the first attack -> explosions
            if self.atk_info['type'] == 0:
                #attack 1: kabooms
                if '1_warnings' in self.atk_info.keys():
                    for warning in self.atk_info['1_warnings']:
                        warning.kill()
                    del self.atk_info['1_warnings'][:]
                self.atk_info['1_warnings'] = [ ] #warning.rect.center will provide as the coordinates. no need for dupe values
                self.timers['1'] = 0 #period between warnings and explosions: 120 frames currently
                self.atk_info['1_amount'] = 30 #will increase based on health
                self.atk_info['1_explosions'] = [ ] #the explosions occurring at any given time. 
                self.atk_info['1_state'] = 0 #0 is warnings, 1 is the wait, 2 is the shooting, and then it ends
                self.atk_info['1_count'] = 0 #current explosion being created


            #definition for second attack -> arms
            if self.atk_info['type'] == 1:
                #attack 2: arms - values
                if '2_Lwarn' in self.atk_info.keys():
                    self.atk_info['2_Lwarn'].kill()
                self.atk_info['2_arm']:int = 0 #0 -> L, 1 -> R
                self.atk_info['2_Lpos'] = self.atk_info['2_Rpos'] = 0 
                self.atk_info['2_Lwarn'] = Warning((-1000,-1000))
                self.timers['2'] = 0 #a timer that will reset on occasion
                #adding the warning symbols
                self.sprites[0].add(self.atk_info['2_Lwarn'])
                self.atk_info['2_Lwarn'].rect.center = self.player.rect.center

        if self.atk_info['type'] == 1:
            self.timers['2'] += 1

            if self.timers['2'] < 90:
                self.attributes["Larm"].rect.centery = self.attributes["Rarm"].rect.centery = self.player.rect.centery 
                self.atk_info['2_Lwarn'].rect.center = self.player.rect.center
            
            elif self.timers['2'] == 120:
                self.atk_info['2_Lwarn'].kill()
                self.attributes["Larm"].aimg.change_anim("atk")
                self.attributes["Rarm"].aimg.change_anim("atk")

            elif self.timers['2'] > 210:
                self.sprites[0].add(WhiteFlash(surface=self.window))
                self.change_state('idle')

        elif self.atk_info['type'] == 0:
            #select a bunch of random coordinates, place warnings respectively in order
            #when they are all placed, cause explosions in the order they were placed
            if self.atk_info['1_state'] == 0 :
                if self.timers['in_state'] % 10 == 0:
                    warn = Warning(pos=(random.randint(0,600),random.randint(0,800)))
                    self.atk_info['1_warnings'].append(warn)
                    self.sprites[0].add(warn) 
                    if len(self.atk_info['1_warnings']) > self.atk_info['1_amount']:
                        self.atk_info['1_state'] = 1    
            #starting warnings
            elif self.atk_info['1_state'] == 1 :
                self.timers['1'] += 1      
                if self.timers['1'] > 60:
                    self.atk_info['1_state'] = 2     
            #exploisons
            elif self.atk_info['1_state'] == 2 :
                if self.timers['in_state'] % 2 == 0:
                    if len(self.atk_info['1_warnings']) > 0:
                        kaboom=CRT_explosion(coord=self.atk_info['1_warnings'][0].rect.center)
                        self.sprites[2].add(kaboom)
                        self.atk_info['1_warnings'][0].kill()
                        del self.atk_info['1_warnings'][0]  
                    else:
                        self.atk_info['1_state'] = 3
            #end
            else:
                self.sprites[0].add(WhiteFlash(surface=self.window))
                self.change_state('idle')      

        #DOING THE EVIL IDLE BULLETS IF PINCH MODE
        if self.info['pinch'] and self.timers['in_state']%30==0:
            #switching shoot direction
            for i in range(10):
                angle = 52.5 + 10*sin(self.timers['in_state']/30) + i*20
                spd = 3
                self.attributes["ctrl"].shoot("angle",spd=spd,info=((10,0),angle),texture="bullet_hack")
                self.attributes["ctrl"].shoot("angle",spd=spd,info=((winrect.right-10,0),angle-45),texture="bullet_hack")
            

    def state_switch(self,start:bool=False):
        if start: 
            #kaboom up top, have the control panel fall off screen
            self.info['switch_state'] = 0
            self.info['pinch'] = True
            self.sprites[0].add(CRT_explosion(self.attributes['ctrl'].rect.center,(250,250)))
            self.attributes['ctrl'].y_momentum = -5
            #arms ouchie
            self.attributes['Larm'].aimg.change_anim("hurtloop")
            self.attributes['Rarm'].aimg.change_anim("hurtloop")
            #whiteflash
            self.sprites[0].add(WhiteFlash(surface=self.window,spd=30))
            #removing all warnings
            if '1_warnings' in self.atk_info.keys():
                for warning in self.atk_info['1_warnings']:
                    warning.kill()
                del self.atk_info['1_warnings'][:]
            #warnings
            if '2_Lwarn' in self.atk_info.keys():
                self.atk_info['2_Lwarn'].kill()

        elif self.info['switch_state'] == 0:
            #the control panel falling
            self.attributes['ctrl'].rect.y += self.attributes['ctrl'].y_momentum
            self.attributes['ctrl'].y_momentum += 0.25
            #the crt falling upwards
            if self.attributes['body'].rect.bottom > 0: 
                self.attributes['body'].rect.y -= self.timers['in_state']/5
            #ending falling
            if self.attributes['ctrl'].rect.y > pygame.display.play_dimensions[1] or self.attributes['ctrl'].y_momentum > 50 or self.timers['in_state'] > 480:
                self.attributes['body'].kill()
                self.attributes['ctrl'].kill()
                self.info['switch_state'] = 1


        elif self.info['switch_state'] == 1:
            #moving down new control panel
            self.attributes['body2'].rect.y += 2
            if self.attributes['body2'].rect.y > -5 or self.timers['in_state'] > 640:
                #switching animations and changing state
                self.attributes['Larm'].aimg.change_anim("idle")
                self.attributes['Rarm'].aimg.change_anim("idle")
                self.sprites[0].add(WhiteFlash(surface=self.window))
                self.change_state('idle')
            
    def state_die(self,start:bool=False):
        if start:
            #graphical effects
            self.sprites[0].add(WhiteFlash(surface=self.window,spd=5.0)) #white flash
            newbg=pygame.Surface(pygame.display.play_dimensions);newbg.fill('black')
            self.boss_state.playstate.background.aimg.__init__(host=self.boss_state.playstate.background,force_surf=newbg)
            #defining movement
            self.info['die_state'] = 0 
            self.sprites[0].add(CRT_explosion(self.attributes['body2'].rect.center,(350,350)))
            self.attributes['body2'].y_momentum = -10
            self.attributes['body2'].rotate = 0 
            #killing attributes
            for k,v in self.attributes.items():
                if k != 'body2':v.kill()
            #warnings
            if '2_Lwarn' in self.atk_info.keys():
                self.atk_info['2_Lwarn'].kill()
            #more warnings
            if '1_warnings' in self.atk_info.keys():
                for warning in self.atk_info['1_warnings']:
                    warning.kill()

        #kaboom falling
        elif self.info['die_state'] == 0:
            if self.attributes['body2'].rect.top < pygame.display.play_dimensions[1]:
                self.attributes['body2'].rect.y += self.attributes['body2'].y_momentum
                self.attributes['body2'].y_momentum += .5
                self.attributes['body2'].rotate += 25
                self.attributes['body2'].image = pygame.transform.rotate(self.attributes['body2'].image,self.attributes['body2'].rotate)
            elif self.timers['in_state'] > 360:
                self.info['ENDWORLD'] = self.info['ENDBOSSEVENT'] = True                



class CRT_explosion(Em):
    def __init__(self,coord:tuple,resize:tuple=(125,125)):
        self.lifespan = 0
        Em.__init__(self,im="kaboom",coord=coord,isCenter=True,animation_killonloop=True,resize=(125,125))
    def update(self):
        Em.update(self)
        self.lifespan += 1
    def on_collide(self,collide_type:int,collided:pygame.sprite.Sprite):
        if self.lifespan >= 15: return
        elif type(collided) == Player:collided.hurt()
                




#CRUSTACEAN
class Crustacean(Boss):
    def __init__(self,**kwargs):
        Boss.__init__(self,kwargs=kwargs)

        #basic information
        self.info['health'] = 25 #needed to trigger phase 2 if you shoot accurately
        self.info['shellhealth'] = 600 #needed to trigger phase 2 if you shoot him enough
        self.info['pinch'] = self.info['pinch2'] = False
        self.states['pinch'] = self.state_pinch
        self.states['final'] = self.state_final
        self.bg = self.boss_state.playstate.background

        #attack information
        self.atk_info['enter_time'] = 0 
        self.state = 'enter'
        self.atk_info['types'] = 3 #0 -> conch spam, 1 -> fish spam, 2 -> spinning and circling the border, 3 -> tentacles swiping from the sides
        self.atk_info['type'] = 0 # current attack
        
        #attributes
        self.addAttribute('body',BossAttribute(host=self,sprites=self.sprites,name="body",pos=(-100,100),image="crustbody.png"))
        self.addAttribute('shell',BossAttribute(host=self,sprites=self.sprites,name="shell",pos=(-100,100),image="crustshell.png"))



    def update(self):
        Boss.update(self)
        self.attributes['shell'].rect.center = self.attributes['body'].rect.center
        

    def collision_master(self,collider,collide_type,collided):
        if (collider.name == "shell" or collider.name == "body") and self.info['state'] != 'final' and self.info['state'] != 'enter':
            #jump code
            if type(collided) == Player:
                if ((collider.rect.centery) > collided.rect.bottom-collided.movement[0]):
                    #bouncing the player up
                    collided.bounce()
                    #making the player invincible for six frames to prevent accidental damage
                    collided.invincibility_counter = 18
                    self.info[('shell' if collider.name == 'shell' else '')+'health'] -= 1
                #hurting player if not invincible
                else:
                    collided.hurt()
            #bullet interaction code
            elif collide_type == 1: 
                self.info[('shell' if collider.name == 'shell' else '')+'health'] -= 1
                collided.hurt()
        #CODE EXCLUSIVELY FOR PHASE 3
        elif collider.name == 'body' and self.info['state'] == 'final':
            if type (collided) == Player:
                collided.hurt()
                self.attributes['body'].rect.y -= 100
            elif collide_type == 1:
                self.attributes['body'].rect.y -= 5
                self.info['health'] -= 1
                collided.hurt()
                if self.info['health'] == 10:
                    ps('bigboom1.wav')
        #causing phase 2 
        if self.info['health'] <=0 or self.info['shellhealth'] <=0 and not self.info['pinch']:
            self.change_state('pinch')
        #causing phase 3
        if self.info['health'] <= 0 and self.info['pinch'] and not self.info['pinch2']:
            self.change_state('final')
                
            


    def state_enter(self,start=False):
        #positioning
        if start:
            self.attributes['body'].rect.center = (-100,100)
        
        elif self.timers['in_state'] < 240:
            #waddling onscreen
            if abs(self.attributes['body'].rect.centerx - winrect.centerx) > 10:
                self.attributes['body'].rect.centerx += 2.5 +(sin(self.timers['in_state']/5))
            
        elif self.timers['in_state'] == 240:
            #play hold animation
            self.attributes['body'].rect.center = (winrect.centerx,100)
            self.attributes['body'].aimg.change_anim('start_hold')
        
        elif self.timers['in_state'] == 330:
            #play push animation, change bg, new scrolling effect
            self.sprites[0].add(WhiteFlash(surface=self.window))
            self.attributes['body'].aimg.change_anim('start_push')
            #change bg, like completely initialize it and make the scroll speed QUICK
            self.bg.aimg.__init__(host=self.bg,name="crust_bg.png",resize=(600,800))
            self.bg.speed[1] = 25
            #hiding background elements
            if self.boss_state.playstate.floor is not None:
                self.boss_state.playstate.floor.hide = True
            if self.boss_state.playstate.formation is not None:
                self.boss_state.playstate.formation.image_hide = True


        elif self.timers['in_state'] == 390:
            #new idle animation, begin idle state
            self.change_state('idle')
        
        else:
            pass

            
    def state_idle(self,start=False):
        #centering
        if start:
            self.attributes['body'].rect.center = (winrect.centerx,100)
            self.bg.speed[1] = 15 if not self.info['pinch'] else 2
            self.atk_info['idle_angle'] = atan2(self.player.rect.centery-self.attributes['body'].rect.centery,self.player.rect.centerx-self.attributes['body'].rect.centerx)
        
        #moving around if pinch
        if self.info['pinch']:
            self.attributes['body'].rect.centerx = winrect.centerx + sin(self.timers['in_state']*0.2)*200
            self.attributes['body'].rect.centery = 100 + random.randint(-5,5)
            self.bg.speed[0] = 25*sin(self.timers['in_state']/30)
        #setting the background speed
        else:
            self.bg.speed[0] = 5*sin(self.timers['in_state']/30)

        if self.timers['in_state']%2==0:
            self.attributes['body'].shoot("angle",spd=2,info=(self.attributes['body'].rect.center,self.atk_info['idle_angle']))
            self.attributes['body'].shoot("angle",spd=4,info=(self.attributes['body'].rect.center,self.atk_info['idle_angle']*2))
            self.atk_info['idle_angle'] += 13

        if self.timers['in_state'] > 360: #CHANGE TO 360
            self.change_state('attack')


    def state_attack(self,start=False):
        if start:
            self.bg.speed = [0,-2]
            self.atk_info['type'] = random.randint(0,self.atk_info['types'])
            self.sprites[0].add(WhiteFlash(surface=self.window))
            # self.atk_info['type'] = 2
            #resetting attack information
            self.atk_info['amount'] = 0 #how many times shells/fish have been thrown
            self.atk_info['max'] = 1 #how many times shells/fish will be thrown per attack
            self.atk_info['amountper'] = 1#how many shells/fish will be thrown per throw - getting confusing yet?
            self.atk_info['2_phase'] = 0 #0 -> moving left ; 1 -> moving down ; 2 -> moving right ; 3 -> moving up ; 4 -> moving left ; 0 -> end
            #setting attack-specific attack information
        
        #shooting bullets
        elif self.atk_info['type'] == 0:
            if self.timers['in_state'] % (50 if not self.info['pinch'] else 15) == 0:
                for i in range(random.randint(1,3) if not self.info['pinch'] else random.randint(3,7)):
                    Crustacean.shoot_crustbullet(start=self.attributes['body'].rect.center,end=self.player.rect.center,sprites=self.sprites)
                self.atk_info['amount'] += 1
                if self.timers['in_state'] >= 480 or self.atk_info['amount'] > random.randint(5,10):self.change_state("idle")
            
        #shooting fish
        elif self.atk_info['type'] == 1:
            if self.timers['in_state'] % (45 if not self.info['pinch'] else 30) == 0:
                Crustacean.shoot_crustfish(start=(random.choice((0,pygame.display.play_dimensions[0])),self.attributes['body'].rect.centery+100),player=self.player,sprites=self.sprites)
                self.atk_info['amount'] += 1
                if self.timers['in_state'] >= 360 or self.atk_info['amount'] > random.randint(10,20):self.change_state("idle")


        #zooming up down and all around the stage
        elif self.atk_info['type'] == 2:
            rect = self.attributes['body'].rect
            #going up down and all around the stage
            if self.atk_info['2_phase'] == 0:
                rect.x -= 5
                if rect.centerx <= -10: self.atk_info['2_phase'] = 1

            elif self.atk_info['2_phase'] == 1:
                rect.y += 15
                if rect.centery > self.player.rect.centery: self.atk_info['2_phase'] = 2
                if self.timers['in_state'] % (10 if self.info['health'] > 25 else 5) == 0: 
                    self.attributes['body'].shoot(type="point",spd=7,info=(self.attributes['body'].rect.center,self.player.rect.center))
            elif self.atk_info['2_phase'] == 2:
                rect.x += 25
                if rect.centerx >= pygame.display.play_dimensions[0] + 10: self.atk_info['2_phase'] = 3
            elif self.atk_info['2_phase'] == 3:
                rect.y -= 30
                if abs(rect.centery -100) < 35: self.atk_info['2_phase'] = 4
            elif self.atk_info['2_phase'] == 4:
                rect.x -= 5
                if abs(rect.centerx - winrect.centerx) < 10: self.atk_info['2_phase'] = 999
            else:
                self.change_state("idle")

        #tentacles
        elif self.atk_info['type'] == 3:
            #spawning tentacles 
            self.change_state('idle')

        else:
            self.change_state("idle")



    def state_pinch(self,start=False):
        if start and not self.info['pinch']:
            self.info['pinch'] = True
            self.info['health'] = 75
            self.info['pinchcenter'] = self.attributes['body'].rect.center
            self.attributes['shell'].kill()
            self.sprites[0].add(Em(im="kaboom",coord=self.attributes['body'].rect.center,isCenter=True,animation_killonloop=True,resize=(125,125)))
            self.bg.speed[1] = -1
        elif self.timers['in_state'] < 90:
            self.attributes['body'].rect.center = self.info['pinchcenter'][0] + random.randint(-5,5),self.info['pinchcenter'][1] + random.randint(-5,5)
        elif self.timers['in_state'] >= 90:
            self.bg.speed[1] = 2
            self.change_state('idle')



    def state_final(self,start=False):
        speed = self.bg.speed
        if start:
            for bullet in self.bullets: bullet.kill()
            self.sprites[0].add(Em(im="kaboom",coord=self.attributes['body'].rect.center,isCenter=True,animation_killonloop=True,resize=(200,200)))
            self.attributes['body'].rect.center = (winrect.centerx,100)
            self.info['health'] = 50
            self.info['pinch2'] = True
        #final attack
        elif self.timers['in_state'] < 480:
            #slowing the background down
            if abs(speed[0]) > 0.25: speed[0]*=0.975
            else: speed[0] = 0
            if abs(speed[1]) > 0.25: speed[1]*=0.975
            else: speed[1] = 0
            #making the boss spazz out
            self.attributes['body'].rect.centerx = winrect.centerx
            self.attributes['body'].rect.x += random.randint(-15,15)
            self.attributes['body'].rect.y += random.randint(-2,5)
            #locking the player
            self.player.rect.centerx = winrect.centerx
            self.player.reset_movement()
    


    def state_die(self,start=False):
        if start:
            #resetting the background, and doing some graphical whatnots
            self.attributes['body'].kill()
            self.sprites[0].add(WhiteFlash(surface=self.window,spd=0.5))
            self.bg.pos = [0,0]
            self.bg.speed = [0,0]
            #unhiding the floor and formation image
            if self.boss_state.playstate.floor is not None:
                self.boss_state.playstate.floor.hide = False
            if self.boss_state.playstate.formation is not None:
                self.boss_state.playstate.formation.image_hide = False
            #resetting the background image back to whatever it was before
            self.bg.__init__(self.boss_state.playstate.world_data['bg'], resize = self.boss_state.playstate.world_data['bg_size'], speed = self.boss_state.playstate.world_data['bg_speed'])
            ps('bigboom2.wav')
            
        elif self.timers['in_state'] > 480:
            self.info['ENDBOSSEVENT'] = True




    @staticmethod
    def shoot_crustbullet(start,end,sprites):
        bullet=CrustBullet(start,end)
        sprites[2].add(bullet)
    @staticmethod
    def shoot_crustfish(start,player,sprites):
        fish=CrustFish(start,player)
        sprites[2].add(fish)
    



#Crustaceean Bullet
class CrustBullet(pygame.sprite.Sprite):
    warning = None
    def __init__(self,start:tuple,end:tuple):
        pygame.sprite.Sprite.__init__(self)
        #image info
        self.aimg = AImg(host=self,name="shell.png",resize=(40,40))
        #currently moving in a random direction before jutting towards the player
        self.move = tools.AnglePoint(pointA=start,angle=random.randint(0,360),speed=10,static_speed=False)
        self.state = 0 #0 = startup ; 1 = wait 30 frames ; 2 = launch
        self.state1_count = 0
        self.end=end
        self.timer = 0 
    
    #called per-frame
    def update(self):
        #timer updating -> optimization
        self.timer += 1


        if self.state == 0:
            #slowly slowing down as the bullet moves in a random direction
            self.move.speed = round(self.move.speed * 0.925,3)
            self.move.update();self.rect.center = self.move.position
            #switching the state and also changing the move vals thingamajigger
            if self.move.speed < 1:
                self.state = 1
                self.move = tools.MovingPoint(pointA=self.rect.center,pointB=self.end,speed=20)
                self.timer = 0 


        elif self.state == 1:
            self.state1_count += 1
            if self.state1_count > 15:
                self.state = 2

        
        elif self.state == 2:
            self.move.update();self.rect.center = self.move.position
            if self.timer > 90 and not self.rect.colliderect(pygame.display.play_rect) or self.timer > 360:
                self.kill()
            
    #collision with player
    def on_collide(self,collide_type:int,collided:pygame.sprite.Sprite):
        if type(collided) == Player:
            collided.hurt()
            self.kill()
        elif collide_type == 1:
            collided.hurt()
    



#Crustacean fish
class CrustFish(pygame.sprite.Sprite):
    warning = None
    def __init__(self,start:tuple,player:Player):
        #pygame sprite info
        pygame.sprite.Sprite.__init__(self)
        self.aimg = AImg(host=self,name="crust_fish",resize=(35,35))
        self.rect.center = start

        #basic info
        self.health = 3

        #movement info
        self.player = player #constantly tracking position of player
        self.timer = 0 #timer to update information
        self.move = None
        #entrance_info
        self.in_start = True #a basic entrance state
        self.start_speed = 15 #speed the enemy enters at
        self.start_dir = 0 if self.rect.centerx <= winrect.centerx else 1
     
    def update(self):
        self.timer += 1
        self.aimg.update()
        if self.in_start:
            #moving in a specified direction onscreen, as the fish usually appear offscreen
            self.rect.x += self.start_speed if self.start_dir == 0 else self.start_speed * -1
            self.start_speed *= 0.95
            if self.start_speed < 1:
                self.in_start = False
                self.move = tools.MovingPoint(pointA=self.rect.center,pointB=self.player.rect.center,speed=4)
        else:
            #moving towards the player
            self.move.update()
            self.rect.center = self.move.position
            #updating player position
            if self.timer % 15 == 0:
                self.move.change_all(self.player.rect.center)
            #kill if offscreen
            if not self.rect.colliderect(pygame.display.play_rect):
                self.kill()

    #collision with player
    def on_collide(self,collide_type:int,collided:pygame.sprite.Sprite):

        if type(collided) == Player:
            if ((self.rect.centery) > collided.rect.bottom-collided.movement[0]):
                #bouncing the player up
                collided.bounce()
                #making the player invincible for six frames to prevent accidental damage
                collided.invincibility_counter = 18
                #kill yourself
                self.kill()
            else:
                collided.hurt()
                self.kill()
            
        elif collide_type == 1:
            collided.hurt()
            self.hurt()
    
    #damage
    def hurt(self,amount=1):
        self.health -= amount
        if self.health <= 0:
            self.kill()



#crustacean tentacle
class CrustTentacle(pygame.sprite.Sprite):
    warning = None
    def __init__(self,side=None,target:tuple = (100,100)):
        #sets a destination at the start, and launches towards it
        pygame.sprite.Sprite.__init__(self)
        self.aimg = AImg(host=self,name="tentacle",current_anim = "enter")
        #setting position info
        if side == None: side = random.choice(('l','r'))
        if side == 'l': self.rect.left = 0
        elif side == 'r': self.rect.right = pygame.display.play_dimensions[0]
        self.rect.centery = random.randint(0,pygame.display.play_dimensions[1])
        #misc. data
        self.state = 0 #0 -> wait ; 1 -> launch ; 2 -> kill
        self.angle = 0 
        self.timer = 0 #timer to count waiting amount
    def update(self):
        self.aimg.update()
        self.image = pygame.transform.rotate(self.image,angle=self.angle)
        








#The Sun
class TheSun(Boss):
    def __init__(self,**kwargs):
        Boss.__init__(self,kwargs=kwargs)
        #defining more values here
        #to be fair, I think organizing all the previous values in lists was a bit stupid and confusing
        #however, it is still 'readable' it was just harder to code
        #i'll experiment now
        self.bg = self.boss_state.playstate.background

        #basic information
        self.phase = 0
        self.attacks = [ ] 
        self.attack_total = 0
        self.curattack = 0 #the current attack about to be implanted on this guy
        self.atk_time = 600 #time until an attack comes
        #entrance information
        self.enter_phase = 0 
        self.enter_timer = 0 
        self.enter_speed = [0,0]
        #important info to prevent glitching
        self.flaring = False
        #death information
        self.isdying = False
        self.dietimer = 0 
        self.diephase = 0
        self.diedark = None
        self.diedarkswitch = False


        self.attack_methods = (
            self.attack_confetti,
            self.attack_punch,
            self.attack_bullet,
            self.attack_flare,
        )

        self.info['LAYERPLAYERINFRONT'] = True
        
        #attributes, which is only the sun body
        self.addAttribute(name="body",attribute=BossAttribute(host=self,sprites=self.sprites,name="body",image="boss_sun",pos=(winrect.right,0)))

        self.change_state("enter")


    def state_enter(self,start=False):
        if start:
            self.bg.aimg.__init__(host=self.bg,name="boss_sun_bg",resize=None,current_anim="0")
            self.enter_timer += 1
            self.enter_phase = 0
            self.enter_speed = [0,0] #they are set to this as placeholder values, because the speed has to be greater than 0
            self.attributes['body'].aimg.change_anim('idle')
            #hiding background elements
            if self.boss_state.playstate.formation is not None:
                self.boss_state.playstate.formation.image_hide = True


        elif self.enter_phase == 0:
            #waits a couple frames
            self.enter_timer += 1
            if self.enter_timer >= 180:
                #setting the next phase up
                self.enter_timer = 0
                self.enter_phase = 1
                self.attributes['body'].aimg.change_anim('angry1')

        elif self.enter_phase == 1:
            #waits a couple frames
            self.enter_timer += 1
            if self.enter_timer >= 120:
                #setting the next phase up
                self.enter_timer = 0
                self.enter_phase = 2
                self.attributes['body'].aimg.change_anim('angry2')

        elif self.enter_phase == 2:
            #moving to the center
            if self.attributes['body'].rect.centerx > (winrect.centerx+10):
                self.enter_speed[0] = abs(self.attributes['body'].rect.centerx-winrect.centerx)/50
                self.attributes['body'].rect.x -= self.enter_speed[0]
            else:
                self.enter_speed[0] = 0 
                self.attributes['body'].rect.centerx = winrect.centerx
            #moving to the bottom
            if self.attributes['body'].rect.centery < (winrect.centery-10):
                self.enter_speed[1] += 0.1 
                self.attributes['body'].rect.y += self.enter_speed[1]
            else:
                self.enter_speed[1] = 0
                self.attributes['body'].rect.centery = winrect.centery
            #checking to see if both of those are completed
            if self.attributes['body'].rect.centery == winrect.centery and self.attributes['body'].rect.centerx == winrect.centerx:
                if self.enter_timer == 0:
                    self.attributes['body'].aimg.change_anim('phase0')
                self.enter_timer += 1
                if self.enter_timer >= 60:
                    self.change_state('idle')
                    self.enter_timer = 0 
                    
                if self.boss_state.playstate.floor is not None:
                    self.boss_state.playstate.floor.hide = True



    def state_idle(self,start=False):
        if start:
            self.change_phase()
            self.bg.aimg.change_anim(str(self.phase))
            self.attributes['body'].aimg.change_anim("phase"+str(self.phase))
            self.sprites[0].add(WhiteFlash(self.window,start_val=192,spd=5.0))
        
        if self.timers['in_state'] == self.atk_time//2:
            #deciding what curattack is 
            if self.attack_total <= 3:
                self.curattack = self.attack_total
            elif self.flaring is not None: 
                self.curattack = random.randint(0,2)
            else:
                self.curattack = random.randint(0,3)
            self.sprites[0].add(sunWarn(anim=str(self.curattack)))

        if self.timers['in_state'] >= self.atk_time:
            self.attacks.append({'type':self.curattack,'time':0,'done':False})
            id = len(self.attacks) - 1
            self.attack_methods[self.curattack](id=id,start=True)
            self.attack_total += 1
            self.change_state('idle')
        
        for i in range(len(self.attacks)):
            #updating the attack and the attack timer
            self.attacks[i]['done'] = self.attack_methods[self.attacks[i]['type']](id=i)
            self.attacks[i]['time'] += 1
            #deleting dead enemies, and immediately breaking the loop 
            if self.attacks[i]['done']:
                del self.attacks[i]
                break



    def state_die(self,start=False):
        if start:
            self.isdying = False
            self.dietimer = self.diephase = 0 
        #DYING PHASE 1 -> waiting for the attacks to stop
        elif len(self.attacks) > 0:
            for i in range(len(self.attacks)):
                #updating the attack and the attack timer
                self.attacks[i]['done'] = self.attack_methods[self.attacks[i]['type']](id=i)
                self.attacks[i]['time'] += 1
                #deleting dead enemies, and immediately breaking the loop 
                if self.attacks[i]['done']:
                    del self.attacks[i]
                    break
        #DYING PHASE 2 -> SHOWING THE BOSS IS DYING
        elif not self.isdying:
            self.isdying = True
            self.bg.aimg.change_anim('5')
            self.attributes['body'].aimg.change_anim("phase5")
            self.sprites[0].add(WhiteFlash(self.window,start_val=255,spd=0.75))
        #DYING PHASE 3 -> WAITING
        elif self.diephase == 0:
            self.dietimer += 1
            #hanging out for a while at the death screen
            if self.dietimer > 480:
                self.dietimer = 0 
                self.diephase = 1
                #creating a darkness that consumes all
                self.diedark = WhiteFlash(self.window,start_val=0,end_val=400,spd=-1,color="#000000",isreverse=True)
                self.sprites[0].add(self.diedark)

        #DYING PHASE 4 -> CONSUMED IN DARKNESS
        elif self.diephase == 1:
            self.dietimer += 1
            if self.dietimer == 375:
                self.bg.__init__("black", resize = self.boss_state.playstate.world_data['bg_size'], speed = self.boss_state.playstate.world_data['bg_speed'])
                self.attributes['body'].kill()
            #resetting everything when the screen is black
            if self.dietimer > 500:
                self.diephase = 2
                self.dietimer = 0


        #DYING PHASE 5 -> NO MORE
        elif self.diephase == 2:
            self.info['ENDBOSSEVENT'] = self.info['ENDWORLD'] = True
            

                







    def attack_confetti(self,id:int,start=False) -> bool:
        info = self.attacks[id]
        
        if start:
            #creating basic values put into the attack list's dictionary
            info['yippee'] = sunYippee()
            self.sprites[0].add(info['yippee'])
            info['timer'] = info['amount'] = 0
            return False

        else:
            #timer stuff
            info['timer'] += 1
            if info['timer']%30==0:
                #shooting off confetti
                info['timer'] = 0 ; info['amount'] += 1
                ps('yippee.mp3');info['yippee'].aimg.change_anim('attack')
                #shooting off confetti
                for i in range(10):
                    confetti = Confetti(pos = (self.player.rect.centerx,random.randint(200,400)))
                    self.sprites[2].add(confetti)
            #exiting
            if info['amount'] > 10:
                info['yippee'].kill()
                return True #telling the boss it's done
            #not exitintg
            else:
                return False
                


    def attack_punch(self,id:int,start=False) -> bool:
        #creating information about the attack, as instead of a class I use a dictionary like a loooooser
        info = self.attacks[id]
        if start:
            info['amount'] = 0
            info['timer'] = 30 
        else:
            info['timer'] += 1
            if info['timer'] > 30:
                info['amount'] += 1
                info['timer'] = 0 
                self.sprites[2].add(sunArm(host = self))
            if info['amount'] > 5:
                return True
            else:
                return False
              


    def attack_bullet(self,id:int,start=False) -> bool:
        info = self.attacks[id]
        if start:
            info['gun'] = sunGun(sprites=self.sprites,host=self)
            self.sprites[2].add(info['gun'])
        elif info['gun'].finished:
            return True
        else:
            return False



    def attack_flare(self,id:int,start=False) -> bool  :
        info = self.attacks[id]

        if start:
            self.flaring = True
            info['flare'] = WhiteFlash(surface=self.window,start_val=0,end_val=250.0,spd=-1.0,img="boss_sun_flash",isreverse=True)
            info['sunblock'] = sunBlock(player=self.player)
            info['gohere'] = Em(im="ui_gohere",coord=(info['sunblock'].rect.x-50,info['sunblock'].rect.centery),isCenter=True)
            info['flared'] = False
            self.sprites[0].add(info['flare'],info['gohere'])
            self.sprites[2].add(info['sunblock'])
            return False
        else:
            if info['sunblock'].got and not info['gohere'].dead: info['gohere'].kill()
            if info['flare'].vals[0] == 180 and not info['flared']:
                ps('bigboom1.wav') 
            elif info['flare'].vals[0] >= 250 and not info['flared']:
                #finishing the flare, creating a damaging sunwave
                info['gohere'].kill();info['sunblock'].kill();info['flare'].kill()
                info['flared'] = True;ps('bigboom2.wav') 
                #maiking a flashing effect that either does nothing or damages the player
                flash = WhiteFlash(surface=self.window,start_val=255,end_val=0,spd=15.0,isreverse=False)
                self.sprites[(2 if not info['sunblock'].got else 0)].add(flash)
                #creating an explosion effect for the sunblock 
                if info['sunblock'].got: 
                    self.sprites[0].add(Em(im='kaboom',coord=self.player.rect.center,isCenter=True,animation_killonloop=True))
                #killing the attack assets
                info['flare'].kill();info['sunblock'].kill();info['gohere'].kill()
                self.flaring = False
                return True
            else:
                return False
                



    def change_phase(self):
        if self.attack_total < 4:
            self.phase = 0 
            self.atk_time = 600
        elif self.attack_total < 8:
            self.phase = 1
            self.atk_time = 450
        elif self.attack_total < 12:
            self.phase = 2
            self.atk_time = 300
        elif self.attack_total < 16:
            self.phase = 3
            self.atk_time = 180
        elif self.attack_total < 20:
            self.phase = 4
            self.atk_time = 120
        elif self.attack_total >= 20:
            self.change_state('die')
            



class sunWarn(pygame.sprite.Sprite):
    def __init__(self,anim='0'):
        pygame.sprite.Sprite.__init__(self)
        self.aimg = AImg(host=self,name="boss_sun_sign",current_anim=anim)
        self.lifespan = 0
        self.x = random.choice((150,winrect.right-150))
        self.y = -100
    def update(self):
        self.lifespan += 1
        self.y += 6
        self.rect.centery = self.y + 50*sin(self.lifespan/25)
        self.rect.centerx = self.x + random.randint(-5,5)
        if self.rect.top > winrect.bottom:
            self.kill()
        self.aimg.update()



class sunYippee(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.aimg = AImg(host=self,name="boss_sun_yippee")
        self.rect.center = (winrect.width*.75,winrect.height*.85)
        self.mask = self.aimg.mask
    def update(self):
        self.aimg.update()
    


class sunArm(pygame.sprite.Sprite):
    def __init__(self,host):
        pygame.sprite.Sprite.__init__(self)
        #setting info
        self.aimg = AImg(host=self,name="boss_sun_arm")
        self.rect.top = 0 #The arm sits at the top waiting for a spot to fall
        self.rect.centerx = winrect.centerx #starts at the center
        self.mask = self.aimg.mask
        self.warning = Warning(pos = (-100,-100))
        host.sprites[0].add(self.warning)
        self.lifespan = 0 #a timer used for checking the phases
        self.spd = random.randint(1,30)
        self.phase = 0 # 0 -> moving back and forth ; 1 -> waiting for a moment before going down ; 2 -> throwing down until hitting the bottom ; 3 -> waiting a few frames ; 4 -> going back up until gone
        
        self.host=host
    
    def update(self):
        #updating the timer
        self.lifespan += 1
        #image
        self.aimg.update()

        if self.phase == 0:
            # moving back and forth
            self.rect.centerx = winrect.centerx + (winrect.centerx * sin(self.lifespan / self.spd))
            #moving onto and setting up next phase
            if self.lifespan > 120 and abs(self.rect.centerx - self.host.player.rect.centerx) < 15:
                self.phase = 1
                self.lifespan = 0
                self.warning.rect.centery = self.host.player.bar[1]
                self.warning.rect.centerx = self.rect.centerx
        elif self.phase == 1:
            #just waiting
            if self.lifespan > 60:
                self.phase = 2
                self.lifespan = 0
        elif self.phase == 2:
            #going down
            self.rect.y += 40
            if self.rect.bottom > winrect.height:
                self.rect.bottom = winrect.height
                self.phase = 3
                self.lifespan = 0
                self.aimg.change_anim('squash')
                self.warning.kill()
        elif self.phase == 3:
            #waiting a little longer
            if self.lifespan > 15:
                self.phase = 4
                self.lifespan = 0
        elif self.phase == 4:
            #flying off
            self.rect.y -= 50
            if self.rect.bottom < 0:
                self.kill()


    def on_collide(self,collide_type,collided):
        if type(collided) == Player:
            #killing bullet
            collided.hurt()
        elif collide_type == 1:
            collided.hurt()
            if self.phase == 2:
                self.rect.y -= 80



class sunBlock(pygame.sprite.Sprite):
    def __init__(self,player):
        pygame.sprite.Sprite.__init__(self)
        self.aimg = AImg(host=self,name="sunblock.png")
        self.mask = self.aimg.mask
        self.got = False
        self.player = player
        self.rect.center = (random.randint(0,winrect.right),self.player.bar[1] - random.randint(0,75))
    def update(self):
        if not self.got: return
        else:
            self.rect.center = self.player.rect.center
    def on_collide(self,collide_type,collided):
        if self.got:
            return
        elif type(collided) == Player:
            self.got = True



class sunGun(pygame.sprite.Sprite):
    def __init__(self,sprites,host,shots=10,shoottimer=30):
        pygame.sprite.Sprite.__init__(self)
        self.aimg = AImg(host=self,name="gun.png")
        self.rect.center = winrect.centerx,0
        self.angle = 0 ; self.anglev = 1 ; self.shoottimer = shoottimer ; self.timer = 0 ; self.lifespan = 0 
        self.sprites = sprites
        self.finished = False
        self.health = 25

    def update(self):
        self.angle += self.anglev
        self.anglev += 0.01
        #image rotation + placement
        self.aimg.update()
        self.image = pygame.transform.rotate(self.image,self.angle)
        self.rect = self.image.get_rect()
        self.rect.center = ((winrect.centerx + (winrect.centerx*0.75*sin(self.lifespan/20))),60+self.lifespan//10)
        #timer to shoot
        self.timer += 1 ; self.lifespan += 1
        if self.timer > self.shoottimer:
            bullet = HurtBullet(type="angle",spd=7,info=(self.rect.center,self.angle*-1),texture="bullet.png")
            self.sprites[2].add(bullet)
            self.shoottimer -= 1
            self.timer = 0
            
        if self.shoottimer <= -60:  
            self.finished = True
            self.kill()
        
    def on_collide(self,collide_type,collided):
        #taking damge from bullets and hurting the player
        if collide_type == 1:
            collided.hurt()
            self.health -=1
            if self.health <=0:
                self.finished = True
                self.kill()

    


class Angel(Boss):
    def __init__(self):
        Boss.__init__(self)
        




loaded = {
    "ufo":UFO,
    "nope":Nope,
    "crt":CRT,
    "crustacean":Crustacean,
    "sun":TheSun,
}