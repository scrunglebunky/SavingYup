import pygame, enemies, tools
from anim import AutoImage as AImg
from emblems import Emblem as Em
from emblems import TextEmblem as TEm
from player import Player
""" 
THE BOSS(ES) BUT NOT REALLY IT'S JUST ONE BOSS
CONGRATULATIONS! YOU'VE GOTTEN PAST 4 LEVELS! BUT TO BEAT THE ZONE, YOU NEED TO BEAT THE BOSS!
KING NOPE IS WHAT HOLDS YOU BACK FROM YOUR NEXT ASCENSION! KILL HIM.

The boss is a pygame.sprite.Sprite asset in the enemies group.
It shares methods with a lot of other sprites: hurt, on_collide, etc.
It shares other attributes with other sprites: health, state, states, aimg, etc.

When the boss is initialized, it sets its values and decides its health, idle state, and available attacks based off difficulty
The boss will be in its Idle state, and after enough time decide an attack to go through based off its attack pool

just listing off the available states
#####
idle_0 # the enemy just sits there not moving, maybe shaking a little bit
idle_1 # it moves back and forth in a sine pattern like atk_sine, scales in speed based off difficulty
idle_2 # it just copies spasm but it doesn't attack this time
idle_3 # copies atk_teleport but also doesn't attack
idle_n
atk_bounce # the enemy points towards you and launches itself at you while bouncing along anything it sees
atk_spasm # the enemy does a bounce to random spots while shooting in all directions each time it hits its point
atk_sine # it moves around back and forth in a sine for both x and y while shooting in all directions (but this time only 1 bullet at a time)
atk_fall # it moves back and forth in a sine pattern (for x) and randomly slams its body down to the bottom of the screen
atk_jump # the enemy moves up and down in a sine pattern, and randomly jumps to the opposite side
atk_teleport # spasm but scarier. he teleports from each spot and does the same shooting stuff
atk_throw # the seashells attack from the crustacean, where the bullets pop out from a differing angle, and then all aim towards the player
atk_children # nope starts giving violent birth and its children slowly move towards you unless you kill them
atk_n
entrance # coming in -- invincible
exit # dying
done # dead
#####
Each of these attacks are actual classes, because they do things on start and end.
The classes take the host boss as an argument.

"""


class Boss(pygame.sprite.Sprite):
    # all states
    allstates ={
        "enter":Enter,
        "idle1":Idle1,
    }
    # idles
    idles = [
        "idle1"
    ]
    # attacks
    attacks = [
        "attack1"
    ]
    

    def __init__(self,formation):
        pygame.sprite.Sprite.__init__(self)
        self.formation = formation
        # pulling from formation
        self.player = self.formation.player
        self.sprites = self.formation.sprites
        self.difficulty = self.formation.difficulty_rounded
        self.window = self.formation.window
        # image/rect
        self.aimg = AImg(host=self,name="nope_D")
        # just note that pos is changed a whole bunch, and THEN changed into rect.center
        self.pos = formation.pos
        self.rect.center = self.pos 

        # basic info
        self.health = 100*(self.difficulty) if self.difficulty < 100 else 10000 
        self.score = 1
        self.dead = False
        self.in_atk = False
        self.state = "enter"
        self.maxhealth = self.health 

        # healthbar info
        self.healthbar_pos = (self.window.get_width()/2,15)


    
    def update(self):
        self.aimg.update()



    @staticmethod
    def generate_attacklist(difficulty) -> list:
        output = []
        # 3 attacks are unlocked at a base
        # and then a new attack is unlocked per difficulty


    def make_attack(self):
        ...

    # collision
    def on_collide(self,
                   collide_type:int, #the collide_type refers to the sprite group numbers. 0 for universal (not used), 1 for other player elements, 2 for enemies
                   collided:pygame.sprite.Sprite,
                   ):
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
        # wow you get auto money
        self.player.coins += damage*self.score
        # self.change_anim("hurt")
        # self.sprites[0].add(Em(im='die',coord=self.rect.center,isCenter=True,animation_killonloop=True))
        

    # basic methods that the template uses, so nothing breaks with an error
    def formationUpdate(self,*args,**kwargs):...


""" THE BOSS STATE
This is the parent class for all boss states, including attacks, idles, etc.
They take the host boss as an argument and modify it as time goes on.
The BossState class defines things that are used in every boss class."""
class BossState():
    def __init__(self,host,lifespan_force = 120):
        self.life = 0
        self.active = False # if the state is running
        self.ended = False # if the state is over -- kind of goes hand-in-hand with active
        self.host = host
        self.lifespan = lifespan_force # this is the default set lifespan, and will be changed afterwards or in the argument by a boss class
    def start(self):
        # this isn't really used...
        self.active = True
        self.ended = False
    def end(self):
        self.active = False
        self.ended = True
    def update(self):
        self.life += 1
        if self.life >= self.lifespan:
            self.end()




""" THE IDLE BOSS STATE
This is a modification of the boss state that is only used for the idle states.
All this really does is make the parent class do an attack after finishing."""
class IdleState(BossState):  
    def end(self):
        self.host.make_attack()




class Enter(BossState):
    def __init__(self,host,*args,**kwargs):
        BossState.__init__(self,host,lifespan_force = 240)
        # the boss flies down rapidly, and then the speed gradually goes down until it stops
        self.mp = tools.MovingPoint(pointA = (host.window.get_width()/2,-10), pointB = (host.window.get_width(),host.window.get_height()*.25),speed = 10, ignore_speed = True, check_finished = False)
    
    def update(self,host):
        # updating the speed
        self.mp.update()
        if not self.mp.finished:
            if self.mp.speed < 0.01: 
                self.mp.speed = 0 
                self.mp.finished = True
            else: 
                self.mp.speed *= 0.95
        # just note that the rest of the finishing code for this state is handled by the default stuff



# idle v1 -- sitting there and doing not much
class Idle1(IdleState):
    def __init__(self,host,*args,**kwargs):
        BossState.__init__(self,host,lifespan_force = 360-(self.difficulty*5))
    
    def update(self):
        BossState.update(self)
        self.pos