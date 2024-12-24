import pygame, enemies, tools, random, math, bullets
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

just listing off the available states -- NOT ALL OF THESE MADE IT IN OR WORK THE SAME AS STATED.
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


""" BOSS SUB-CLASS ATTACKS
I asked an AI to give me groups of attacks I could use to give to the boss subclasses. Here is what it gave me.
For organizing the attacks into sub-classes, you can group them by common behavior or theme. I’ve divided the attacks into 20 groups of 3, where each group corresponds to a distinct sub-class with a unique flavor of movement and attack pattern. Each group features similar dynamics to give the boss subclasses distinct personalities and patterns. Here's the suggested organization:

    Bounce-Based Attacks:
        atkbounce (bouncing with bullet bursts)
        atkthrow (sine pattern with bullet throw)
        atkfall (falling with position adjustment)

    Teleportation-Based Attacks:
        atkteleport (random teleportation with bullet circle)
        atkchase (moves towards the player while attacking)
        atkspiral (spiraling motion while shooting)

    Patterned Sine-Based Attacks:
        atksine (sine movement with radial bullets)
        atkslide (jumping sine pattern with falling bullets)
        atkfall (falling with patterns that mimic sine behavior)

    Beam Attacks:
        atkbeam (stationary 4-direction beam rotation)
        atkswing (group of bullets thrown at you with a swinging arc)
        atkcurve (bullets in a circular pattern with angle variation)

    Bullet Wall Attacks:
        atkwall (walls of bullets with gaps)
        atkblast (huge bullet wall forcing directional movement)
        atkbirth (spawns mini enemies that keep attacking)

    Position-Based Attacks:
        atkperimeter (moves along stage walls)
        atkjump (throws sideways bullets forcing player to jump)
        atkhoriz (sideways bullet throw forcing jump/fall)

    Complex Bullet Spasms:
        atkspasm (random tweening with downward shooting)
        atksine (sine wave motion while shooting in all directions)
        atkthrow (sine with bullet variation)

    Chase and Close-Range Attacks:
        atkchase (boss moves toward player gradually)
        atkslam (boss locks in and slams down)
        atkfall (boss falls to player’s position)

    Horizontal Bullet Attacks:
        atkhoriz (sideward bullets forcing movement)
        atkjump (sideways bullet throw)
        atkwall (falling walls with small gaps)

    Evasive and Teleporting Attacks:
        atkteleport (teleporting with bullet circle)
        atkperimeter (movement along the edges of the stage)
        atkspiral (spiraling movement pattern)

    Wave-like Attacks:
        atkspasm (random tweening with shooting bursts)
        atkfall (falling bullet wave from above)
        atksine (sine-based wave motion with shooting)

    Clever Dodge/Chase Attacks:
        atkchase (boss moves toward you)
        atkthrow (sine with bullet throws)
        atkbeam (shoots 4-direction beams)

    Wall Formation Attacks:
        atkwall (walls with bullet gaps)
        atkblast (big bullet wall forcing side movement)
        atkcurve (bullets in unpredictable circular paths)

    Evasive Attacks with Homing:
        atkswing (bullets fly at varying angles before homing)
        atkcurve (bullets in chaotic circular paths)
        atkbounce (bouncing with bullet circles)

    Melee and Close Combat Attacks:
        atkslam (boss slams down after moving towards player)
        atkfall (boss falls while adjusting position)
        atkspasm (tweens randomly while attacking)

    Repetitive Fire Attacks:
        atkbeam (stationary 4-direction beams)
        atkspasm (tweens with continual shooting)
        atkswing (regular throwing of homing bullets)

    Difficult Evasion Attacks:
        atkcurve (bullets with random directional changes)
        atkperimeter (moves along walls with unpredictable attacks)
        atkthrow (sine movement with bullet throws)

    Explosive Formation Attacks:
        atkblast (wall of bullets forcing movement)
        atkbirth (mini enemies spawn to attack)
        atkslam (sine pattern with a final slam)

    Dynamic Stage Control Attacks:
        atkwall (falling walls with gaps to jump through)
        atkbounce (bouncing bullets creating multiple paths)
        atkspiral (spiraling motion forcing jumps)

    High-Intensity Multi-Move Attacks:
        atkspasm (random tweens with frequent attacks)
        atkchase (boss chases the player down)
        atkbeam (beam shooting in multiple directions)

Wow, isn't Artificial Intelligence a wonder to behold? At least I'm not some lazy numnut using it to make the code for me.
Or to make the art.
What am I? Lazy? Well yeah but not THAT lazy.
"""


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
    def on_collide(self,collide_type,collided):
        ... # this does nothing by default, it's just there to be there


""" THE IDLE BOSS STATE
This is a modification of the boss state that is only used for the idle states.
All this really does is make the parent class do an attack after finishing."""
class IdleState(BossState):  
    def __init__(self,host,*args,**kwargs):
        BossState.__init__(self,host,lifespan_force = (360 - host.difficulty*20) if host.difficulty < 12 else 120)
        self.host.aimg.change_anim('idle')
    def end(self):
        self.host.make_attack()

""" THE ATTACK BOSS STATE
a sliiiiight modification of the boss state
this makes the parent class go to idle after finishing
and it also has a pre-set attack length
"""
class AtkState(BossState):  
    def __init__(self,host,*args,**kwargs):
        BossState.__init__(self,host,lifespan_force = (480-(host.difficulty*20)) if host.difficulty < 12 else 240)
        self.host.aimg.change_anim('attack')
    def end(self):
        self.host.make_idle()


"""THE DIE BOSS STATE
the simplest of the three
it just has a pre-set lifespan window
and it moves around"""
class DieState(BossState):
    def __init__(self,host,*args,**kwargs):
        BossState.__init__(self,host=host,lifespan_force=(180))
        self.host.aimg.change_anim('die')
    def end(self):
        # telling the boss to tell the formation to move to the next level
        self.host.dead = True
        self.host.kill()


##########   BASIC STATES

# enter -- lowering down
class Enter(BossState):
    spr_introtext = TEm(txt="THIS\nIS AN ERROR\nAND SHOULD NOT\nSHOW UP",coord=(0,0))
    def __init__(self,host,*args,**kwargs):
        BossState.__init__(self,host,lifespan_force = 240)
        # the boss flies down rapidly, and then the speed gradually goes down until it stops
        self.mp = tools.MovingPoint(pointA = (host.window.get_width()/2,-10), pointB = (host.window.get_width()/2,host.window.get_height()*.5),speed = 10, ignore_speed = True, check_finished = False)
        self.host.aimg.change_anim('idle')
        # updating the intro text
        self.textfull:str = self.host.introtext.split('\n')
        self.textcurrent = ""
        self.linecounter = 0 
        self.texttimer = 60
        self.texttime = 60
        # adding introtext
        Enter.spr_introtext.update_text("")
        Enter.spr_introtext.kill()
        self.host.sprites[0].add(Enter.spr_introtext)
        # the host is intangible
        self.host.intangible =True

    def update(self):
        # updating the speed
        if self.mp.finished:
            # # when it's done moving, the boss goes into idle
            # self.end()
            # self.host.make_idle()
            # return
            ...
        else:
            self.mp.update()
            if self.mp.speed < 0.01: 
                self.mp.speed = 0 
                self.mp.finished = True
            else: 
                self.mp.speed *= 0.95
        
        # updating the text
        self.texttime += 1
        if self.texttime > self.texttimer:
            self.texttime = 0
            self.update_introtext()
            # print('done')

        # just note that the rest of the finishing code for this state is handled by the default stuff
        self.host.pos = self.mp.position

    def update_introtext(self):
        # this function adds a line, and updates the text
        self.textcurrent = ""

        # making sure no overflow
        if self.linecounter >= len(self.textfull):
            self.linecounter = len(self.textfull) - 1
            self.end()
        else:
            self.linecounter += 1



        #reassembling the text into a string
        for i in range(self.linecounter):
            self.textcurrent += self.textfull[i] + "\n"    
        
        # updating the textemblem
        Enter.spr_introtext.update_text(self.textcurrent)

    def end(self):
        BossState.end(self)
        Enter.spr_introtext.kill()
        self.host.make_idle()
        self.host.intangible = False

########## DIE STATES -- (simple)


