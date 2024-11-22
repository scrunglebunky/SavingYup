import pygame,os,player,text,random,formation,anim,audio,tools,events,score,enemies,enemies_bosses
from anim import all_loaded_images as img
from anim import WhiteFlash
from text import display_numbers as dn
from text import text_list as tl
from backgrounds import Background as Bg
from backgrounds import Floor as Fl
from emblems import Emblem as Em
from bullets import emptyBulletMax as eBM
from bullets import BulletParticle as BP
from math import sin
from player import PlayerDummy as PD
from levels import worlds 
from events import GamePlayInfo as GPI

winrect = pygame.display.rect
height,width = winrect.height,winrect.width
starty = winrect.height * 0.25



#basic template for states to go off of
class Template():
    def __init__(self):
        self.next_state = None #Needed to determine if a state is complete
    def update(self):
        ...
    def on_start(self):
        ...
    def on_end(self):
        ...
    def event_handler(self,event):
        ...
    def kaboom(self,group:pygame.sprite.Group,coord:tuple,animation_resize:tuple,play:bool=False,): #because kaboom happens so much
            group.add(
            Em(
                im='kaboom',
                coord=coord,
                isCenter=True,
                animation_killonloop=True,
                resize=animation_resize
                ))





#UPDATED GAMEPLAY
class Play(Template):
    sprites = { #sprites are now state-specific hahaha
            0:pygame.sprite.Group(), #ALL SPRITES
            1:pygame.sprite.Group(), #PLAYER SPRITE, INCLUDING BULLETS ; this is because the player interacts with enemies the same way as bullets
            2:pygame.sprite.Group(), #ENEMY SPRITES
            3:pygame.sprite.Group(), #UI SPRITES
        }
    



    def __init__(self,
                 window:pygame.display,
                 level:int = 0,
                 #is_demo:bool=False, #a way to check if the player is simulated or not
                 ):

        self.sprites = Play.sprites

        self.next_state = None #Needed to determine if a state is complete
        self.fullwindow = window

        self.debug = {0:[],1:[]}
        #self.is_demo = is_demo


        #resetting the sprite groups
        for group in self.sprites.values():
            group.empty()

        #06/23/2023 - SETTING THE GAMEPLAY WINDOW
        # YUP has a touhou-like border surrounding the entire game as it works
        # Because of this, gameplay will have its own entire tiny display to work with 
        # It still saves the original pygame window, but this is just to draw the display to.abs
        self.window = pygame.Surface(pygame.display.play_dimensions).convert_alpha()

        #Player movement info
        self.bar = ( #the field the player is able to move along
            "h", #if the bar is horizontal or vertical.
            pygame.display.play_dimensions[1]*0.90, #x position if vertical, y position if horizontal.
            (20,pygame.display.play_dimensions[0]-20), #the limits on both sides for the player to move on, y positions if vertical, x positions if horizontal
            1, #gravity. 
            )
            
        self.player = player.Player(bar=self.bar,sprite_groups=self.sprites)
        self.sprites[1].add(self.player)









        #06/01/2023 - Loading in level data -- NOT ANYMORE!!
        # self.campaign = campaign
        # self.world = world
        self.level = 0 #the total amount of levels passed, usually used for intensities or score
        self.difficulty = 1 + self.level / 5

        # world data is now handled here, in code, since it updates manually
        # self.world_data = Play.default_world_data


        # current running game info, which replaces world data
        # this isn't a dictionary anymore because they're annoying to write
        self.char_list = [] 
        self.char_start_patterns = {}
        self.backgroundlist_unlocked = []
        #unlocking new character/background
        GPI.unlock_enemy(playstate=self)
        GPI.unlock_bg(playstate=self)
        #06/01/2023 - loading the formation
        #the formation handles spawning and management of most enemies, but the state manages drawing them to the window and updating them
        self.new_formation()
        # self.new_bg("bg01") # now set by GPI

        #timer for updating new level
        self.leveltimer = 0 

        #needed to stop error - FIX LATER
        self.curBossName = "ufo"

    
    def update(self, draw=True):
        #Drawing previous gameplay frame to the window -- don't ask why, it just does. 
        if draw: self.fullwindow.blit(pygame.transform.scale(self.window,pygame.display.play_dimensions_resize),pygame.display.play_pos)


        #Updating backgrounds - drawing to window
        self.background.update()
        self.background.draw(self.window)
        if self.floor is not None:
            self.floor.update()
            self.floor.draw(self.window)
        # self.formation.draw_img(window=self.window) #displaying a special formation image if necessary


        #updating all individual sprites, with the fourth group having special priority.
        self.sprites[0].update()
        self.sprites[1].update()
        self.sprites[2].update()
        self.sprites[0].draw(self.window)
        self.sprites[1].draw(self.window)
        self.sprites[2].draw(self.window)



        #ending function early if event playing
        # if self.event is not None and self.event.playing:
        #     self.event.update()
        #     return


        #only updating the formation after checking for events, to prevent the level starting beforehand.
        self.formation.update()

        #print debug positions
        # for pos in self.debug[0]:
            # self.window.blit(pygame.transform.scale(img["placeholder.bmp"],(10,10)),pos)
        
        #calling collision
        self.collision()
        

        
        # DEMO PURPOSES -- CHANGE LATER!!! 
        if self.formation.cleared and self.leveltimer > 180:
            self.new_level()

        #updating the wait timer
        elif self.formation.cleared:
            self.leveltimer += 1
        
        #08/21/2023 - Game Over - opening a new state if the player is dead
        if self.player.health <= 0:
            self.next_state = "gameover"



    
    def on_start(self,**kwargs):#__init__ v2, pretty much.
        #06/24/2023 - Playing the song
        audio.play_song("kurosaki.mp3")
        self.player.sprite_groups = self.sprites
        eBM()



    def on_end(self,**kwargs): #un-init, kind of
        pygame.mixer.music.stop()
        if tools.debug: print(self.debug.values())
        eBM()






    def collision(self):
        #Detecting collision between players and enemies 
        collidelist=pygame.sprite.groupcollide(self.sprites[1],self.sprites[2],False,False,collided=pygame.sprite.collide_mask)
        for key,value in collidelist.items():
            for item in value:
                key.on_collide(2,item)
                item.on_collide(1,key)



    
    def new_formation(self):
        self.formation = formation.Formation(
            player = self.player,
            # world_data = self.world_data,
            char_list=self.char_list,
            start_patterns=self.char_start_patterns,
            level=self.level,
            difficulty=self.difficulty,
            sprites=self.sprites,
            window=self.window,
            #is_demo = self.is_demo
            )



        

    def new_bg(self,bg="bg01",transition_effect:bool=False):
        #06/03/2023 - Loading in the background
        self.background = Bg(bg, resize = (600,800), speed = (0,0))
        # also loading in the floor if it exists
        self.floor = Fl(
            image='floor-default',
            player=self.player,
            window=self.window,
            move=(.25,.25),
            scale=(800,800)
            ) 
        # print(self.floor.image, self.floor.rect.center, self.floor.hide)

    def new_zone(self):
        # new zone code
        GPI.unlock_enemy(playstate=self)
        GPI.unlock_bg(playstate=self)

        
    
    def new_level(self):
        # updating level and difficulty info
        self.level += 1
        self.difficulty = 1 + self.level / 5        
        self.formation.empty()
        # TEST FOR DEMO
        # self.new_zone()
            
        #restarting the formation
        self.new_formation()

        #resetting the level timer
        self.leveltimer = 0 

        if self.level%5 == 0 or self.level in (1,2,3):
            self.new_zone()

    def event_handler(self,event):
        #if self.is_demo: return
        self.player.controls(event)
        #changing what comes next
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.next_state = "pause"
            if tools.debug: 
                ...
        if event.type == pygame.MOUSEBUTTONDOWN and tools.debug:
            pos = tuple(pygame.mouse.get_pos())
            pos = [pos[0]-pygame.display.play_pos[0],pos[1]-pygame.display.play_pos[0]]
            pos2 = [pygame.display.play_dimensions_resize[0]-pos[0],pos[1]]
            self.debug[0].append(pos)
            self.debug[1].append(pos2)
            print(pos,pos2)








