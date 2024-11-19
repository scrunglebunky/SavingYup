import pygame,os,player,text,random,levels,json,formation,anim,audio,tools,events,score,enemies,enemies_bosses
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





#gameplay
class Play(Template):
    sprites = { #sprites are now state-specific hahaha
            0:pygame.sprite.Group(), #ALL SPRITES
            1:pygame.sprite.Group(), #PLAYER SPRITE, INCLUDING BULLETS ; this is because the player interacts with enemies the same way as bullets
            2:pygame.sprite.Group(), #ENEMY SPRITES
            # 4:pygame.sprite.Group(), #UI SPRITES
        }
    demo_sprites = { #sprites exclusively for the demo state
            0:pygame.sprite.Group(), #ALL SPRITES
            1:pygame.sprite.Group(), #PLAYER SPRITE, INCLUDING BULLETS ; this is because the player interacts with enemies the same way as bullets
            2:pygame.sprite.Group(), #ENEMY SPRITES
        }

    def __init__(self,
                 window:pygame.display,
                 campaign:str = "main_story.order",
                 world:int = 0,
                 level:int = 0,
                 level_in_world:int = 0,
                 is_restart:bool = False, #so init can be rerun to reset the whole ass state
                 is_demo:bool=False, #a way to check if the player is simulated or not
                 ):

        self.sprites = Play.sprites if not is_demo else Play.demo_sprites

        self.next_state = None #Needed to determine if a state is complete
        self.fullwindow = window

        self.debug = {0:[],1:[]}
        self.is_demo = is_demo


        #resetting the sprite groups
        for group in self.sprites.values():
            group.empty()

        #06/23/2023 - SETTING THE GAMEPLAY WINDOW
        # YUP has a touhou-like border surrounding the entire game as it works
        # Because of this, gameplay will have its own entire tiny display to work with 
        # It still saves the original pygame window, but this is just to draw the display to.abs
        if not is_restart: #it only makes this the first time
            self.window = pygame.Surface(pygame.display.play_dimensions).convert_alpha()

        #Player spawn
        self.bar = ( #the field the player is able to move along
            "h", #if the bar is horizontal or vertical.
            pygame.display.play_dimensions[1]*0.90, #x position if vertical, y position if horizontal.
            (20,pygame.display.play_dimensions[0]-20), #the limits on both sides for the player to move on, y positions if vertical, x positions if horizontal
            1, #gravity. 
            )
            
        self.player = player.Player(bar=self.bar,sprite_groups=self.sprites,demo=self.is_demo)
        self.sprites[1].add(self.player)

        #06/01/2023 - Loading in level data
        self.campaign = campaign
        self.world = world
        self.level = level #the total amount of levels passed, usually used for intensities or score
        self.level_in_world = level_in_world #the amount of levels completed in the world currently 
        self.world_data = levels.fetch_level_info(campaign_world = (self.campaign,self.world))


        #event data - an event that plays over all else.
        self.event = events.NewLevelEvent(level=self.level,window=self.window) if not self.is_demo else None
        

        #updating based on intensity
        if self.world_data["dynamic_intensity"]:
            levels.update_intensities(self.level,self.world_data)

        #06/01/2023 - loading the formation
        #the formation handles spawning and management of most enemies, but the state manages drawing them to the window and updating them
        self.formation = formation.Formation(
            player = self.player,
            world_data = self.world_data,
            level=self.level,
            level_in_world=self.level_in_world, 
            sprites=self.sprites,
            window=self.window,
            is_demo = self.is_demo)

        #06/03/2023 - Loading in the background
        self.background = Bg(self.world_data['bg'], resize = self.world_data['bg_size'], speed = self.world_data['bg_speed'])
        #also loading in the floor if it exists
        self.floor = Fl(image=self.world_data['floor_img'],player=self.player,window=self.window,move=self.world_data['floor_move'],scale=self.world_data['floor_size']) if self.world_data['floor_img'] is not None else None


        #timer for updating new level
        self.leveltimer = 0 
        #relating to advance sprite
        self.in_advance:bool = False #if true, will not update much besides the background and player
        #what boss the boss state pulls from
        self.curBossName = "ufo"

   
    
    def on_start(self,**kwargs):#__init__ v2, pretty much.
        #06/24/2023 - Playing the song
        audio.play_song(self.world_data["song"])
        self.player.sprite_groups = self.sprites
        eBM()



    def on_end(self,**kwargs): #un-init, kind of
        pygame.mixer.music.stop()
        if tools.debug: print(self.debug.values())
        eBM()


    
    def update(self, draw=True):
        #Drawing previous gameplay frame to the window -- don't ask why, it just does. 
        if draw: self.fullwindow.blit(pygame.transform.scale(self.window,pygame.display.play_dimensions_resize),pygame.display.play_pos)


        #Updating backgrounds - drawing to window
        self.background.update()
        self.background.draw(self.window)
        if self.floor is not None:
            self.floor.draw(self.window)
        self.formation.draw_img(window=self.window) #displaying a special formation image if necessary


        #updating all individual sprites, with the fourth group having special priority.
        self.sprites[0].update()
        self.sprites[1].update()
        self.sprites[2].update()
        self.sprites[0].draw(self.window)
        self.sprites[1].draw(self.window)
        self.sprites[2].draw(self.window)

        #ending function early if event playing
        if self.event is not None and self.event.playing:
            self.event.update()
            return


        #only updating the formation after checking for events, to prevent the level starting beforehand.
        self.formation.update()

        #print debug positions
        for pos in self.debug[0]:
            self.window.blit(pygame.transform.scale(img["placeholder.bmp"],(10,10)),pos)

        

        #ending function early if advancing
        if self.in_advance: return 
        
        #calling collision
        self.collision()
        

        
        #06/18/2023 - Starting a new level
        if self.formation.cleared and self.leveltimer > 180:
            #checking to start the advance state
            if self.level_in_world >= self.world_data["levels"]:
                self.next_state = "advance"
                return
            #checking to see if the next world should be a boss intermission -- does not update levels
            elif self.level_in_world + 1 in self.world_data['boss_levels']:
                self.next_state = "boss"
                self.curBossName = self.world_data['bosses'][self.world_data['boss_levels'].index(self.level_in_world + 1)]
                self.level_in_world += 1
                return
            #if not, updating everything
            else:
                self.level += 1
                self.level_in_world += 1
                self.formation.empty()
                
            #restarting the formation
            self.formation.__init__(
                world_data = self.world_data,
                level=self.level,
                level_in_world=self.level_in_world, 
                sprites=self.sprites,
                player=self.player,window=self.window,
                is_demo = self.is_demo)

            #resetting the level timer
            self.leveltimer = 0 

            #restarting the new level event
            if self.event is not None: self.event.__init__(window=self.window,level=self.level)

        #updating the wait timer
        elif self.formation.cleared:
            self.leveltimer += 1
        
        #08/21/2023 - Game Over - opening a new state if the player is dead
        if self.player.health <= 0:
            self.next_state = "gameover"



    def collision(self):
        #Detecting collision between players and enemies 
        collidelist=pygame.sprite.groupcollide(self.sprites[1],self.sprites[2],False,False,collided=pygame.sprite.collide_mask)
        for key,value in collidelist.items():
            for item in value:
                key.on_collide(2,item)
                item.on_collide(1,key)



    def new_world(self):
        self.world += 1
        self.level_in_world = 0
        self.world_data = levels.fetch_level_info(campaign_world = (self.campaign,self.world))
        #changing bg
        self.background.__init__(self.world_data['bg'], resize = self.world_data['bg_size'], speed = self.world_data['bg_speed'])
        #changing floor
        self.floor = Fl(image=self.world_data['floor_img'],player=self.player,window=self.window,move=self.world_data['floor_move'],scale=self.world_data['floor_size']) if self.world_data['floor_img'] is not None else None


    def event_handler(self,event):
        if self.is_demo: return
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
        

        self.demo_state = Play(window = self.window, world = 1, level = random.randint(0,50), is_demo = True) #this is different from the tools.demo value, as this is just to simulate a player
        self.hiscoresheet = score.generate_scoreboard()

        #basic events that will occur during the title
        self.events = [
            "demo",
            "hiscore",
        ]
        self.event = 0
        self.timer = 0
        self.resize = [(winrect.width * 0.4) , 800 * ((winrect.width*0.4)/600)]
        if self.resize[0] > 600:
            self.resize = [600,800]
        self.image_placements = {}
            # "welcome":(pygame.display.rect.width*0.01,pygame.display.rect.height*0.01),
        self.image_placements["demo"] = (pygame.display.rect.width*0.01,pygame.display.rect.height*0.1)
        self.image_placements["score"] = (pygame.display.rect.width*0.99 - self.resize[0] ,pygame.display.rect.height*0.1)
        Title.em_continue.change_pos((winrect.centerx,winrect.centery),isCenter=True)

        self.hiscoresheet = pygame.transform.scale(self.hiscoresheet,self.resize)
        
    
    
    def on_start(self):
        self.event = self.id = 0
        self.demo_state.__init__(window = self.window, world = 1, level = random.randint(0,50), is_demo = True)
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
        self.demo_state.update(draw=False)
        self.window.blit(pygame.transform.scale(self.demo_state.window,self.resize),self.image_placements['demo'])
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
                self.next_state = "tutorial"
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
        rank_val = score.score * (1 + 0.01*self.play_state.world) * (1+(0.01*self.play_state.level))
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
            is_restart=True
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
                    is_restart=True
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
        self.phases = (self.phase0,self.phase1,self.phase2,self.phase3,self.phase4)
        """ PHASE LIST
        0 - the background slowly fading in
        1 - "LEVEL COMPLETE" hitting the screen
        2 - A list of certain things that have occurred: killed enemies, damage taken, shots fired, accuracy
        3 - Saying where you are going, with a scaled-down picture of the background. 
        4 - Playing a random animation that launches the player offscreen"""
        #defining a bunch of values elsewhere
        self.initialize_values()   

        
    def on_start(self):
        #advancing the world early in playstate so the right info is fetched
        self.play_state.new_world()
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
            self.sprites.add(self.em_nextlevel,self.em_movingto,self.em_nextleveltext,self.em_enemylog)




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



    def phase4(self):
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
    
    def phase5(self):
        ...
        

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
        self.em_nextlevel = Em(im=self.play_state.world_data['bg'],resize=(225,300),pattern="sine",coord=(winrect.width*0.75,winrect.centery),isCenter=True)
        self.em_movingto = Em(im="a_movingto.png",pattern="jagged",coord=(self.em_nextlevel.rect.centerx,self.em_nextlevel.rect.top-25),isCenter=True)
        self.em_nextleveltext = Em(force_surf = text.load_text(str(self.play_state.world_data['world_name']),50),pattern="jagged",coord=(self.em_nextlevel.rect.centerx,self.em_nextlevel.rect.bottom+25),isCenter=True)
        self.em_enemylog = Em(force_surf = anim.generate_enemy_log(world_data=self.play_state.world_data), pattern = 'sine', 
                coord = (self.em_nextleveltext.rect.centerx,self.em_nextleveltext.rect.bottom), isCenter=True)
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
        self.is_demo = self.playstate.is_demo

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
        