# die -- flying off
class Die1(DieState):
    def __init__(self,host,*args,**kwargs):
        DieState.__init__(self,host=host)
        # positioning and intangibility
        self.pos = self.host.pos
        self.velocity = 10
        self.host.intangible = True
    def update(self):
        BossState.update(self)
        # flying off
        self.velocity -= 0.75
        self.pos[1] += self.velocity
        self.host.pos = self.pos
    
# die -- falling down
class Die2(DieState):
    def __init__(self,host,*args,**kwargs):
        DieState.__init__(self,host=host)
        # positioning and intangibility
        self.pos = self.host.pos
        self.velocity = -10
        self.host.intangible = True
    def update(self):
        BossState.update(self)
        # flying off
        self.velocity += 0.75
        self.pos[1] += self.velocity
        self.host.pos = self.pos
    
# die3 -- bouncing everywhere
class Die3(DieState):
    def __init__(self,host,*args,**kwargs):
        DieState.__init__(self,host=host)
        # positioning and intangibility
        self.angle = random.randint(0,360)
        self.move_vals = list(tools.AnglePoint.calc_move_vals(math.radians(self.angle),speed=100,static_speed=True))
        self.pos = self.host.pos
        self.intangible = True
    def update(self):
        BossState.update(self)
        # flying off
        self.pos[0] += self.move_vals[0]
        self.pos[1] += self.move_vals[1]
        # bouncing
        if self.pos[0] > self.host.window.get_width() and self.move_vals[0] > 0 or self.pos[0] < 0 and self.move_vals[0] < 0:
            self.move_vals[0]*=-1
        if self.pos[1] > self.host.window.get_height() and self.move_vals[1] > 0 or self.pos[1] < 0 and self.move_vals[1] < 0:
            self.move_vals[1]*=-1
    
# die -- spazzing out
class Die4(DieState):
    def __init__(self,host,*args,**kwargs):
        DieState.__init__(self,host=host)
        # positioning and intangibility
        self.pos = self.host.pos
        
    def update(self):
        BossState.update(self)
        self.pos[0] += random.randint(-25,25)
        self.pos[1] += random.randint(-25,25)
        self.host.pos = self.pos

# die -- inching off
class Die5(DieState):
    def __init__(self,host,*args,**kwargs):
        DieState.__init__(self,host=host)
        # positioning and intangibility
        self.pos = self.host.pos
        self.mp = tools.AnglePoint(pointA = self.pos,angle = random.randint(0,360),speed=1)
        self.host.intangible = True
        
    def update(self):
        BossState.update(self)
        self.mp.update()
        self.pos = self.mp.position
        self.host.pos = self.pos

# die -- doing nothing
class Die6(DieState):
    def __init__(self,host,*args,**kwargs):
        DieState.__init__(self,host=host)
        self.pos = self.host.pos
        self.host.intangible = True
    def update(self):
        BossState.update(self)









#########   IDLE STATES