#title screen
class Title(Template):
    emblems = {}
    emblems_perm = {}
    sprites=pygame.sprite.Group()
    em_continue = Em(im='continue')

    def __init__(self,window:pygame.Surface,border): #Remember init is run only once, ever.
        self.window=window
        self.border=border
        self.next_state = None
        

        #self.demo_state = Play(window = self.window, world = 1, level = random.randint(0,50), is_demo = True) #this is different from the tools.demo value, as this is just to simulate a player
        self.hiscoresheet = score.generate_scoreboard()

        #basic events that will occur during the title
        self.events = [
            "hiscore",
        ]
        self.event = 0
        self.timer = 0
        self.resize = [(winrect.width * 0.4) , 800 * ((winrect.width*0.4)/600)]
        if self.resize[0] > 600:
            self.resize = [600,800]
        self.image_placements = {}
            # "welcome":(pygame.display.rect.width*0.01,pygame.display.rect.height*0.01),
        #self.image_placements["demo"] = (pygame.display.rect.width*0.01,pygame.display.rect.height*0.1)
        self.image_placements["score"] = (pygame.display.rect.width*0.99 - self.resize[0] ,pygame.display.rect.height*0.1)
        Title.em_continue.change_pos((winrect.centerx,winrect.centery),isCenter=True)

        self.hiscoresheet = pygame.transform.scale(self.hiscoresheet,self.resize)
        
    
    
    def on_start(self):
        self.event = self.id = 0
        #self.demo_state.__init__(window = self.window, world = 1, level = random.randint(0,50), is_demo = True)
        self.border.emblems['logo'].add_tween_pos(cur_pos = self.border.emblems['logo'].rect.center , target_pos = (winrect.centerx,winrect.height*0.25),speed=5,started=True,isCenter=True)
        self.border.change_vis(lives=True,score=True,debug=True,weapon=True)

    def on_end(self):
        self.border.emblems['logo'].add_tween_pos(cur_pos = self.border.emblems['logo'].rect.topleft , target_pos = self.border.emblems['logo'].orig_coord  ,speed=5,started=True,isCenter=False)
        self.border.change_vis(lives=False,score=False,debug=False,weapon=False)


    def update(self):
        
        #drawing
        # self.window.blit(img['demo.png'],self.image_placements['welcome'])
        
        #demo
        #updating and drawing
        Title.em_continue.update()
        self.window.blit(Title.em_continue.image,Title.em_continue.rect)
        #self.demo_state.update(draw=False)
        #self.window.blit(pygame.transform.scale(self.demo_state.window,self.resize),self.image_placements['demo'])
        self.window.blit(self.hiscoresheet,self.image_placements['score'])
         ###### demo player controls
        # event = pygame.event.Event(random.choice([pygame.KEYDOWN,pygame.KEYUP]), key = random.choice([pygame.K_UP,pygame.K_DOWN,pygame.K_LEFT,pygame.K_RIGHT,pygame.K_z,pygame.K_x])) #create the event        
        # #stopping constant movement
        # if event.type == pygame.KEYDOWN and (event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT):
        #     self.demo_state.player.move(dir=event.key == pygame.K_RIGHT,release=True)
        # else: self.demo_state.player.controls(event)

        #timer updating
        self.timer += 1
        if self.timer > 360:
            self.event = self.event + 1 if self.event + 1 < len(self.events) else 0
            self.timer = 0 
            



        


    def event_handler(self,event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_z:
                self.next_state = "play" #no longer tutorial
            if event.key == pygame.K_ESCAPE:
                self.next_state = "quit"





# 08/08/2023 - THE GAME OVER STATE
# The game over state will use the gameplay state and modify it so everything slows down and the assets disappear and a graphic shows
class GameOver(Template):
    sprites=pygame.sprite.Group()
    def __init__(self,window,play_state):
        #08/08/2023 - PSEUDOCODE 
        # Remember, playstate has a separate surface that is drawn to the window, again, entirely separately. 
        # GameOverState will, animated-ly, blow up everything onscreen, then make the surface do a falling animation.
        # The separate surface is ignored from there on out. A game over graphic appears, which shows your score and how you did, before giving a rating.
        # Pressing enter brings you back to the main menu.
        self.next_state = None
        self.window = window
        self.play_state = play_state
        self.bg_multiplier = 0
        #timers
        self.timer = 0 #timer measurement
        self.events = [            
            120, #time until screen explodes
            360, #time until everything stops exploding, and shows your score
            1200, #time until high score is shown
            1500, #finishing high score
        ]
        self.events_func = [
            self.event0,
            self.event1,
            self.event2,
            self.event3,
            self.event4
        ]
        self.state = 0

        #event 1 explosion
        self.event1_ = [
            0, #angle transform
            0, #y momentum
            0, #y 
        ]

        #game over background
        self.background = Bg(img = "game_over_bg.png" , resize = [pygame.display.rect.width,pygame.display.rect.height], speed=[1.25,1], border_size=pygame.display.dimensions)        
        
        #needed to check for exit input
        self.exit_ok:bool = False

        #high score information
        self.name=""
        self.scoregraphic=Em(force_surf=score.generate_graphic(score.score,""),coord=(0,0),isCenter=True)

    def on_start(self):
        #kabooming the player 
        self.kaboom(coord=self.play_state.player.rect.center,animation_resize=(150,150),play=True)
        self.play_state.formation.start_state_leave()
        self.play_state.background.speed[1] *= 3
        self.bg_multiplier = self.play_state.background.speed[1] * 0.1
        



    def on_end(self):
        pygame.mixer.music.stop()

    def update(self):
        self.events_func[self.state]() #running each function

        #update the timer
        self.timer += 1
        if self.state<len(self.events) and self.timer >= self.events[self.state]:
            self.state += 1

        #updating any used sprites
        GameOver.sprites.update()
        GameOver.sprites.draw(self.window )


    def event0(self): #SLOWING EVERYTHING DOWN
        #the first state, which slows everything down
        #updating current state
        self.play_state.update()
        #changing bg
        self.play_state.background.speed[1] -= self.bg_multiplier
        self.bg_multiplier *= 1.025
    
    def event1(self): #BLOWING EVERYTHING UP
        if self.timer == 121: audio.play_song("gameover.mp3")
        self.play_state.update(draw=False)

        #shaking
        if self.timer < 180:
            self.window.blit(
                pygame.transform.scale(
                    self.play_state.window,pygame.display.play_dimensions_resize),
                    (pygame.display.play_pos[0]*random.uniform(0.7,1.3),pygame.display.play_pos[1]*random.uniform(0.7,1.3))
                    )
            if self.timer % 2 == 0:
                self.kaboom(animation_resize=(150,150),coord=(random.randint(0,pygame.display.dimensions[0]),random.randint(0,pygame.display.dimensions[1])))
    
        #Big explosion
        elif self.timer < 360:
            if self.timer == 181:
                self.event1_[1] = -30
                self.kaboom(
                    coord=(
                        pygame.display.play_pos[0]+(pygame.display.play_dimensions[0]/2),
                        pygame.display.play_pos[1]+(pygame.display.play_dimensions[1]/2)
                        ),animation_resize=(500,500))
                
            self.event1_[1] += 0.75
            self.event1_[2] += self.event1_[1]
            self.event1_[0] -= 1
            #falling window
            self.window.blit(
                pygame.transform.rotate(
                    pygame.transform.scale(self.play_state.window,pygame.display.play_dimensions_resize),
                    self.event1_[0]),
                (
                    pygame.display.play_pos[0],
                    (pygame.display.play_pos[1])+self.event1_[2])
                    )
            
            #kabooms
            if self.timer == 330 or self.timer == 340:
                self.kaboom(coord=(random.randint(0,pygame.display.dimensions[0]),random.randint(0,pygame.display.dimensions[1])),animation_resize=(random.randint(500,1000),random.randint(500,1000)))
            elif self.timer == 350:
                self.kaboom(coord=pygame.display.rect.center,animation_resize=(3000,3000))
            
            


    def event2(self):
        self.background.update()
        self.background.draw(window=self.window)

        #spawning in the game over logo
        if self.timer == 400:
            GameOver.sprites.add(Em(im="gameover.png",coord=(pygame.display.rect.center[0]*0.35,pygame.display.rect.center[1]*0.30),isCenter=True))
        #icons
        if self.timer == 500:
            GameOver.sprites.add(Em(im="gameover_score.png",coord=(pygame.display.rect.center[0]*0.35,pygame.display.rect.height*0.35),isCenter=True))
        if self.timer == 650:
            GameOver.sprites.add(Em(im="g_level.png",coord=(pygame.display.rect.center[0]*0.35,pygame.display.rect.height*0.45),isCenter=True))
        if self.timer == 800:
            GameOver.sprites.add(Em(im="g_rank.png",coord=(pygame.display.rect.center[0]*0.35,pygame.display.rect.height*0.90),isCenter=True))
        #numbers
        if self.timer == 530:
            GameOver.sprites.add(Em(force_surf = text.load_text(text=str(score.score),size=40) ,coord=(pygame.display.rect.center[0]*0.75,pygame.display.rect.height*0.32),isCenter=False))
        if self.timer == 680:
            GameOver.sprites.add(Em(force_surf = text.load_text(text=str(self.play_state.level),size=40),coord=(pygame.display.rect.center[0]*0.75,pygame.display.rect.height*0.42),isCenter=False,))
        #rank
        if self.timer == 830:
            GameOver.sprites.add(Em(force_surf = text.load_text(text=self.generate_rank(),size=40),coord=(pygame.display.rect.center[0],pygame.display.rect.height*0.90),isCenter=True,))
        
        #either high score screen or telling game to kill itself
        if self.timer == 1000:
            if self.got_high_score():
                self.timer = 1200
                GameOver.sprites.empty()
                self.kaboom(coord=pygame.display.rect.center,animation_resize=(3000,3000))
                return
            else:
                sp = Em(im="gameover_return.png",coord=(pygame.display.rect.width*0.75,pygame.display.rect.center[1]),isCenter=True)
                sp.pattern="sine"
                GameOver.sprites.add(sp)
                self.exit_ok = True

        if self.timer > 1190:
            self.timer = 1001
        


    def event3(self):
        self.background.update()
        self.background.draw(window=self.window)

        if self.timer == 1201:
            #speeding up bg
            self.background.speed=[-7,-7]
            #high score image 
            sp = Em(im="hiscore.png",coord=(pygame.display.rect.center[0]*0.35,pygame.display.rect.center[1]*0.30),isCenter=True)
            sp.pattern = "jagged";GameOver.sprites.add(sp)
        if self.timer == 1260:
            #showing the high scores, showing yours, and telling you to input
            GameOver.sprites.add(
                Em(force_surf=score.scoreboard,coord=(pygame.display.rect.width*0.75,pygame.display.rect.height*0.5),isCenter=True)
            )
            #scoregraphic
            GameOver.sprites.add(self.scoregraphic)
            self.scoregraphic.change_pos(pos=(pygame.display.rect.width*0.25,pygame.display.rect.height*0.4),isCenter=True)
            #telling you
            x = Em(im="hiscore_name.png",coord=(pygame.display.rect.width*0.25,pygame.display.rect.height*0.5),isCenter=True) ; x.pattern = "sine"
            GameOver.sprites.add(x)
        #stopping it from advancing if you don't enter your name in time
        if self.timer >= 1490 and self.timer < 1500: self.timer = 1300

    
    def event4(self):
        if self.timer == 1501:
            GameOver.sprites.empty()
            self.kaboom(coord=pygame.display.rect.center,animation_resize=(1000,1000))
            #updating the new scoreboard
            score.scores = score.add_score(score=score.score,name=self.name,scores=score.scores)
            score.scoreboard = score.generate_scoreboard()
            GameOver.sprites.add(Em(force_surf=score.scoreboard,coord=pygame.display.rect.center,isCenter=True))

        if self.timer >= 1740:
            self.finish()

    def event_handler(self,event):
        if event.type == pygame.KEYDOWN:
            if (event.key == pygame.K_z or event.key == pygame.K_x) and (self.exit_ok):
                self.finish()
            if self.state == 3:
                if event.key == pygame.K_BACKSPACE:
                    self.hiscore_updatename(backspace=True)
                elif event.key == pygame.K_RETURN:
                    self.timer = 1500 #finishing it all off
                else:
                    self.hiscore_updatename(pygame.key.name(event.key))



    def generate_rank(self) -> str:
        #makes a rank value and gives you a set of ranks based off of it
        rank_val = score.score * (1+(0.01*self.play_state.level))
        ranks = {
            0:"joke", #joke 
            100:"horrible", #horrible
            500:"bad", #bad
            1000:"notgood", #not good
            2500:"mid", #mid
            5000:"ok", #ok
            10000:"good", #good 
            25000:"great", #great (shitpost)
            50000:"amazing", #amazing
            100000:"cracked", #cracked 1
            250000:"crackeder", #cracked 2
            500000:"crackedest", #cracked 3
            1000000:"holymoly" #holy hell
        }
        #figuring out what rank to put you into
        rank_key=None
        for val in ranks.keys():
            if rank_val >= val:
                rank_key = int(val)
            else:
                break
        #giving the rank
        rank = random.choice(tl["rank_" + str(ranks[rank_key])])
        return rank

    def got_high_score(self) -> bool: #it says if you got a high score or not
        return (score.score > score.scores[0][1]) or (len(score.scores)<10)


    def hiscore_updatename(self,text:str="",backspace:bool=False):
        if backspace and len(self.name) > 0: 
            tempname = list(self.name)
            tempname[len(tempname)-1] = ''
            self.name = ''
            self.name.join(tempname)
        else: self.name += (text.upper() if text.upper() != "SPACE" else " ")
        self.scoregraphic.aimg.image = score.generate_graphic(score.score,self.name)



        
    def kaboom(self,coord:tuple,animation_resize:tuple,play:bool=False,): #because kaboom happens so much
            (GameOver.sprites if not play else self.play_state.sprites[0]).add(
            Em(
                im="kaboom",
                coord=coord,
                isCenter=True,
                animation_killonloop=True,
                resize=animation_resize
                ))

    def finish(self):
        #the finishing part
        GameOver.sprites.empty()
        score.score = 0
        self.play_state.__init__(
            window=self.play_state.fullwindow,
        )
        self.__init__(window=self.window,play_state=self.play_state)
        score.save_scores(scores=score.scores)
        self.next_state="title"





#paused
class Pause(Template):
    def __init__(self,window:pygame.Surface,play_state):
        
        self.next_state = None #Needed to determine if a state is complete
        self.return_state = "play"
        self.play_state = play_state
        self.window = window
        self.bg = play_state.window
        self.logo_pos:list = [0,0] #[frames_in,y_pos] 
        self.bgpos = pygame.display.play_pos[0] + 35 , pygame.display.play_pos[1] + 38

    def on_start(self,**kwargs): #__init__ v2, pretty much.
        audio.play_song("kurosaki.mp3")
        if 'return_state' in kwargs.keys(): self.return_state = kwargs['return_state']
    def on_end(self,**kwargs): #un-init, kind of
        pygame.mixer.music.stop()

    def update(self):
        #displaying of all the pause graphics and such - likely heavily unoptimized.
        self.bg.blit(img["paused.png"],(0,0))
        self.bg.blit(img["paused.png"],(0,600))
        self.window.blit(pygame.transform.scale(img["pauseborder.png"],pygame.display.play_dimensions_resize),pygame.display.play_pos)
        self.window.blit(pygame.transform.scale(self.bg,(390,270)),self.bgpos)

    def event_handler(self,event):
        #changing what comes next
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                self.next_state = "options","pause"
            if event.key == pygame.K_q:
                self.next_state = "title"
                self.play_state.__init__(
                    window=self.play_state.fullwindow,
                )
            if event.key == pygame.K_ESCAPE:
                self.next_state = self.return_state





#when a world is completed
class Advance(Template):
    sprites=pygame.sprite.Group()

    emblems = {
        "score":Em(im="g_score.png",coord=(0,starty+height*0)),
        "lives":Em(im="g_lives.png",coord=(0,starty+height*0.1)),
        "shots":Em(im="g_shots.png",coord=(0,starty+height*0.2)),
        "kills":Em(im="g_kills.png",coord=(0,starty+height*0.3)),
        "accuracy":Em(im="g_accuracy.png",coord=(0,starty+height*0.4)),
        "rank":Em(im="g_rank.png",coord=(0,height*0.9)),
    }
    emblemkeys = list(emblems.keys())
    values = {"score":0,"lives":0,"shots":0,"kills":0,"accuracy":0,"rank":"hello"}
    suffix = {"score":0,"lives":10,"shots":0.25,"kills":1,"accuracy":1000,"rank":0}
    


    def __init__(self,window,play_state):
        #setting values
        self.window = window
        self.play_state = play_state
        self.next_state = None
        #phases
        self.phases = (self.phase0,self.phase1,self.phase2,self.phase3)
        """ PHASE LIST
        0 - the background slowly fading in
        1 - "LEVEL COMPLETE" hitting the screen
        2 - A list of certain things that have occurred: killed enemies, damage taken, shots fired, accuracy
        X - Saying where you are going, with a scaled-down picture of the background. 
        3 - Playing a random animation that launches the player offscreen"""
        #defining a bunch of values elsewhere
        self.initialize_values()   

        
    def on_start(self):
        #advancing the world early in playstate so the right info is fetched
        # self.play_state.new_world()
        #player
        self.play_state.player.movement_redo()
        self.play_state.player.bullet_lock = True
        #defining values
        self.initialize_values()
        self.fetch_numbers() #copying the world logs
        tools.update_log() #resetting the world logs to 0 
        #player stuff -> state stuff
        self.play_state.player.aimg.change_anim("yay")
        self.play_state.player.reset_movement()
        self.play_state.in_advance = True #stopping play_state from doing weird shit


    def on_end(self):
        
        self.frames = self.counter1 = self.phase = 0
        self.play_state.player.aimg.change_anim("idle")
        self.play_state.player.bullet_lock = False
        self.play_state.in_advance = False #letting play_state be goofy again
        self.sprites.empty


    def update(self):
        Advance.values['score'] = score.score
        self.phases[self.phase]()
        return
        # self.frames += 1
        # self.frames==1: Advance.sprites.add(Em(im="levelcomplete.png",coord=(pygame.display.play_dimensions_resize[0]/2+pygame.display.play_pos[0],pygame.display.play_dimensions_resize[1]*0.25+pygame.display.play_pos[1]),isCenter=True,pattern="jagged"))
        # #changing the play_state stored world
        # if self.frames == 150:
        #     Advance.sprites.empty()
        #     self.play_state.new_world()
        #     self.kaboom(
        #         coord=(pygame.display.play_dimensions_resize[0]/2+pygame.display.play_pos[0],pygame.display.play_dimensions_resize[1]/2+pygame.display.play_pos[1]),
        #         animation_resize=(500,500))
        # #ending
        # if self.frames > 300:
        #     self.next_state = "play"


    def phase0(self):
        self.counter1 += 1
        #updating the background
        self.bgFlash.update()
        self.bg.update()
        self.bg.image = self.bgFlash.image
        self.playstate_draw()
        #drawing values in order
        self.bg.draw(self.window)
        self.window.blit(pygame.transform.scale(self.play_state.window,pygame.display.play_dimensions_resize),pygame.display.play_pos)
        #checking to finish
        if self.counter1 > 255 or (type(self.bg) == WhiteFlash and self.bg.finished):
            self.phase = 1
            self.counter1 = 0 
            self.bg = Bg(img="level_complete_bg.png",resize=pygame.display.dimensions,speed=[-5,-5])
            self.em_complete.add_tween_pos(cur_pos = (winrect.centerx,-50), target_pos = (winrect.centerx,100), speed=2, started=True, isCenter=True)
            self.sprites.add(self.em_complete)

    def phase1(self):

        #updating the other generic stuff -- player background timer
        self.counter1 += 1
        self.bg.update()
        self.sprites.update()
        self.playstate_draw()
        self.bg.draw(self.window)
        self.window.blit(pygame.transform.scale(self.play_state.window,pygame.display.play_dimensions_resize),pygame.display.play_pos)
        self.sprites.draw(self.window)
        #displaying emblem numbers
        self.draw_numbers()
        #adding emblems to the screen
        if self.counter1 > 45 and self.state1_counter < len(Advance.emblemkeys):
            self.sprites.add(Advance.emblems[Advance.emblemkeys[self.state1_counter]])
            # print(Advance.emblemkeys[self.state1_counter],Advance.emblems[Advance.emblemkeys[self.state1_counter]].rect.topleft)
            self.kaboom(coord=Advance.emblems[Advance.emblemkeys[self.state1_counter]].rect.center,animation_resize = (150,75))
            self.state1_counter += 1
            self.counter1 = 0 

        elif self.state1_counter >= len(Advance.emblemkeys) and self.counter1 > 255:
            self.phase = 2
            self.counter1 = 0


    def phase2(self):
        #updating the other generic stuff -- player background timer
        self.counter1 += 1
        self.bg.update()
        self.sprites.update()
        self.playstate_draw()
        self.bg.draw(self.window)
        self.window.blit(pygame.transform.scale(self.play_state.window,pygame.display.play_dimensions_resize),pygame.display.play_pos)
        self.sprites.draw(self.window)

        #subtracting values to add to score
        done = self.subtract_numbers()
        self.draw_numbers()

        #done
        if done:
            self.counter1 = 0
            self.phase = 3
            # self.sprites.add(self.em_nextlevel,self.em_movingto,self.em_nextleveltext,self.em_enemylog)



    """
    def phase3(self):
        #fade the background away
        self.bg.update()
        self.bg.draw(self.window)

        #updating the other generic stuff -- player background timer
        self.counter1 += 1
        self.sprites.update()
        self.playstate_draw()
        self.window.blit(pygame.transform.scale(self.play_state.window,pygame.display.play_dimensions_resize),pygame.display.play_pos)
        self.sprites.draw(self.window)
        self.draw_numbers()


        #waiting as the game says where the player is moving next
        if self.counter1 > 360:
            self.counter1 = 0
            self.phase = 4
    """


    def phase3(self):
        #fade the background away
        self.bgUnflash.update()
        self.bg.update()
        self.bg.image = self.bgUnflash.image
        self.bg.draw(self.window)

        #updating the other generic stuff -- player background timer
        self.counter1 += 1
        self.sprites.update()
        self.playstate_draw()
        self.window.blit(pygame.transform.scale(self.play_state.window,pygame.display.play_dimensions_resize),pygame.display.play_pos)
        self.sprites.draw(self.window)
        self.draw_numbers()

        #destroying all living assets
        if self.counter1 % 15 == 0:
            if len(self.sprites) <= 0: 
                pass
            else:
                for v in self.sprites:
                    if v.aimg.name == 'kaboom':break
                    self.kaboom(coord=v.rect.center,animation_resize=(v.rect.width,v.rect.height))
                    v.kill()
                    break

        #waiting as the game says where the player is moving next
        if self.counter1 > 150:
            self.next_state = "play"
    
   

    def event_handler(self,event):
        self.play_state.player.controls(event)    
    
    def kaboom(self,coord:tuple,animation_resize:tuple,play:bool=False,): #because kaboom happens so much
            (Advance.sprites if not play else self.play_state.sprites[0]).add(
            Em(
                im='kaboom',
                coord=coord,
                isCenter=True,
                animation_killonloop=True,
                resize=animation_resize
                ))
    
    def playstate_draw(self):
        #managing the player and the background
        self.play_state.sprites[1].update()
        self.play_state.window.fill(pygame.Color(0,0,0,0))
        self.play_state.sprites[1].draw(self.play_state.window)



    def initialize_values(self):
        #startup
        self.frames = 0 
        self.counter1 = 0 # a rapidly-resetting counter that does not measure the lifespan of the state
        self.phase = 0 # phase 0 -> player happy (everything stops) | phase 1 -> background settling in, 
        #fading bg assets
        self.bgFlash = WhiteFlash(img="level_complete_bg.png",surface=self.window,start_val=0,end_val=255,isreverse=True,spd=-2.0)
        self.bgUnflash = WhiteFlash(img="level_complete_bg.png",surface=self.window,spd=2.0)
        self.bg = Bg(img=None,resize=pygame.display.dimensions,speed=[-5,-5])
        self.bg.image = self.bgFlash.image
        #other assets
        self.em_complete = Em(im="levelcomplete.png",coord=(0,0))
        #self.em_nextlevel = Em(im=self.play_state.world_data['bg'],resize=(225,300),pattern="sine",coord=(winrect.width*0.75,winrect.centery),isCenter=True)
        # self.em_movingto = Em(im="a_movingto.png",pattern="jagged",coord=(self.em_nextlevel.rect.centerx,self.em_nextlevel.rect.top-25),isCenter=True)
        #self.em_nextleveltext = Em(force_surf = text.load_text(str(self.play_state.world_data['world_name']),50),pattern="jagged",coord=(self.em_nextlevel.rect.centerx,self.em_nextlevel.rect.bottom+25),isCenter=True)
        # self.em_enemylog = Em(force_surf = anim.generate_enemy_log(world_data=self.play_state.world_data), pattern = 'sine',  coord = (self.em_nextleveltext.rect.centerx,self.em_nextleveltext.rect.bottom), isCenter=True)
        # self.sprites.add(self.bg)
        
        #state 1 values -> emblems
        self.state1_counter = 0 


    def draw_numbers(self):
        for k,v in Advance.emblems.items():
            if k == "rank":
                continue
            elif v.alive():
                if k == "score": 
                    dn(str(Advance.values[k]), pos=v.rect.topright,window=self.window) 
                elif k == "accuracy":
                    dn(str(round(Advance.values[k]*100))+"%x"+str(Advance.suffix[k]), pos=v.rect.topright,window=self.window) 
                else:
                    dn(str(Advance.values[k])+"x"+str(Advance.suffix[k]), pos=v.rect.topright,window=self.window)

    def fetch_numbers(self):
        Advance.values['score'] = score.score
        Advance.values['lives'] = self.play_state.player.health
        Advance.values['kills'] = tools.world_log['hits'] #CGHANGE THIS SOON
        Advance.values['shots'] = tools.world_log['shots'] 
        if Advance.values['shots'] > 0:
            Advance.values['accuracy'] = Advance.values['kills']/Advance.values['shots'] 
        else:
            Advance.values['accuracy'] = 1.0

    def subtract_numbers(self) -> bool:
        snapped=subbed=False
        for k,v in Advance.emblems.items():
            if v.alive():
                if k == "score":
                    continue
                if k == "rank":
                    v.kill()
                    snapped = True
                    self.kaboom(coord=v.rect.center,animation_resize = (100,200))
                else:
                    if Advance.values[k] >= 1:
                        #if >= 1
                        score.score += round(Advance.suffix[k],2)
                        Advance.values[k] -= 1
                        subbed = True
                    elif Advance.values[k] > 0:
                        #if between 1 and 0 
                        score.score += round(Advance.suffix[k]*Advance.values[k],2)
                        Advance.values[k] = 0
                        subbed = True
                    else:
                        #if <= 0 
                        v.kill()
                        self.kaboom(coord=v.rect.center,animation_resize = (100,200))
                        snapped = True
                    score.score = round(score.score,2)
        if snapped:...
        if subbed:
            #play sound
            return False
        else:
            #done
            return True





#same as gameplay but there is now a boss involved
class Boss(Template):
    sprites = {
        0:pygame.sprite.Group(), #other
        1:pygame.sprite.Group(), #player sprite
        2:pygame.sprite.Group(), #boss's sprites
    }
    def __init__(self,play_state:Play):
        Template.__init__(self)
        #Bosses do a majority of what playstate does, except instead of a formation being in place there is a boss.
        #Due to this, there is a new set of sprite groups: player, boss, and bullet
        #Mostly everything is super simplified. 
        self.playstate = play_state
        #self.is_demo = self.playstate.is_demo

        self.window = self.playstate.window
        self.fullwindow = self.playstate.fullwindow
        
        self.player = self.playstate.player

        self.background = self.playstate.background
        self.floor = self.playstate.floor

        # self.playstate.curBossName="sun"
        self.boss = enemies_bosses.loaded[self.playstate.curBossName](sprites=Boss.sprites,player=self.player,window=self.playstate.window,state=self)


    def on_start(self):
        audio.play_song('twisted_inst.mp3' if self.playstate.curBossName == "crt" else "golden_inst.mp3")
        
        #killing all previous sprites
        eBM()
        for group in Boss.sprites.values():
            group.empty()

        #player code
        self.player.sprite_groups = Boss.sprites
        Boss.sprites[1].add(self.player)

        #redoing what was done in __init__
        self.__init__(play_state = self.playstate)


    def on_end(self):
        eBM() #emptying bullet max
        pygame.mixer.music.stop()
        for group in Boss.sprites.values():
            group.empty()


    def update(self,draw=True): 
        # for sprite in self.sprites[0]:pygame.draw.rect(self.window, 'blue', sprite.rect, width=3)
        # for sprite in self.sprites[1]:pygame.draw.rect(self.window, 'green', sprite.rect, width=3)
        # for sprite in self.sprites[2]:pygame.draw.rect(self.window, 'red', sprite.rect, width=3)


        #Drawing previous gameplay frame to the window -- don't ask why, it just does. 
        if draw: self.fullwindow.blit(pygame.transform.scale(self.window,pygame.display.play_dimensions_resize),pygame.display.play_pos)

        

        #updating backgrounds
        self.background.update()
        self.background.draw(self.window)
        #updating floor
        if self.floor is not None:
            self.floor.update()
            self.floor.draw(self.window)
        #updating all 
        Boss.sprites[1].update()
        Boss.sprites[2].update()
        Boss.sprites[0].update()
        #updating boss
        self.boss.update()
        #draw
        Boss.sprites[2].draw(self.window)
        Boss.sprites[1].draw(self.window)
        Boss.sprites[0].draw(self.window)

        #collision
        self.collision()
        #death - somewhat broken atm
        if self.player.dead:
            self.next_state = "play"
        #figuring out what to do when the boss dies
        elif self.boss.info['ENDBOSSEVENT']:
            self.next_state = "play" if not self.boss.info['ENDWORLD'] else 'advance'


    def event_handler(self,event):
        self.player.controls(event)
        #changing what comes next
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                self.next_state = "options","boss"
            if event.key == pygame.K_ESCAPE:
                self.next_state = "pause","boss"


    def collision(self):
        #between player and enemy
        collidelist=pygame.sprite.groupcollide(
            Boss.sprites[1],
            Boss.sprites[2],
            False,False,collided=pygame.sprite.collide_mask)
        #telling the assets that stuff collided
        for key,value in collidelist.items():
            for item in value:
                key.on_collide(2,item)
                item.on_collide(1,key)
        