class Tutorial(Template):
    demosprites = { #sprites are now state-specific hahaha
            0:pygame.sprite.Group(), #ALL SPRITES
            1:pygame.sprite.Group(), #PLAYER SPRITE, INCLUDING BULLETS ; this is because the player interacts with enemies the same way as bullets
            2:pygame.sprite.Group(), #ENEMY SPRITES
            # 4:pygame.sprite.Group(), #UI SPRITES
        }
    sprites = pygame.sprite.Group()
    
    #tutorial player object
    subwindow = pygame.Surface((600,800),pygame.SRCALPHA).convert_alpha()
    subwindowrect = subwindow.get_rect()
    bar=("h",subwindowrect.height*0.8,(10,subwindowrect.width-10),1)
    player = PD(bar=bar,sprite_groups=demosprites)
    #emblmes
    t_title = Em("tutorial",current_anim="tutorial")
    t_yes = Em("tutorial",current_anim="yes")
    t_no = Em("tutorial",current_anim="no")
    t_great = Em("g_great.png",coord=(winrect.width*0.8,winrect.height*0.5),isCenter=True,pattern="sine")
    t_continue = Em("continue",current_anim="idle",coord=(0,0))
    t_sandwich = enemies.BasicEventItem(im="home_D",coord=(subwindowrect.width*.75,bar[1]),isCenter=True)
    t_enemylog = Em(None,force_surf = anim.generate_enemy_log(world_data = levels.fetch_level_info(("main_story.order",random.randint(0,10)))))
    #keeping a consistent image for the continue button
    t_continue.orig_coord = (winrect.width-t_continue.rect.width,winrect.height-t_continue.rect.height)

    #text emblem -- displays specific text at a given time -- no emblem for text yet so this one's modified
    cur_text=Em()
    text = text.AutoNum("DO YOU NEED A TUTORIAL?\nARROW KEYS TO SELECT, Z TO CONFIRM.",host=cur_text,make_host_rect=True)
    cur_text.aimg = text
    
    #tutorial graphic information
    t_tutorial = Em(im="tutorial",current_anim="move",coord=(-100,-100)) #this will change animations based off which part of the tutorial is playing
    tutorial_anim = ("move","jump","crouch","fastfall","shoot","focus")
    tutorial_text = (
        "<- OR -> TO MOVE!",
        "UP KEY TO JUMP!\nYOU CAN JUMP ON ENEMIES!",
        "DOWN TO CROUCH!\nGOOD FOR DODGING.",
        "DOWN KEY WHILE\nIN THE AIR TO FASTFALL!",
        "Z or X TO SHOOT!\nHOLD DOWN TO AUTOSHOOT.",
        "SHIFT TO FOCUS!\nTHIS MAKES YOU SMALLER AND SLOWER!",)
    enemies_text = (
        "ENEMIES SIT AT THE TOP OF THE SCREEN\n AND SWERVE DOWN TO ATTACK YOU.",
        "THERE ARE FOUR DIFFERENT ENEMY TYPES:\n A,B,C, AND D.",
        "A SWERVES DOWN, B BOUNCES,\n C IS A TURRET, AND D IS SPECIAL PER WORLD.",
        "A GUIDE WILL SHOW TO TELL YOU WHICH ENEMIES\n ARE WHICH AT THE START OF THE WORLD.",
    )
    end_text = (
        "GREAT JOB!\nHAVE A SANDWICH AS A REWARD.",
        "...",
        "DAMN.",
        "NO NO NO WAIT-"
    )

   

    def __init__(self,window):
        Template.__init__(self)
        self.window=window
        self.initialize_values()

    def on_start(self):
        self.initialize_values()
        self.update_phase()

    def on_end(self):
        ...

    def start(self,start=False):
        if start:
            #creating emblems for this purpose
            Tutorial.sprites.add(Tutorial.t_title,Tutorial.t_yes,Tutorial.t_no,Tutorial.cur_text,Tutorial.t_continue)
            Tutorial.t_title.add_tween_pos((winrect.centerx,-100),(winrect.centerx,50),speed=2.0,started=True,isCenter=True)
            Tutorial.t_no.add_tween_pos((-100,winrect.centery/2),(winrect.width*0.4,winrect.centery/2),speed=2.0,started=True,isCenter=True)
            Tutorial.t_yes.add_tween_pos((winrect.width+100,winrect.centery/2),(winrect.width*0.6,winrect.centery/2),speed=2.0,started=True,isCenter=True)
            Tutorial.cur_text.add_tween_pos((0,winrect.height+100),(0,winrect.height*0.8),speed=5,started=True)
            Tutorial.t_continue.add_tween_pos((Tutorial.t_continue.orig_coord[0],winrect.width+100),Tutorial.t_continue.orig_coord,speed=2.0,started=True)
            return
        self.counter1 += 1
        #bg effects
        self.bgFlash.update()
        self.bg.update()
        self.bg.image = self.bgFlash.image
        self.bg.draw(self.window)
        self.bg.speed=[5*sin(self.counter1/250),5*sin(self.counter1/400)]
        #sprites
        self.update_sprites()

        #drawing choice
        if not self.choice:
            self.window.blit(img['cursor.png'],(Tutorial.t_no.rect.centerx-50, Tutorial.t_no.rect.centery-10))
        else:
            self.window.blit(img['cursor.png'],(Tutorial.t_yes.rect.centerx-50, Tutorial.t_yes.rect.centery-10))


    def tutorial(self,start=False):
        if start:
            self.subphase=0
            #deleting old graphics, adding new ones, changing text graphic
            Tutorial.t_yes.kill();Tutorial.t_no.kill();Tutorial.t_continue.kill()
            Tutorial.sprites.add(Tutorial.t_tutorial)
            Tutorial.cur_text.aimg.update_text(Tutorial.tutorial_text[self.subphase])
            #changing the background
            self.bg.aimg.__init__(host=self.bg,name="tutorial_bg.png",resize=winrect.size)
            self.bg.speed=[0,1]
            #extra new graphic info
            Tutorial.t_tutorial.add_tween_pos((-100,winrect.centery/2),(winrect.centerx/2,winrect.centery/2),speed=5,started=True,isCenter=True)
            Tutorial.t_tutorial.pattern = "sine"
            #adding the player
            Tutorial.demosprites[1].add(Tutorial.player)
            Tutorial.player.reset()
            return

        self.counter1 += 1
        #bg
        self.bg.update()
        self.bg.draw(self.window)
        self.bg.speed=[0,1]
        #sprites
        self.update_sprites()
        #updating information
        self.checker1 = self.checker1 or Tutorial.player.check[Tutorial.tutorial_anim[self.subphase]]
        if self.checker1 and self.intermission > 60:
            if self.subphase +1 >= len(Tutorial.tutorial_anim):
                self.update_phase()
                return
            #updating task checking info
            Tutorial.player.reset()
            self.checker1 = False
            self.subphase += 1
            self.intermission = 0
            #updating graphics
            Tutorial.t_tutorial.aimg.change_anim(Tutorial.tutorial_anim[self.subphase])
            Tutorial.cur_text.aimg.update_text(Tutorial.tutorial_text[self.subphase])
            #killing 'great'
            Tutorial.t_great.kill()
        elif self.checker1 and self.intermission == 0:
            self.intermission += 1
            Tutorial.sprites.add(Tutorial.t_great)
            self.kaboom(group=Tutorial.sprites,coord=Tutorial.t_great.rect.center,animation_resize=(225,120))
        #intermission code
        elif self.checker1:
            self.intermission += 1
            Tutorial.sprites.add(BP(pos=(Tutorial.t_great.rect.centerx,Tutorial.t_great.rect.centery+50),texture="greenblock"))
            self.bg.speed=[5*sin(self.counter1/5),10*sin(self.counter1/2)]



    def objective(self,start=False):
        # self.next_state = "play"

        if start:
            self.counter1 = 0 
            Tutorial.sprites.empty()
            Tutorial.sprites.add(Tutorial.t_tutorial,Tutorial.t_title,Tutorial.cur_text,Tutorial.t_continue)
            Tutorial.t_tutorial.aimg.change_anim('premise')
            Tutorial.cur_text.add_tween_pos((0,winrect.height+100),(0,winrect.height*0.8),speed=5,started=True)
            Tutorial.cur_text.aimg.update_text("ITEMS WITH A RED SHADOW WILL DAMAGE YOU.\nITEMS WITH A GREEN SHADOW ARE SAFE TO TOUCH.")
            Tutorial.player.pos[0] = Tutorial.subwindowrect.centerx
            Tutorial.player.reset_movement()
            Tutorial.player.autoshoot=False
            Tutorial.t_continue.add_tween_pos((Tutorial.t_continue.orig_coord[0],winrect.width+100),Tutorial.t_continue.orig_coord,speed=2.0,started=True)

        #bg
        self.counter1 += 1
        self.bg.update()
        self.bg.draw(self.window)
        self.bg.speed=[0,1]
        #sprites
        self.update_sprites()

        #Adding example elements
        if self.counter1 % 80 == 0:
            Tutorial.demosprites[2].add(enemies.HurtHeal(self.player,type=self.obj_type))
            self.obj_type = not self.obj_type


    def enemies(self,start=False):
        if start:
            self.counter1 = 0 
            self.subphase = 0 
            self.checker1 = False
            Tutorial.sprites.empty()
            Tutorial.sprites.add(Tutorial.t_tutorial,Tutorial.t_title,Tutorial.cur_text,Tutorial.t_continue)
            Tutorial.t_tutorial.aimg.change_anim('enemies')
            Tutorial.cur_text.aimg.update_text(Tutorial.enemies_text[self.subphase])
            
            Tutorial.t_continue.add_tween_pos((Tutorial.t_continue.orig_coord[0],winrect.width+100),Tutorial.t_continue.orig_coord,speed=2.0,started=True)
            Tutorial.cur_text.add_tween_pos((0,winrect.height+100),(0,winrect.height*0.8),speed=5,started=True)
            Tutorial.player.rect.centerx = winrect.centerx
            Tutorial.player.movement[0],Tutorial.player.movement[3] = Tutorial.player.movement_old[0],Tutorial.player.movement_old[3]
            Tutorial.player.autoshoot=False


        self.counter1 += 1
        self.bg.update()
        self.bg.draw(self.window)
        self.bg.speed=[1,0.5]
        self.update_sprites()

        if self.subphase == 3:
            if self.counter1 % 60 == 0:
                Tutorial.t_enemylog.aimg.image = anim.generate_enemy_log(world_data = levels.fetch_level_info(("main_story.order",random.randint(0,10))))



        if self.checker1:
            self.checker1 = False
            self.subphase += 1
            if self.subphase >= len(Tutorial.enemies_text):
                self.update_phase()
                Tutorial.t_enemylog.kill()
            else:
                if self.subphase == 1:
                    Tutorial.sprites.add(Tutorial.t_enemylog)
                    Tutorial.t_enemylog.aimg.image = anim.all_loaded_images['enemylog_hint.png']
                    Tutorial.t_enemylog.add_tween_pos((winrect.centerx,-100),winrect.center,speed=5,started=True,isCenter=True)
                if self.subphase == 3:
                    Tutorial.t_enemylog.aimg.image = anim.generate_enemy_log(world_data = levels.fetch_level_info(("main_story.order",random.randint(0,10))))

                Tutorial.cur_text.aimg.update_text(Tutorial.enemies_text[self.subphase])



    def end(self,start=False):
        if start:
            #initializing values yet again
            self.counter1 = self.subphase = 0 
            Tutorial.demosprites[2].add(Tutorial.t_sandwich)
            Tutorial.t_tutorial.aimg.change_anim('enemies')
            Tutorial.cur_text.aimg.update_text(Tutorial.end_text[self.subphase])
            Tutorial.cur_text.pattern='sine'
            Tutorial.cur_text.add_tween_pos(Tutorial.cur_text.coord,(0,winrect.height*0.5),speed=5,started=True)
            Tutorial.t_continue.add_tween_pos(Tutorial.t_continue.orig_coord,(Tutorial.t_continue.orig_coord[0],winrect.width+100),speed=1.0,started=True)
            Tutorial.t_title.add_tween_pos(Tutorial.t_title.rect.center,(Tutorial.t_title.rect.centerx,-100),isCenter=True,speed=3.0,started=True)
            Tutorial.t_tutorial.add_tween_pos(Tutorial.t_tutorial.rect.center,(0,-999),isCenter=True,speed=5.0,started=True)
            Tutorial.player.rect.centerx = winrect.centerx
            Tutorial.player.autoshoot=False

        else:
            self.counter1 += 1
            
            self.bg.update()
            if self.subphase == 1:
                self.bgUnflash.update()
                self.bg.image = self.bgUnflash.image
            self.bg.draw(self.window)
            self.bg.speed=[1,0.5]
            self.update_sprites()

            if self.counter1 == 120:
                Tutorial.t_continue.kill()
                Tutorial.t_title.kill()
                Tutorial.t_tutorial.kill()


            #turnary operators go brr
            self.checker1 = Tutorial.t_sandwich.touched if self.subphase == 0 else self.counter1 > 240 if self.subphase == 1 else self.counter1 > 120 if self.subphase == 2 else self.counter1 > 30 if self.subphase == 3 else False
            #updating subphase info
            if self.checker1:
                self.subphase += 1
                if self.subphase >= len(Tutorial.end_text):
                    self.update_phase()
                else:
                    Tutorial.cur_text.aimg.update_text(Tutorial.end_text[self.subphase])
                    

                #phase-specific events
                if self.subphase == 1:
                    self.counter1 = 0 
                    Tutorial.t_sandwich.kill()
                    Tutorial.player.kill()
                    self.kaboom(Tutorial.demosprites[0],Tutorial.player.rect.center,Tutorial.player.rect.size)

                elif self.subphase == 2:
                    self.bg.aimg.__init__(host=self.bg,name="NONE")
                    self.counter1 = 0 
                elif self.subphase == 3:
                    self.kaboom(Tutorial.sprites,winrect.center,(winrect.size[0]*2,winrect.size[1]*2))
                    self.counter1 = 0






    def done(self,start=False):
        #skipping the cutscene for now
        self.next_state = "play"



    def update(self):
        self.phases[self.phase]()
        self.collision()



    def update_phase(self):
        self.phase += 1
        self.phases[self.phase](start=True)



    def update_sprites(self):
        #sprites
        Tutorial.subwindow.fill(pygame.Color(0,0,0,0))
        # Tutorial.subwindow.fill(pygame.Color(128,128,255,128))
        for v in Tutorial.demosprites.values():
            v.update()
            v.draw(Tutorial.subwindow)
        Tutorial.sprites.update()
        Tutorial.sprites.draw(self.window)
        self.window.blit(pygame.transform.scale(Tutorial.subwindow,pygame.display.play_dimensions_resize),(winrect.width-pygame.display.play_dimensions_resize[0],0))



    def initialize_values(self):
        #bg info
        self.bgFlash = WhiteFlash(surface=self.window,img="tutorial_bg.png",start_val=0,end_val=255,spd=-1.0,isreverse=True)
        self.bgUnflash = WhiteFlash(surface=self.window,img="tutorial_bg.png",start_val=255,end_val=0,spd=1.25)
        self.bg=Bg(img=self.bgFlash.image,speed=[0.25,0.25],resize=pygame.display.dimensions)
        self.bg.pos = [pygame.display.dimensions[0]/-2,pygame.display.dimensions[0]/-2]
        
        #emblem info
        Tutorial.cur_text.aimg.update_text("DO YOU NEED A TUTORIAL?\nARROW KEYS TO SELECT, Z TO CONFIRM.")

        #other info
        self.next_state = None
        self.return_state = "play"
        #phase info
        self.phase=-1
        self.phases = (
            self.start,
            self.tutorial,
            self.objective,
            self.enemies,
            self.end,
            self.done,)
        #start phase
        self.choice = True #initially says you need a tutorial
        #tutorial subphase
        self.subphase = 0 
        self.intermission = 0
        self.checker1 = False
        self.counter1 = 0 

        #objective phase
        self.obj_type = True
        

        

    def event_handler(self,event):
        if self.phase == 0:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    self.choice = True
                elif event.key == pygame.K_LEFT:
                    self.choice = False
                    
        elif self.phase == 1 or self.phase == 4:
            Tutorial.player.controls(event)

        if event.type == pygame.KEYDOWN and event.key == pygame.K_z:
            if self.phase == 0:
                if self.choice:
                        self.update_phase()
                else:
                    for i in range(4):
                        self.update_phase()
                    

            if self.phase == 1:
                if self.checker1:
                    self.intermission = 999
            elif self.phase == 3:
                self.checker1 = True
            elif self.phase == 2:
                self.update_phase()
                


    def collision(self):
        #Detecting collision between players and enemies 
        collidelist=pygame.sprite.groupcollide(Tutorial.demosprites[1],Tutorial.demosprites[2],False,False,collided=pygame.sprite.collide_mask)
        for key,value in collidelist.items():
            for item in value:
                key.on_collide(2,item)
                item.on_collide(1,key)