# idle v1 -- sitting there and doing not much
class Idle1(IdleState):
    def __init__(self,host,*args,**kwargs):
        IdleState.__init__(self,host=host)
        make_explosion(coord=self.host.pos,group=self.host.sprites[0])
        self.pos = (random.randint(0,self.host.window.get_width()),random.randint(0,self.host.window.get_height()//2))    
        self.offset = [0,0]
    def update(self):
        BossState.update(self)
        self.offset = [random.randint(-5,5),random.randint(-5,5)]
        self.host.pos = [self.pos[0]+self.offset[0],self.pos[1]+self.offset[1]]

# idle v2 -- waving back and forth 
class Idle2(IdleState):
    def __init__(self,host,*args,**kwargs):
        IdleState.__init__(self,host=host)
        self.middle_h = self.host.window.get_width()//2
        self.middle_v = self.host.window.get_height()//4
        self.speed_h = self.host.difficulty/50
        self.speed_v = self.host.difficulty/10
        self.range_h = self.middle_h * 0.7    
        self.range_v = self.host.window.get_height() * .05    

        self.pos = [self.middle_h,self.middle_v]

    def update(self):
        BossState.update(self)
        self.pos[0] = self.middle_h + (math.sin(self.life*self.speed_h)*self.range_h)
        self.pos[1] = self.middle_v + (math.sin(self.life*self.speed_v)*self.range_v)
        self.host.pos = self.pos

# idle v3 -- teleporting around
class Idle3(IdleState):
    def __init__(self,host,*args,**kwargs):
        IdleState.__init__(self,host=host)
        self.timelimit = 90 - (self.host.difficulty * 4)
        self.pos = self.host.pos[:]
        self.move()
    def update(self):
        BossState.update(self)
        # moving to a new position every x frames
        if self.life % self.timelimit == 0 or self.timelimit <=0:
            self.move()
        # setting position stuff
        self.host.pos = self.pos
    def move(self):
        # add explosion at previous point
        make_explosion(coord=self.pos,group=self.host.sprites[0])
        # move to new point
        self.pos = [random.randint(0,self.host.window.get_width()),random.randint(0,self.host.window.get_height()//2)]
        # makes another explosion
        # make_explosion(coord=self.pos,group=self.host.sprites[0])

# idle v4 -- zig zagging around
class Idle4(IdleState):
    def __init__(self,host,*args,**kwargs):
        IdleState.__init__(self,host=host)
        self.pos = self.host.pos[:]
        self.mp = self.redo_mp()

    def update(self):
        # yupdating the state
        IdleState.update(self)

        # yupdating mp
        self.mp.update()
        self.pos = self.mp.position
        
        # slowing down mp
        if self.mp.speed <= 1:
            self.mp.speed = 1
        else:
            self.mp.speed *= 0.98

        # setting a new mp value
        if self.mp.finished:
            self.mp = self.redo_mp()
        
        # updating host position with this position
        self.host.pos = self.pos

    def redo_mp(self):
        return tools.MovingPoint(
            pointA = self.pos, 
            pointB = (random.randint(0,self.host.window.get_width()),random.randint(0,self.host.window.get_height()//2)),
            speed = self.host.difficulty * 3 if self.host.difficulty < 20 else 23,
            check_finished = True,
            ignore_speed = True,
            )



##########   ATTACK STATES

# bounce attack -- pointing at a random spot and then bouncing along, shooting in every direction with each bounce
class AtkBounce(AtkState):
    def __init__(self,host):
        AtkState.__init__(self,host=host)
        # it makes a move_vals value based off a random angle, which now doesn't have any angles or fancy math since it's truly random
        self.angle = random.uniform(0,2*3.14)
        self.move_vals = [math.cos(self.angle),math.sin(self.angle)]
        self.spd = 0.1
        self.max_spd = self.host.difficulty * 5 if self.host.difficulty < 2 else 10
        self.pos = self.host.pos[:]
    
    def update(self):
        BossState.update(self)
        # yupdating movement
        self.pos[0] += self.move_vals[0] * self.spd
        self.pos[1] += self.move_vals[1] * self.spd
        # yupdating sppeed
        if self.spd < self.max_spd:
            self.spd *= 1.05
        else:
            self.spd = self.max_spd

        # doing bounce code
        self.bounce()

        # updating host position
        self.host.pos = self.pos
        
    def bounce(self):
        mh = self.move_vals[0]
        mv = self.move_vals[1]
        ph = self.pos[0]
        pv = self.pos[1]
        bounced = False

        if ph < self.spd:
            # left 
            mh = mh * -1 if mh < 0 else mh
            bounced = True
        elif ph > self.host.window.get_width()-self.spd:
            # right
            mh = mh * -1 if mh > 0 else mh
            bounced = True
        if pv < self.spd:
            # top
            mv = mv * -1 if mv < 0 else mv
            bounced = True 
        elif pv > self.host.window.get_height()-self.spd:
            # bottom
            mv = mv * -1 if mv > 0 else mv
            bounced = True

        if bounced:
            for i in range(18):
                self.host.shoot(type="angle",spd=2,info=(self.host.pos,i*20))

            
        self.move_vals = [mh,mv]
        return




# spasm attack -- copying the idle4 directly but every time it redoes mp it shoots at you a few times
class AtkSpasm(AtkState):
    def __init__(self,host):
        AtkState.__init__(self,host=host)
        self.pos = self.host.pos[:]
        self.mp = Idle4.redo_mp(self)
        self.shoottimer = (30 - self.host.difficulty * 3) if self.host.difficulty < 8 else 5
        self.shoottime = 0

    def update(self):
        BossState.update(self)

        # yupdating mp
        self.mp.update()
        self.pos = self.mp.position
        
        # slowing down mp
        if self.mp.speed <= self.host.difficulty if self.host.difficulty < 5 else 5:
            self.mp.speed = self.host.difficulty if self.host.difficulty < 5 else 5
        else:
            self.mp.speed *= 0.95

        # setting a new mp value
        if self.mp.finished:
            self.mp = Idle4.redo_mp(self)
            # shooting as well
            for i in range(5):
                self.host.shoot(
                    type="point",
                    spd=random.randint(5,7),
                    info=(
                        self.host.pos,(self.host.player.pos[0]+random.randint(-25,25),
                        self.host.player.pos[1]+random.randint(-25,25))))

        # note the enemy also just shoots a few bullets down
        self.shoottime += 1
        if self.shoottime >= self.shoottimer:
            self.shoottime = 0
            self.host.shoot(
                type="angle",
                spd=random.randint(5,7),
                info=(self.host.pos,90)
            )

        # updating host position with this position
        self.host.pos = self.pos




# sine attack -- moves in a sine pattern and shoots circularly
# this is really easy at a low level   
class AtkSine(AtkState):
    def __init__(self,host):
        AtkState.__init__(self,host=host)
        self.angle = 0
        self.shoottimer = 10-self.host.difficulty 
        self.shoottime = 0  

        # movement information
        self.middle_h = self.host.window.get_width()//2
        self.middle_v = self.host.window.get_height()//4
        self.speed_h = self.host.difficulty/100
        self.speed_v = self.host.difficulty/50
        self.range_h = self.middle_h * 0.7    
        self.range_v = self.host.window.get_height() * .05    

        # position
        self.pos = [self.middle_h,self.middle_v]


    def update(self):
        BossState.update(self)

        # yupdating angle and shooting
        self.shoottime += 1
        if self.shoottime > self.shoottimer:
            self.angle += (5 + self.host.difficulty) if self.host.difficulty < 5 else 10
            self.host.shoot(type="angle",spd=3,info=(self.host.pos,self.angle))
            self.shoottime = 0

        # m,oving
        self.pos[0] = self.middle_h + (math.sin(self.life*self.speed_h)*self.range_h)
        self.pos[1] = self.middle_v + (math.sin(self.life*self.speed_v)*self.range_v)
        self.host.pos = self.pos




# Atk Teleport -- just a clone of the idle teleport but he shoots!
# Not gonna lie, I think the idle state should just be him standing still at this point.
class AtkTeleport(AtkState):

    def __init__(self,host,*args,**kwargs):
        AtkState.__init__(self,host=host)
        self.timelimit = (60 - (self.host.difficulty * 5)) if self.host.difficulty < 11 else 5
        self.pos = self.host.pos[:]
        self.move()
    def update(self):
        BossState.update(self)
        # moving to a new position every x frames
        if self.life % self.timelimit == 0 or self.timelimit <=0:
            self.move()
        # setting position stuff
        self.host.pos = self.pos
    def move(self):
        # add explosion at previous point
        make_explosion(coord=self.pos,group=self.host.sprites[0])
        # move to new point
        self.pos = [random.randint(0,self.host.window.get_width()),random.randint(0,self.host.window.get_height()//2)]
        # makes another explosion
        # make_explosion(coord=self.pos,group=self.host.sprites[0])
        for i in range(18):
            self.host.shoot(type="angle",spd=5,info=(self.host.pos,i*20))




# Atk Throw. Okay this is a lie. He moves back and forth in a sine pattern and occasionally shoots a blast of bullets down
class AtkThrow(AtkState):
    def __init__(self,host,*args,**kwargs):
        AtkState.__init__(self,host=host)
        self.timelimit = (60 - self.host.difficulty*5) if self.host.difficulty < 9 else 15
        # movement information
        self.middle_h = self.host.window.get_width()//2
        self.middle_v = self.host.window.get_height()//4
        self.speed_h = self.host.difficulty/50
        # self.speed_v = self.host.difficulty/50
        self.range_h = self.middle_h * 0.7    
        # self.range_v = self.host.window.get_height() * .05    

        # position
        self.pos = [self.middle_h,self.middle_v]
        self.host.pos = self.pos


    def update(self):
        BossState.update(self)
        # moving left to right
        self.pos[0] = self.middle_h + (math.sin(self.life*self.speed_h)*self.range_h)
        if self.life % self.timelimit == 0:
            for i in range(10):
                self.host.shoot('angle',random.randint(7,10),info=(self.pos,random.randint(80,100)))

        # updating host pos
        self.host.pos = self.pos




# Atk Beam -- goes in 4 directions and spins, however he does this in stationary
class AtkBeam(AtkState):
    def __init__(self,host,*args,**kwargs):
        AtkState.__init__(self,host=host)
        self.angle = 0
        self.shoottimer = 5 - self.host.difficulty
        self.shoottime = 0
        self.pos = [random.randint(0,self.host.window.get_width()),random.randint(0,self.host.window.get_height()//4)]
        # graphical explosion effect
        make_explosion(coord=self.host.pos,group=self.host.sprites[0])
        self.host.pos = self.pos

    def update(self):
        BossState.update(self)
        self.shoottime += 1
        if self.shoottime > self.shoottimer:
            self.shoottime = 0
            self.angle += (math.sin(self.life/50)*100)
            for i in range(4):
                self.host.shoot("angle",3 ,info=(self.pos,self.angle + i * 90))
        self.host.pos = self.pos




# Atk Jump -- spawns these large slow-moving bullets you have to jump over. Don't cheat by double jumping!
class AtkJump(AtkState):
    def __init__(self,host,*args,**kwargs):
        AtkState.__init__(self,host=host)
        self.ceilingshoottimer = 5
        self.ceilingshoottime = 0 
        self.floorshoottimer = (120 - self.host.difficulty*5) if self.host.difficulty < 12 else 60
        self.floorshoottime = random.randint(0,15)
        self.floorshoottime2 = random.randint(0,15)
    
    def update(self):
        BossState.update(self)

        # the ceiling shoot time
        self.ceilingshoottime += 1
        if self.ceilingshoottime > self.ceilingshoottimer:
            self.ceilingshoottime = 0
            self.host.shoot("angle",25,((10,self.host.player.bar[1]-130),0))
            self.host.shoot("angle",25,((self.host.window.get_width()-10,self.host.player.bar[1]-130),180))
        
        # the floor shoot time
        self.floorshoottime += 1
        if self.floorshoottime > self.floorshoottimer:
            self.floorshoottime = 0
            # note the size is determined by the texture because the masks are pre-generated and resizing them doesnt change it
            self.host.shoot("angle",random.randint(4,10),((10,self.host.player.bar[1]),0),texture="bullet_big")
            self.floorshoottimer = random.randint(30,(120 - self.host.difficulty*5) if self.host.difficulty < 12 else 60)

        
        # the second floor shoot time if the difficulty is high
        if self.host.difficulty > 6:
            self.floorshoottime2 += 1
            if self.floorshoottime2 > self.floorshoottimer:
                self.floorshoottime2 = 0
                # note the size is determined by the texture because the masks are pre-generated and resizing them doesnt change it
                self.host.shoot("angle",random.randint(4,10),((self.host.window.get_width()-10,self.host.player.bar[1]),180),texture="bullet_big")
                

# Atk Slide -- the enemy moves up and down along a wall in a sine pattern, and randomly jumps
# when the enemy jumps, it rains bullets and the screen shakes
class AtkSlide(AtkState):
    def __init__(self,host,*args,**kwargs):
        AtkState.__init__(self,host=host)
        self.middle_v = self.host.window.get_height()//3
        self.speed_v = 1/30
        self.range_v = self.host.window.get_height()//4   

        self.side:int = 0 # 0 = left, 1 = right
        self.positions:tuple = (10,self.host.window.get_width()-10)
        self.in_jump:bool = True
        self.jumptimer = random.randint(15,(120 - self.host.difficulty* 5) if self.host.difficulty < 20 else 20)
        self.jumptime = 9999

        # setting pos
        # self.pos = [self.positions[self.side],self.middle_v]
        self.pos = self.host.pos[:]


    def update(self):
        BossState.update(self)
        # vert mov
        self.pos[1] = self.middle_v + (math.sin(self.life*self.speed_v)*self.range_v)
        self.host.pos = self.pos
        # horizontal timer
        self.jumptime += 1
        if self.jumptime > self.jumptimer: 
            # starting the jump
            self.jumptime = 0 
            self.jumptimer = random.randint(15,(120 - self.host.difficulty* 5) if self.host.difficulty < 20 else 20)
            self.in_jump = True
            # this is what side it's GOING to, or where it's AT.
            self.side = 0 if self.side == 1 else 1

        # actually doing the jump
        if self.in_jump:
            if self.side == 0:
                # moving to the left 
                self.pos[0] -= 50
                if self.pos[0] <= 10:
                    # resets the position AND makes it rain
                    self.pos[0] = 10
                    self.in_jump = False
                    self.make_rain()
            elif self.side == 1:
                # moving to the right 
                self.pos[0] += 50
                if self.pos[0] >= self.host.window.get_width()-10:
                    # resets the position AND makes it rain
                    self.pos[0] = self.host.window.get_width()-10
                    self.in_jump = False
                    self.make_rain()

        self.host.pos = self.pos
    
    def make_rain(self):
        for i in range(15):
            self.shootrain()
    
    def shootrain(self):
        rain = Rain(pos = ((random.randint(10,self.host.window.get_width()-10)),10), bottom = self.host.window.get_height())
        self.host.sprites[2].add(rain)
        return rain




# Atk Wall -- the enemy sits there and walls of the "rain" attribute fall, leaving small gaps for you to fall through
class AtkWall(AtkState):
    def __init__(self,host,*args,**kwargs):
        AtkState.__init__(self,host=host)
        self.wall_min = 60 - self.host.difficulty * 5 if self.host.difficulty < 11 else 5
        self.wall_max = 120 - self.host.difficulty * 10 if self.host.difficulty < 11 else 10
        self.wall_speed = 5 + self.host.difficulty if self.host.difficulty < 15 else 20
        self.wall_width = self.host.window.get_width() / 50
        self.walltimer = random.randint(self.wall_min,self.wall_max)
        self.walltime = 0
        self.gap_point = random.randint(0,39)
        

    def update(self):
        BossState.update(self)
        self.walltime += 1
        if self.walltime > self.walltimer:
            self.walltime = 0
            self.walltimer = random.randint(self.wall_min,self.wall_max)
            self.make_wall()

    
    def make_wall(self):
        # this makes 50 rain assets
        # however, there is a gap of 3, marked at a certain point
        self.gap_point += random.randint(-3,3)
        if self.gap_point > 39:
            self.gap_point -= 5
        if self.gap_point < 0:
            self.gap_point += 5
        for i in range(50):
            if i >= self.gap_point and i < self.gap_point + 10:
                continue
            else:
                rain = Rain(pos=(1+i*self.wall_width,10),acceleration=0.1,terminal=self.wall_speed)
                self.host.sprites[2].add(rain)



# Atk Swing -- what atk throw was originally 
# It jumps around like the AtkSpasm, but every time the momentum stops entirely it throws a bunch of shells at you and then stops again
class AtkSwing(AtkState):
    def __init__(self,host,*args,**kwargs):
        AtkState.__init__(self,host=host)
        self.pos = self.host.pos[:]
        self.mp = Idle4.redo_mp(self)

    def update(self):
        BossState.update(self)

        self.mp.update()
        self.pos = self.mp.position
        self.mp.speed *= (0.995 - (self.host.difficulty * 0.02)) if self.host.difficulty < 15 else 0.65
        # if the speed slows to a crawl, it bounces again and does the shooty shoot.
        if self.mp.speed < 0.5:
            self.mp = Idle4.redo_mp(self)
            for i in range(5):
                self.swing_bullets()

        self.host.pos = self.pos

    def swing_bullets(self):
        itm = SwingBullet(pos=self.host.rect.center,player = self.host.player)
        self.host.sprites[2].add(itm)



#Atk Curve -- similar to atkbeam but it's jagged,and changes the angle every x frames
class AtkCurve(AtkState):
    def __init__(self,host,*args,**kwargs):
        AtkState.__init__(self,host=host)
        self.updatetimer = 120 - self.host.difficulty*10 if self.host.difficulty < 11 else 5
        self.updatetime = 0
        self.shoottimer = 3
        self.shoottime = 0

        # the info that gets updated with updatetimer
        self.angle = 0

    
        # moving to a new spot
        self.pos = [random.randint(100,self.host.window.get_width()-100),random.randint(100,self.host.window.get_height()//4)]
        make_explosion(coord=self.host.pos,group=self.host.sprites[0])
        self.host.pos = self.pos

    def update(self):
        BossState.update(self)

        # shooting 5 bullets at a time 360 degrees
        self.shoottime += 1
        if self.shoottime > self.shoottimer:
            self.shoottime = 0
            for i in range(12):
                self.host.shoot("angle",(5 + self.host.difficulty) if self.host.difficulty < 10 else 15 ,info=(self.pos,self.angle + i * 30))
        
        self.updatetime += 1
        if self.updatetime > self.updatetimer:
            self.updatetime = 0
            self.angle = random.randint(0,360)

        # position
        self.host.pos = self.pos



#Atk Horiz -- horizontally throwing bullets at you leaving you to jump and fast fall
class AtkHoriz(AtkState):
    def __init__(self,host,*args,**kwargs):
        AtkState.__init__(self,host=host)
        self.player = self.host.player
        self.time = 0
        self.timer = (60 - (self.host.difficulty * 5)) if self.host.difficulty < 10 else 10
        

    def update(self):
        BossState.update(self)
        self.time += 1
        if self.time > self.timer:
            self.time = 0
            if bool(random.randint(0,1)):
                # shoot right
                self.host.shoot("angle",15,((10,self.player.pos[1]),0),texture="bullet_big")

            else:
                # shoot left
                self.host.shoot("angle",15,((self.host.window.get_width()-10,self.player.pos[1]),180),texture="bullet_big")



#Atk Birth -- it spawns a group of nopes that do their attack and die
# Actually this is too complicated, I'll just make an asset that chases after you
class AtkBirth(AtkState):
    def __init__(self,host,*args,**kwargs):
        AtkState.__init__(self,host=host)
        # timer info
        self.birthtimer = (60 - (self.host.difficulty * 5)) if self.host.difficulty < 11 else 5
        self.birthtime = 0
        # positioning info
        # moving to a new spot
        self.pos = [self.host.window.get_width()//2,self.host.window.get_height()//4]
        self.centerx = self.pos[0]
        self.centery = self.pos[1]
        make_explosion(coord=self.host.pos,group=self.host.sprites[0])
        self.host.pos = self.pos

    def update(self):
        BossState.update(self)
        # updating positioning
        self.pos[0] = self.centerx + math.sin(self.life/50)*200
        self.host.pos = self.pos
        # birthing info
        self.birthtime += 1
        if self.birthtime > self.birthtimer:
            self.birthtime = 0
            print(self.pos)
            new = random.choice([BirthEnemyA,BirthEnemyB,BirthEnemyC])(pos = self.pos,player=self.host.player)
            self.host.sprites[2].add(new)
        

#Atk Blast -- Nope makes a huge wall of bullets and blasts them while moving to a certain side of the wall
class AtkBlast(AtkState):
    def __init__(self,host,*args,**kwargs):
        AtkState.__init__(self,host=host) 
        # i can't explain this, this only exists in my mind.
        self.blastwidth = self.host.window.get_width()//50
        self.blastindex = 0 
        # timer until the blaster moves right
        self.blasttimer = 10 - self.host.difficulty
        self.blasttime = 0
        # right or left
        self.direction = random.choice((-1,1)) # 1 for right, -1 for left
        # shoott iming
        self.shoottimer = 0
        self.shoottime = 0
        self.swapped = False
        # wait timing
        self.waittimer = 0

    def update(self):
        BossState.update(self)
        # it waits a few frames at the end so you can actually make it to the other side
        if self.waittimer != 0:
            self.waittimer -= 1
        else:
            # timing the shoot
            self.shoottime += 1
            if self.shoottime > self.shoottimer:
                self.shoottime = 0 
                self.host.shoot("angle",10,info=((self.blastindex * self.blastwidth,0),90))
            # timing the blast
            self.blasttime += 1
            if self.blasttime > self.blasttimer:
                self.blasttime = 0 
                self.blastindex += self.direction
                if self.blastindex >= 45 and self.direction == 1:
                    self.direction = -1
                    self.blastindex = 50
                    self.swapped = True
                    self.waittimer = 30
                elif self.blastindex <= 5 and self.direction == -1:
                    self.direction = 1
                    self.blastindex = 0
                    self.swapped = True
                    self.waittimer = 30
            
            
#Atk Chase -- Nope puts a MP at YOUR position! He's coming at you fast, better avoid him!
class AtkChase(AtkState):
    def __init__(self,host,*args,**kwargs):
        AtkState.__init__(self,host=host)
        self.player = self.host.player
        self.pos = self.host.pos[:]
        self.mp = tools.MovingPoint(pointA=self.pos,pointB=self.player.pos,speed=10,ignore_speed=True)
        self.min_speed = (1 + self.host.difficulty/2) if self.host.difficulty < 14 else 8

    def update(self):
        BossState.update(self)
        # moves towards player
        self.mp.update()
        self.pos = self.mp.position
        # slows down mp
        if self.mp.speed > self.min_speed:
            # slows down mp
            self.mp.speed *= 0.98
        else:
            # updating mp
            self.mp = tools.MovingPoint(pointA=self.pos,pointB=self.player.pos,speed=10,ignore_speed=True)
        # telling boss to go to recorded position
        self.host.pos = self.pos


#Atk Slam -- Nope follows you at the top and throws himself down at you a few times! Be careful!
class AtkSlam(AtkState):
    def __init__(self,host,*args,**kwargs):
        AtkState.__init__(self,host=host)
        self.lifespan *= 2 # makes it harder :3
        # sine pattern information
        self.centerx = self.host.window.get_width()//2
        self.centery = self.host.window.get_width()//8
        self.rangex = self.host.window.get_width()//2
        self.speedx = (50 - (self.host.difficulty * 5)) if self.host.difficulty < 9 else 5
        # positioning
        self.pos = [self.centerx,self.centery]
        # locking information
        self.lock: bool = False
        self.lockframes = 0
        self.lockpos = [0,0]
        self.lockvelocity = 0
        self.lockvelocityterminal = 50
        self.lockacceleration = 0.1 * self.host.difficulty
        self.lockbottom = self.host.window.get_height()*0.9
    def update(self):
        BossState.update(self)
        if not self.lock:
            # updating x position
            posold = self.pos[0]
            self.pos[0] = self.centerx + math.sin((self.life-self.lockframes) / self.speedx)*self.rangex
            # checking for closeness
            if abs(self.pos[0] - self.host.player.pos[0]) < (10+(abs(self.pos[0] - posold))):
                self.lock = True
                self.lockpos = self.pos[:]
            # same stuff
            self.host.pos = self.pos
        else:
            # falling down
            self.lockframes += 1
            self.lockpos[1] += self.lockvelocity
            # updating velocity if moving down
            if True:
                if self.lockvelocity < self.lockvelocityterminal:
                    self.lockvelocity += self.lockacceleration
                else:
                    self.lockvelocity = self.lockvelocityterminal
            # inverting velocity if the enemy has passed the floor
            if self.lockpos[1] > self.lockbottom:
                self.lockvelocity *= -1
                for i in range(10):
                    rain = Rain(pos = [random.randint(10,self.host.window.get_width()-10),10],acceleration=random.uniform(0.1,0.5),terminal=random.uniform(5,10))
                    self.host.sprites[2].add(rain)
            # ending lock if the enemy goes back up to the top
            if self.lockpos[1] < self.pos[1] and self.lockvelocity < 0:
                self.lock = False
                self.lockvelocity = 0 
            # updating pos
            self.host.pos = self.lockpos
            
            
    
#Atk Fall -- Like slam, but this time Nope falls from the top to the bottom and teleports back to the top and continues falling, at your position now!
class AtkFall(AtkState):
    def __init__(self,host,*args,**kwargs):
        AtkState.__init__(self,host=host)
        self.velocity = 0
        self.velocityterminal = 10*self.host.difficulty if self.host.difficulty < 5 else 60
        self.acceleration = 0.25
        self.pos = [self.host.player.pos[0],-10]
        self.bottom = self.host.window.get_height()

    def update(self):
        BossState.update(self)
        # moving down
        self.pos[1] += self.velocity
        # updating velocity
        if self.velocity < self.velocityterminal:
            self.velocity += self.acceleration
        else:
            self.velocity = self.velocityterminal
        # if it's at the bottom it re-positions to the top and at the player
        if self.host.rect.top > self.bottom:
            self.pos[1] = -25
            self.pos[0] = self.host.player.pos[0]
        # updating host position to attack position
        self.host.pos = self.pos


#Atk Spiral -- Nope starts in the middle, but moves in a circular pattern until he goes offscreen, and then comes back
class AtkSpiral(AtkState):
    def __init__(self,host,*args,**kwargs):
        AtkState.__init__(self,host=host)
        # changing position
        make_explosion(coord=self.host.pos,group = self.host.sprites[0])
        self.host.pos = list(self.host.window.get_rect().center)
        # rotation stuff
        self.angle = 0 # in radians
        self.radius = 0 # in radiuses :3
        self.speedangle = 3.14 / (15 - self.host.difficulty if self.host.difficulty < 5 else 10)
        self.speedradius = 2
        # positions
        self.ogpos = self.host.pos[:]
        self.pos = self.host.pos[:]
    def update(self):
        BossState.update(self)
        # updating position. Thanks, calculus! (Shake Kraynak)
        self.pos[0] = self.ogpos[0] + (self.radius * math.cos(self.angle))
        self.pos[1] = self.ogpos[1] + (self.radius * math.sin(self.angle))
        # updating radius and angle
        self.angle += self.speedangle
        self.radius += 2
        # shooting
        if self.radius <= 15 * self.host.difficulty:
            Boss.shoot(self.host,type="angle",spd=5,info=(self.host.pos,math.degrees(self.angle*-1)))
        # same thing
        self.host.pos = self.pos

#Atk Perimeter -- Nope goes to the walls of the stage and spins along it. When he's far from you, he shoots!!
class AtkPerimeter(AtkState):
    def __init__(self,host,*args,**kwargs):
        AtkState.__init__(self,host=host)
        self.position = 0 # 0-3
        self.velocity = 0
        self.acceleration = 0.25
        self.velocityterminal = 5*self.host.difficulty if self.host.difficulty < 10 else 50
        offset = self.host.window.get_height()-self.host.player.bar[1]
        self.walls = [offset,self.host.window.get_width()-offset,self.host.window.get_height()-offset]
        self.pos = [offset for i in range(2)]

    def update(self):
        BossState.update(self)
        # speed info
        if self.velocity<self.velocityterminal:self.velocity += self.acceleration
        else:self.velocity = self.velocityterminal
        # moving based off position
        match self.position:
            case 0:
                self.pos[0] += self.velocity
                if self.pos[0] > self.walls[1]:
                    self.position = 1
                    self.pos[0] = self.walls[1]
                # if self.life % 5 == 0:
                Boss.shoot(self.host,"point",spd=10,info=(self.host.pos,self.host.player.pos))
            case 1:
                self.pos[1] += self.velocity
                if self.pos[1] > self.walls[2]:
                    self.position = 2
                    self.pos[1] = self.walls[2]
            case 2:
                self.pos[0] -= self.velocity
                if self.pos[0] < self.walls[0]:
                    self.position = 3
                    self.pos[0] = self.walls[0]
            case 3:
                self.pos[1] -= self.velocity
                if self.pos[1] < self.walls[0]:
                    self.position = 0
                    self.pos[1] = self.walls[0]
        # same thing
        self.host.pos = self.pos











########### THE boss class, which holds all the assets and everything of that matter.
class Boss(pygame.sprite.Sprite):
    # all states
    allstates ={
        "enter":Enter,
        "idle1":Idle1,
        "idle2":Idle2,
        "idle3":Idle3,
        "idle4":Idle4,
        "atkbounce":AtkBounce,
        "atkspasm":AtkSpasm,
        "atksine":AtkSine,
        "atkteleport":AtkTeleport,
        "atkthrow":AtkThrow,
        "atkbeam":AtkBeam,
        "atkjump":AtkJump,
        "atkslide":AtkSlide,
        "atkwall":AtkWall,
        "atkswing":AtkSwing,
        "atkcurve":AtkCurve,
        "atkhoriz":AtkHoriz,
        "atkbirth":AtkBirth,
        "atkblast":AtkBlast,
        "atkchase":AtkChase,
        "atkslam":AtkSlam,
        "atkfall":AtkFall,
        "atkspiral":AtkSpiral,
        "atkperimeter":AtkPerimeter,
        'die1':Die1,
        'die2':Die2,
        'die3':Die3,
        'die4':Die4,
        'die5':Die5

    }
    # idles
    allidle = [
        "idle1",
        "idle2",
        "idle3",
        "idle4",
    ]
    # attacks
    allatk = [
        "atkbounce", # picks an angle and moves across the stage at the angle, shooting a circle of bullets each time it bounces
        "atkspasm", # starts slowly tweening to different parts of the stage, shooting downwards the entire time and shooting at you every time it picks a new spot to tween to
        "atksine", # moves back and forth in a sine pattern, up and down in a sine pattern, shooting bullets all 360 degrees one at a time every x frames
        "atkteleport", # teleports to random positions and shoots bullets in a circle (all 360 degrees at once) per teleportation
        "atkthrow", # moves back and forth in a sine pattern, and shoots bullets down (with variation of 20 degrees) every so and so frames
        "atkbeam", # stands in one spot, shooting in 4 directions while rotating the angles by (sin) degrees
        "atkjump", # shoots bullets sideways towards the player, forcing them to jump
        "atkslide", # jumping from side to side, making bullets fall from the ceiling with each jump
        "atkwall", # making walls of bullets fall from the ceiling, leaving tiny gaps for you to run through
        "atkswing", # throws a group of bullets at you every x frames. however, the bullets fly out at different angles at first before homing at you.
        "atkcurve", # shoots in a circle, but randomly changes the angle to a random value so you have to adjust very fast
        "atkhoriz", # throwing bullets at you from the side so you have to jump or fastfall. like atkjump but simpler
        "atkbirth", # creates miniature versions of the previous enemies that attack you. will stay on screen even into the next attack
        "atkblast", # creates a huge wall of bullets that force you to move to one side of the stage or another
        "atkchase", # the boss moves towards the player gradually. run.
        "atkslam", # the boss moves back and forth in a sine pattern and throws its body down when it locks in with you
        "atkfall", # the boss falls from top to bottom of the screen, and reappears back at the top at your current x position
        "atkspiral", # the boss moves in a spiral pattern, leaving you to time your jump to escape
        "atkperimeter" # the boss moves along the 4 walls of the stage, leaving you to jump.
    ]
    # deaths
    alldie = [
        'die1',
        'die2',
        'die3',
        'die4',
        'die5'
    ]

    # spritesheets
    allsprites = [
        "boss_baby",
        "boss_bald",
        "boss_bfdi",
        "boss_big",
        "boss_blue",
        "boss_eww",
        "boss_exe",
        "boss_fruity",
        "boss_greasy",
        "boss_green",
        "boss_hairy",
        "boss_hatter",
        "boss_king_upsidedown",
        "boss_king1",
        "boss_king2",
        "boss_larry",
    ]
    

    def __init__(self,formation):
        pygame.sprite.Sprite.__init__(self)
        self.formation = formation
        # pulling from formation
        self.player = self.formation.player
        self.sprites = self.formation.sprites
        self.difficulty = self.formation.difficulty_rounded
        # self.difficulty = 15
        self.window = self.formation.window
        # image/rect
        self.spritename = self.generate_sprite()
        self.aimg = AImg(host=self,name=self.spritename)
        # just note that pos is changed a whole bunch, and THEN changed into rect.center
        self.pos = formation.pos[:]
        self.rect.center = self.pos

        # basic info
        self.health = 50*(self.difficulty) if self.difficulty < 100 else 10000 
        self.score = 1
        self.dead = False # dead means the boss is actually finished and is ready to move onto the next level
        self.isdead = False # isdead is what is used if the boss is dying and is getting ready to be dead
        self.in_atk = False
        self.maxhealth = self.health 
        self.intangible = False # if this is true, the player cannot be touched by him
        # intro text -- what the game says during the enter state :3
        self.introtext = self.generate_introtext()

        # state info
        self.cur_state = "enter" # the name of the next state
        self.state = None
        self.change_state(self.cur_state) # the actual state classrunning 
        self.idlelist = self.generate_idlelist()
        self.atklist = self.generate_atklist()
        self.dielist = self.generate_dielist()

        # healthbar info
        self.healthbar_pos = (self.window.get_width()/2,15)


        

        # TEEEST 
        # self.health = -1000


    
    def update(self):
        self.aimg.update()
        self.state.update()
        self.die_check()

        
        self.rect.center = self.pos

    @staticmethod
    def generate_atklist() -> list:
        output = []
        # 3 attacks are unlocked at a base
        # and then a new attack is unlocked per difficulty
        return Boss.allatk[:] # this is a test, just so when idle attacks you can see something is being done

    @staticmethod
    def generate_idlelist() -> list:
        output = []
        # one random idle is picked per bossfight
        return [random.choice(Boss.allidle)]

    @staticmethod
    def generate_dielist() -> list:
        output = []
        return Boss.alldie[:] #test, or not, idk.

    @staticmethod
    def generate_sprite() -> str:
        return random.choice(Boss.allsprites)

    @staticmethod
    def generate_introtext() -> str:
        return "RAA I AM\nTHE DEFAULT BOSS\nFEAR ME."

    def make_attack(self):
        self.in_atk = True
        self.change_state(random.choice(self.atklist))

    def make_idle(self):
        self.in_atk = False
        self.change_state(random.choice(self.idlelist))

    def make_die(self):
        self.isdead = True
        self.intangible = True
        self.in_atk = False
        self.change_state(random.choice(self.dielist))
        

    def die_check(self):
        # not doing kill code if 
        if self.isdead: return

        if self.health <= 0:
            self.make_die()


    # collision
    def on_collide(self,
                   collide_type:int, #the collide_type refers to the sprite group numbers. 0 for universal (not used), 1 for other player elements, 2 for enemies
                   collided:pygame.sprite.Sprite,
                   ):
        #if colliding with an enemy, either hurt or bounce based on positioning
        if type(collided) == Player :
            if self.intangible:
                return
            else:
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
            if self.intangible:
                return
            #I SAID damaging the enemy either way
            self.hurt(collided.dmg)
            collided.hurt()
    
    
    def hurt(self,damage=1):
        self.health -= damage
        # wow you get auto money
        self.player.coins += damage*self.score
        # self.change_anim("hurt")
        # self.sprites[0].add(Em(im='die',coord=self.rect.center,isCenter=True,animation_killonloop=True))
        # spritesheet code
        if self.health % 5 == 0:
            if self.in_atk:
                self.aimg.change_anim("hurt_attack")
            else:
                self.aimg.change_anim("hurt_idle")
        
    def change_state(self,newstate:str):
        self.cur_state = newstate
        self.state:BossState = Boss.allstates[newstate](host=self)
        self.state.start()

    # basic methods that the template uses, so nothing breaks with an error
    def formationUpdate(self,*args,**kwargs):...

    # the shoot method creates a bullet following certain criteria annd then ... yeah you get it.
    def shoot(self,type:str="point",spd:int=7,info:tuple=((0,0),(100,100)),texture="bullet_def",resize = None):
        bullet = bullets.HurtBullet(type=type,spd=spd,info=info,texture=texture,resize=resize)
        # self.sprites[0].add(bullet)
        self.sprites[2].add(bullet)
        return bullet











########### BOSS DERIVATIVES
"""
speaking of, here they are in list form
# ["atkbounce", "atkthrow", "atkfall"]  # Bounce-Based Attacks
# ["atkteleport", "atkchase", "atkspiral"]  # Teleportation-Based Attacks
# ["atksine", "atkslide", "atkfall"]  # Patterned Sine-Based Attacks
# ["atkbeam", "atkswing", "atkcurve"]  # Beam Attacks
# ["atkwall", "atkblast", "atkbirth"]  # Bullet Wall Attacks
# ["atkperimeter", "atkjump", "atkhoriz"] # Position-Based Attacks
["atkspasm", "atksine", "atkthrow"]  # Complex Bullet Spasms
# ["atkchase", "atkslam", "atkfall"] # Chase and Close-Range Attacks
# ["atkhoriz", "atkjump", "atkwall"] # Horizontal Bullet Attacks
# ["atkteleport", "atkperimeter", "atkspiral"] # Evasive and Teleporting Attacks
["atkspasm", "atkfall", "atksine"]  # Wave-like Attacks
# ["atkchase", "atkthrow", "atkbeam"]  # Clever Dodge/Chase Attacks
["atkwall", "atkblast", "atkcurve"]  # Wall Formation Attacks
["atkswing", "atkcurve", "atkbounce"] # Evasive Attacks with Homing
# ["atkslam", "atkfall", "atkspasm"] # Melee and Close Combat Attacks
["atkbeam", "atkspasm", "atkswing"] # Repetitive Fire Attacks
["atkcurve", "atkperimeter", "atkthrow"] # Difficult Evasion Attacks
# ["atkblast", "atkbirth", "atkslam"] # Explosive Formation Attacks
# ["atkwall", "atkbounce", "atkspiral"]  # Dynamic Stage Control Attacks
["atkspasm", "atkchase", "atkbeam"] # High-Intensity Multi-Move Attacks
"""

#### THESE ARE BOSS ASSETS THAT DO EVERYTHING IDENTICALLY, BUT HAVE THEIR OWN PRESET ATTACK PATTERNS (modifies fetch_Xlist)
class bossBig(Boss):
    def generate_atklist(self): return ["atkbounce", "atkthrow", "atkfall"]  # Bounce-Based Attacks
    def generate_idlelist(self): return ["idle1"]
    def generate_introtext(self): return "BIG NOPE\nI'M DA GIANT\nNOPE THAT MAKES\nALL OF DA RULES\n"
    def generate_dielist(self):return Boss.generate_dielist()
    def generate_sprite(self): return "boss_big"
class bossKing1(Boss):
    def generate_atklist(self): return ["atkteleport", "atkchase", "atkspiral"]  # Teleportation-Based Attacks
    def generate_idlelist(self): return ["idle3"]
    def generate_introtext(self): return "KING NOPE\n   THE 1ST\nHE DOESN'T LIKE YOU"
    def generate_dielist(self):return Boss.generate_dielist()
    def generate_sprite(self): return "boss_king1"
class bossKing2(Boss):
    def generate_atklist(self): return ["atksine", "atkslide", "atkfall"]  # Patterned Sine-Based Attacks
    def generate_idlelist(self): return ["idle2"]
    def generate_introtext(self): return "KING NOPE\n   THE 2ST\nHE STILL DOESN'T LIKE YOU"
    def generate_dielist(self):return Boss.generate_dielist()
    def generate_sprite(self): return "boss_king2"
class bossBaby(Boss):
    def generate_atklist(self): return ["atkchase", "atkthrow", "atkbeam"]  # Clever Dodge/Chase Attacks
    def generate_idlelist(self): return ["idle1"]
    def generate_introtext(self): return "KING NOPE\n   THE BABYst\nSHOOT THE BABY"
    def generate_dielist(self):return Boss.generate_dielist()
    def generate_sprite(self): return "boss_baby"
class bossHairy(Boss):
    def generate_atklist(self): return ["atkblast", "atkbirth", "atkslam"] # Explosive Formation Attacks
    def generate_idlelist(self): return ["idle3"]
    def generate_introtext(self): return "PRINCE NOPE\n   THE HAIRY\nHE LOST HIS BRUSH"
    def generate_dielist(self):return Boss.generate_dielist()
    def generate_sprite(self): return "boss_hairy"
class bossGreasy(Boss):
    def generate_atklist(self): return ["atkwall", "atkblast", "atkbirth"]  # Bullet Wall Attacks
    def generate_idlelist(self): return ["idle1"]
    def generate_introtext(self): return "PRINCE NOPE\n   THE GREASY\nHE'S GETTING ZITTY"
    def generate_dielist(self):return Boss.generate_dielist()
    def generate_sprite(self): return "boss_greasy"
class bossBlue(Boss):
    def generate_atklist(self): return ["atkbeam", "atkswing", "atkcurve"]  # Beam Attacks
    def generate_idlelist(self): return ["idle2"]
    def generate_introtext(self): return "KING NOPE\n   THE BLUEST\nWHAT A STIBBITY!"
    def generate_dielist(self):return Boss.generate_dielist()
    def generate_sprite(self): return "boss_blue"
class bossGreen(Boss):
    def generate_atklist(self): return  ["atkhoriz", "atkjump", "atkwall"] # Horizontal Bullet Attacks
    def generate_idlelist(self): return ["idle1"]
    def generate_introtext(self): return "KING NOPE\n   THE GREENTH\nTHOSE WHO KNOW"
    def generate_dielist(self):return Boss.generate_dielist()
    def generate_sprite(self): return "boss_green"
class bossEww(Boss):
    def generate_atklist(self): return ["atkteleport", "atkperimeter", "atkspiral"] # Evasive and Teleporting Attacks
    def generate_idlelist(self): return ["idle4"]
    def generate_introtext(self): return "KING...\nEW...\n....EUGH...\nWHAT...\nGROSS.."
    def generate_dielist(self):return Boss.generate_dielist()
    def generate_sprite(self): return "boss_eww"
class bossFruity(Boss):
    def generate_atklist(self): return ["atkwall", "atkbounce", "atkspiral"]  # Dynamic Stage Control Attacks
    def generate_idlelist(self): return ["idle3"]
    def generate_introtext(self): return "KING NOPE\n   THE FRUITY\nKNIFE TO BEEF YOU."
    def generate_dielist(self):return Boss.generate_dielist()
    def generate_sprite(self): return "boss_fruity"
class bossUpsideDown(Boss):
    def generate_atklist(self): return ["atkchase", "atkslam", "atkfall"] # Chase and Close-Range Attacks
    def generate_idlelist(self): return ["idle1","idle2"]
    def generate_introtext(self): return "KING NOPE\n   THE UPSIDE DOWNST\nSTEEFRABBLEN"
    def generate_dielist(self):return Boss.generate_dielist()
    def generate_sprite(self): return "boss_king_upsidedown"
class bossBFDI(Boss):
    def generate_atklist(self): return ["atkperimeter", "atkjump", "atkhoriz"] # Position-Based Attacks
    def generate_idlelist(self): return ["idle1","idle3"]
    def generate_introtext(self): return "PRINCE NOPE\n   THE DEFORMED\nHE'S KINDA HOT THO...\n..."
    def generate_dielist(self):return Boss.generate_dielist()
    def generate_sprite(self): return "boss_bfdi"
class bossBald(Boss):
    def generate_atklist(self): return ["atkspasm", "atksine", "atkthrow"]  # Complex Bullet Spasms
    def generate_idlelist(self): return ["idle1","idle2"]
    def generate_introtext(self): return "KING NOPE\n   THE BALDTH\nOH.... OH.... OH... OH...\nOH.... OH... OH... OH...."
    def generate_dielist(self):return Boss.generate_dielist()
    def generate_sprite(self): return "boss_bald"
class bossHatter(Boss):
    def generate_atklist(self): return ["atkbeam", "atkspasm", "atkswing"] # Repetitive Fire Attacks
    def generate_idlelist(self): return ["idle1","idle2","idle3","idle4"]
    def generate_introtext(self): return "HATTER\nTHEY TOOK\n   EVERYTHING FROM ME.\nREDUCED TO A SIMPLE\n   USELESS BOSS\nHELP ME."
    def generate_dielist(self):return Boss.generate_dielist()
    def generate_sprite(self): return "boss_hatter"
class bossLarry(Boss):
    def generate_atklist(self): return ["atkspasm", "atkfall", "atksine"]  # Wave-like Attacks
    def generate_idlelist(self): return ["idle2"]
    def generate_introtext(self): return "TRY NOT TO GET SCARED\nSCARIEST STORIES\nGOD DOES NOT LIVE IN FEAR\nOF WHAT HE CREATED\nHE HIDES IN FEAR OF\n...\n...\nLARRY"
    def generate_dielist(self):return Boss.generate_dielist()
    def generate_sprite(self): return "boss_larry"
class bossEXE(Boss):
    def generate_atklist(self): return ["atkslam", "atkfall", "atkspasm"] # Melee and Close Combat Attacks
    def generate_idlelist(self): return ["idle4"]
    def generate_introtext(self): return "SO MANY SOULS TO....\nSOULS TO\nUH...\nSHAMMALAMMA\nDING DONG\n HEEEEEEHEEEEEEEEEEEE\nWAHOO YABBABFJSADHKFJASHDFKIASJ"
    def generate_dielist(self):return Boss.generate_dielist()
    def generate_sprite(self): return "boss_exe"
class INeedYou(Boss):
    def generate_atklist(self): return Boss.allatk[:] # Melee and Close Combat Attacks
    def generate_idlelist(self): return Boss.allidle[:]
    def generate_introtext(self): 
        return random.choice([
            "I need you.",
            "You make me\nSo Happy\nSo So Happy\nPlease come here."
            "Do you remember\nAll the time\nWe spent Together?",
            "I still love you.",
            "Please come back to me\nDon't you love me?",
            "You can't just\nLeave your own\nkind Like this",
    ])
    def generate_dielist(self):return Boss.generate_dielist()
    def generate_sprite(self): return "boss_you"




loaded = {
    "bossbig":bossBig,
    "bossking1":bossKing1,
    "bossking2": bossKing2 ,
    "bossbaby": bossBaby ,
    "bosshairy": bossHairy ,
    "bossgreasy": bossGreasy ,
    "bossblue": bossBlue ,
    "bossgreen": bossGreen ,
    "bosseww": bossEww ,
    "bossfruity": bossFruity ,
    "bossupsidedown": bossUpsideDown ,
    "bossbfdi": bossBFDI ,
    "bossbald": bossBald ,
    "bosshatter": bossHatter ,
    "bosslarry": bossLarry ,
    "bossexe": bossEXE ,
    "bossineedyou":INeedYou,
}










######### BOSS ASSETS THAT ARE USED ON OTHER MOVES


# the explosion
def make_explosion(coord:list,group:pygame.sprite.Group):
    spr = Em("kaboom",coord=coord,isCenter=True,animation_killonloop=True)
    group.add(spr)


# bullets that move down with momentum.
class Rain(pygame.sprite.Sprite):
    def __init__(self,pos:tuple,bottom:int=None,acceleration:float=None,terminal:float=None):
        pygame.sprite.Sprite.__init__(self)
        self.aimg = AImg(host=self,name="bullet_def")
        self.rect.center = pos
        self.momentum = 0
        if acceleration == None:
            self.acceleration = random.uniform(0.025,0.15)
        else:
            self.acceleration = acceleration
        if terminal == None:
            self.terminal = random.randint(2,5)
        else:
            self.terminal = terminal
        # self.bottom = bottom

        # bullet info
        self.health = 1

    def update(self):
        # updating aimg
        self.aimg.update()

        # updating the momentum unless it's reached max speed
        self.momentum += self.acceleration
        if self.momentum > self.terminal:
            self.momentum = self.terminal
        self.rect.y += self.momentum

        # print(self.rect.center)

        # kill code
        if not bullets.BulletRAW.on_screen(self) or self.health <= 0: 
            self.kill()
            # print('i dead')
        

    def on_collide(self,collide_type,collided):
        #5/26/23 - This is usually explained elsewhere
        #collision with enemy types
        if type(collided) == Player:
            self.hurt()
            collided.hurt()
    
    def hurt(self):
        self.health -= 1


# bullets that move outwards at an angle, and then home towards the player
class SwingBullet(pygame.sprite.Sprite):
    def __init__(self,pos:tuple,player:Player):
        pygame.sprite.Sprite.__init__(self)
        self.aimg = AImg(host=self,name="bullet_def")
        self.rect.center = pos
        self.phase = 0
        self.ap = tools.AnglePoint(pointA = pos, angle = random.randint(0,360), speed = 5, static_speed = False)
        self.mp = None # none yet, since it needs a current position which it does not have yet :3
        self.player = player
        self.health = 1

    def update(self):
        self.aimg.update()
        match self.phase:
            # in phase 0, the bullet moves out in a random angle until the momentum stops
            case 0:
                if self.ap.speed > 1:
                    # slowing down to a halt
                    self.ap.update()
                    self.rect.center = self.ap.position
                    self.ap.speed *= 0.95
                else:
                    # preparing for phase 1
                    self.mp = tools.MovingPoint(pointA = self.rect.center, pointB = self.player.rect.center,speed=20)
                    self.phase = 1
            # in phase 1, the bullet homes in towards the player and launches quickly
            case 1:
                self.mp.update()
                self.rect.center = self.mp.position

        # kill code -- always running
        if not bullets.BulletRAW.on_screen(self) or self.health <= 0: 
            self.kill()
    
    # the same on-collode / hurt stuff that exists in every single sprite aaagh
    def on_collide(self,collide_type,collided):
        if type(collided) == Player:
            self.hurt()
            collided.hurt()
    def hurt(self):
        self.health -= 1


# a clone of Enemy A, which only goes dowqn and does nothing after that
class BirthEnemyA(pygame.sprite.Sprite):
    def __init__(self,pos:tuple,player):
        pygame.sprite.Sprite.__init__(self)
        self.aimg = AImg(host=self,name="nope_A",current_anim="attack")
        print(pos)
        self.rect.center = pos
        self.centerx = pos[0]
        # this goes in the form of the sine shape 
        self.xspd = random.randint(10,40)
        self.yspd = random.randint(3,5)
        self.xrange = random.randint(30,60)
        # life
        self.life = 0
        self.health = 1
        
    
    def update(self):
        self.aimg.update() 
        self.life += 1
        # positioning
        self.rect.centerx = self.centerx + (math.sin(self.life/self.xspd)*self.xrange)
        self.rect.y += self.yspd
    
   # the same on-collode / hurt stuff that exists in every single sprite aaagh
    def on_collide(self,collide_type,collided):
        if type(collided) == Player:
            self.hurt()
            collided.hurt()
        elif collide_type == 1:
            #I SAID damaging the enemy either way
            self.hurt()
            collided.hurt()
    def hurt(self):
        self.health -= 1
        if self.health <= 0:
            self.kill()

class BirthEnemyB(BirthEnemyA):
    def __init__(self,pos,player):
        # base info
        pygame.sprite.Sprite.__init__(self)
        self.aimg = AImg(host=self,name="nope_B",current_anim="attack")
        self.life = 0
        self.health = 1
        # specific info
        self.player = player
        self.rect.center = pos
        self.mp = tools.MovingPoint(pointA = self.rect.center,pointB = self.player.pos,speed = 10,ignore_speed = True)
    
    def update(self):
        self.aimg.update()
        self.life += 1
        # mp information
        self.mp.update()
        self.rect.center = self.mp.position
        if self.mp.speed > 1:
            self.mp.speed *= 0.95
        else:
            # new mp!
            self.mp = tools.MovingPoint(pointA = self.rect.center,pointB = self.player.pos,speed = 10,ignore_speed = True)

class BirthEnemyC(BirthEnemyA):
    def __init__(self,pos,player):
        # base info
        pygame.sprite.Sprite.__init__(self)
        self.aimg = AImg(host=self,name="nope_C",current_anim="idle")
        self.life = 0
        self.health = 1
        self.rect.center = pos
        self.player = player
        # making an intro mp
        self.mp = tools.MovingPoint(pointA = self.rect.center,pointB = (random.randint(50,pygame.display.play_dimensions[0]-50),random.randint(50,pygame.display.play_dimensions[0]//4)),speed=10,ignore_speed=True)
    
    def update(self):
        self.life += 1
        self.aimg.update()
        # mp information
        self.rect.center = self.mp.position
        if not self.mp.finished:
            self.mp.update()
            if self.mp.speed > 1:
                self.mp.speed *= 0.95
            else:
                self.mp.finished = True
        # shoot information
        if self.life % 60 == 0:
            self.shoot()
    
    def shoot(self):
        bullet = bullets.HurtBullet(type="point",spd=5,info=(self.rect.center,self.player.rect.center),texture="bullet_def")
        # self.sprites[0].add(bullet)
        self.player.sprite_groups[2].add(bullet)
        return bullet