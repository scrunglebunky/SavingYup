"""OLD CODE -- WHAT COULD HAVE BEEN
HERE I POST A LOT OF OLDER PIECES OF CODE WITH A LITTLE DESCRIPTION ON TOP OF WHAT IT DID
SADLY I REMOVED MOST OF THE OLD CODE SO THIS IS RATHER EMPTY."""


""" THE TITLE STATE
the last of the states to be removed... rip.
#title screen
# THIS ALSO HAS TO BE UPDATED
# USE THE EMBLEMS I GAVE YOU DAMNIT
class Title(Template):
    sprites = pygame.sprite.Group()
    em_titlescreen = Em(im="title_image.jpg",coord=(pygame.display.rect.center),isCenter=True,resize=(400,400))
    em_start = TEm(txt="PRESS ANY KEY TO CONTINUE\nARROW KEYS TO MOVE \nZ TO SHOOT \nX CHANGES WEAPON \nESC TO QUIT",
        coord=(em_titlescreen.rect.left,em_titlescreen.rect.bottom),
        isCenter=False,
        resize=(400,pygame.display.rect.height-em_titlescreen.rect.bottom),font=text.terminalfont_20)
    em_highscores = Em(im=None,force_surf = score.generate_scoreboard(),coord=(pygame.display.rect.center),resize=(400,400),isCenter=True,hide=True)
    sprites.add(em_titlescreen,em_highscores,em_start)

    def __init__(self,window:pygame.Surface,border): #Remember init is run only once, ever.
        self.window=window
        # self.border=border
        self.next_state = None
        self.lifespan = 0
   
    
    def on_start(self):
        #self.demo_state.__init__(window = self.window, world = 1, level = random.randint(0,50), is_demo = True)
        # self.border.spr_logo.change_pos(pos = (winrect.centerx,winrect.height*0.1),isCenter=True)
        # self.border.change_vis(True,self.border.spr_logo)
        # self.border.spr_logo.hide = False
        ...

    def on_end(self):
        #this doesn't change the positioning of the icons or anything. It lets the other state, Play, handle it.
        # self.border.spr_logo.add_tween_pos(cur_pos = self.border.spr_logo.rect.topleft , target_pos = self.border.spr_logo.orig_coord  ,speed=5,started=True,isCenter=False)
        # self.border.change_vis(False)
        ...

    def update(self):
        Title.sprites.update()
        Title.sprites.draw(self.window)
        #switching between title image and high scores
        self.lifespan += 1
        if self.lifespan % 120 == 0:
            Title.em_titlescreen.hide = not Title.em_titlescreen.hide
            Title.em_highscores.hide = not Title.em_highscores.hide
        

    def event_handler(self,event):
        if event.type == pygame.KEYDOWN:
            match event.key:
                case pygame.K_ESCAPE:
                    self.next_state = "quit"
                case _:
                    self.next_state = "play"


"""
"""
THE ADVANCE STATE : "when a world is completed"
this was originally some huge stylistic fanfare whenever you completed a world
but i decided it was just too tacky and took away from the game's aesthetic, or at least what I'm going for for it
plus, it incorporated the worlds and such, which i was snubbing out from the final release
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
        \""" PHASE LIST
        0 - the background slowly fading in
        1 - "LEVEL COMPLETE" hitting the screen
        2 - A list of certain things that have occurred: killed enemies, damage taken, shots fired, accuracy
        X - Saying where you are going, with a scaled-down picture of the background. 
        3 - Playing a random animation that launches the player offscreen\"""
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



    \"""
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
    \"""


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

"""


""" THE BOSS STATE: "Playstate but there's a boss now.
I got rid of this one because it had pretty much no purpose.
Like why do this when the formation could just contain the boss and pass all the arguments to it?
And then continue with the levels like usual?

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
        
"""


""" THE GAMEOVER STATE: "gameplay state and modifying it so everything slows down and... yada yada you get the picture"
I removed this from the game because, like advance state, it was very complex and unnecessary.
Sure it's cool, and it modifies all these things and changes all this, but it feels out of place with how fluid it feels
plus everything is hard-coded in a way I don't like. 
When I add the game-over state back, it's just gonna be another interrupt sequence like the shop, probably with a goofy little, shorter sequence.

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
        self.finalscore = play_state.player.coins
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
        self.scoregraphic=Em(force_surf=score.generate_graphic(self.play_state.player.coins,""),coord=(0,0),isCenter=True)

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
            GameOver.sprites.add(Em(force_surf = text.load_text(text=str(finalscore),size=40) ,coord=(pygame.display.rect.center[0]*0.75,pygame.display.rect.height*0.32),isCenter=False))
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
        rank_val = finalscore * (1+(0.01*self.play_state.level))
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
        return (finalscore > score.scores[0][1]) or (len(score.scores)<10)


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
        self.finalscore= 0
        self.play_state.__init__(
            window=self.play_state.fullwindow,
        )
        self.__init__(window=self.window,play_state=self.play_state)
        score.save_scores(scores=score.scores)
        self.next_state="title"

"""


""" REV C ENEMIES
idk why these are even left here
but here they are!


DEFAULT CHARACTER
class CharTemplate(pygame.sprite.Sprite):
    #default image if unchanged
    image = pygame.Surface((30, 30), pygame.SRCALPHA)
    pygame.draw.circle(image, "red", (15, 15), 15)
    
    def __init__(self,formation_position:tuple,offset:tuple,default_image = True,**kwargs):
        #initializes sprite code
        pygame.sprite.Sprite.__init__(self)
        
        #TAKING ARGUMENTS
        self.offset = offset

        #default character code
        self.state = "enter" #current behavior patterns
        self.health=1 #Health for characters
        self.scorevalue=100 #Score given to player
        self.idlePos = [(formation_position[0]+self.offset[0]),(formation_position[1]+self.offset[1])] # current position in idle
        self.dead = (self.health <= 0)

        #IMAGE CODE
        self.sh = None
        if default_image:
            self.image = CharTemplate.image
            self.rect = self.image.get_rect()
    
        #SHOOT CODE    
        self.shoot_times = [] #the maximum amount will be like 10, which would only be achieved after level 100 or so
        #shoot times are not generated by default

        #STATE CODE
        self.frames_in_state = 0 #counter for states. reset at the end of every state, but risen every frame, whether used or not.

        #CONTAINER CODE -- ITEM DROPPER
        self.container:tuple = None #a tuple, containing the type of item and the name of the item. the second index is usually unused if the item is not a bullet.


    def update(self):
        self.state_update()
        self.collision_update()
        self.animation_update()

    def animation_update(self):
        pass

    def state_update(self):
        self.frames_in_state += 1
        if self.state=="enter": self.state_enter()
        if self.state=="idle_search": self.state_idle_search()
        if self.state=="idle": self.state_idle()
        if self.state=="attack": self.state_attack()
        if self.state=="return": self.state_return()

    def state_enter(self):
        self.stchg('idle_search')

    def state_idle_search(self):
        #Slowly dragging the character to the title screen
        horizontal_condition_met = abs(self.idlePos[0] - self.rect.center[0]) <= 5
        vertical_condition_met = abs(self.idlePos[1] - self.rect.center[1]) <= 5
        if not horizontal_condition_met or not vertical_condition_met:
            if not horizontal_condition_met:
                if self.idlePos[0] < self.rect.center[0]:
                    self.rect.x -= 5
                elif self.idlePos[0] > self.rect.center[0]:
                    self.rect.x += 5
            if not vertical_condition_met:
                if self.idlePos[1] < self.rect.center[1]:
                    self.rect.y -= 3
                elif self.idlePos[1] > self.rect.center[1]:
                    self.rect.y += 3
        else: 
            self.stchg('idle')

    def state_idle(self):
        #this is the only state that does not have a frame counter
        #this is because it does not automatically exit
        self.rect.center=self.idlePos

    def state_attack(self):
        #same default as state_enter
        if True: 
            self.stchg("return") 

    def state_return(self):
        if True:
            self.stchg("idle_search") #or 'idle'  

    def collision_update(self):
        #most of what this does is check for health
        #collision is a universal term for health, positioning, etc.
        #DO NOT CHANGE THIS. THIS WILL MESS UP THE FORMATION
        self.dead = (self.health <= 0)
        if self.dead:
            self.kill(reason="health")

    def on_collide(self,
                   collide_type:int #the collide_type refers to the sprite group numbers. 0 for universal (not used), 1 for other player elements, 2 for enemies
                   ):
        #5/26/23 - Updating health shizznit if interaction with "player type" class
        if collide_type == 1:
            self.health -= 1

    def formationUpdate(self,
        new_pos:tuple #location of the formation, not including offset
        ):
        #following formation
        self.idlePos = [
            (new_pos[0] + self.offset[0]),
            (new_pos[1] + self.offset[1])]
    
    def stchg(self,state:str): #changing the state 
        self.frames_in_state = 0 
        self.state = state
    
    def kill(self,reason=None):
        if reason == "health":
            score.score += self.scorevalue
        pygame.sprite.Sprite.kill(self)
       
    def change_anim(self,anim:str) -> bool:
        try:
            self.sh.change_anim(anim)
            return True
        except: return False

class Nope(CharTemplate):

    image = pygame.Surface((30, 30), pygame.SRCALPHA)
    pygame.draw.rect(image,"red",pygame.Rect(0,0,30,30))


    def __init__(self,sprites:dict,level:int,formation_position:tuple,offset:tuple,data:dict,**kwargs):
        CharTemplate.__init__(self,level=level,formation_position=formation_position,offset=offset,data=data,default_image=False,**kwargs)
        #img code
        # self.sh = anim.Spritesheet("NOPE","idle")
        self.image = Nope.image
        self.rect = self.image.get_rect()

        #06/06/23 - enter state - copied from revC
        self.enter_dir = random.choice(('l','r')) #where the character is entering FROM
        self.rect.center = (pygame.display.play_dimensions[0],pygame.display.play_dimensions[1]/2) if self.enter_dir == 'r' else (0,pygame.display.play_dimensions[1]/2)
        self.parabola = (pygame.display.play_dimensions[0],pygame.display.play_dimensions[1]*0.75) if self.enter_dir == 'r' else (25,pygame.display.play_dimensions[1]*0.75)

        #07/09/2023 - the way the character will move in attack state
        self.atk_patterns = [] 
        self.spd = 0

    def update(self):
        CharTemplate.update(self)
        # self.image = Nope.image
        self.image = Nope.image
        if self.state == 'attack':
            self.image = pygame.transform.rotate(Nope.image,3*self.spd)

    def state_enter(self):
        self.rect.x = self.rect.x-2 if self.enter_dir == 'r' else self.rect.x+2

        self.rect.y = (-(1 / 50) * ((self.rect.x + (
            self.parabola[0] if self.enter_dir == 'l' else (self.parabola[0]*-1) )
            ) ** 2) + self.parabola[1])

        if abs(225-self.rect.x) <= 100 or abs(100 - self.rect.y) <= 50:
            self.stchg("idle_search")
    
    def state_attack(self):
        if self.frames_in_state == 1:
            #07/09/2023 - FIRST FRAME IN STATE - SETTING POSITIONS
            self.atk_patterns = [random.randint(10,pygame.display.play_dimensions[0]-10) for i in range(20)]

        # moving down
        self.rect.y+=5

        # moving left and right based on atk_patterns
        if len(self.atk_patterns) > 0:
            if abs(self.rect.center[0] - self.atk_patterns[0]) > 20:
                self.spd = (0.05 * (self.atk_patterns[0] - self.rect.center[0]))
                self.spd = -5 if self.spd < -5 else 5 if self.spd > 5 else self.spd
                self.rect.x += self.spd


            else:
                self.spd = 0 
                self.atk_patterns.pop(0)



        # exit code
        if self.rect.top>=pygame.display.play_dimensions[1]:
            self.rect.bottom=0
            self.frames_in_state = 0
            self.stchg('return') 
class Spike(CharTemplate):
    image = pygame.Surface((30, 30), pygame.SRCALPHA)
    pygame.draw.rect(image,"orange",pygame.Rect(0,0,30,30))
    def __init__(self,formation_position:tuple,offset:tuple,**kwargs):
        #default
        CharTemplate.__init__(self,formation_position,offset,**kwargs)
        #setting images
        self.image = Spike.image
        self.rect = self.image.get_rect()

"""

""" THE OLD UI BORDER
This was mostly just stuff before i created the emblem class, so everything was manually drawn to the screen 

06/22/2023 - UI BAR CLASS
The UI bar is something used by playstate to display things such as the score, background image, and logo.

class BorderOld():
    
    #06/24/2023 - Adding EMBLEMS, which are just different UI symbols to add
    emblems = [ ]

    #06/25/2023 - items to go with emblems
    # So, there are all of the emblems that show where the score values should go, right?
    # Well this is going to be the same thing but a little more specific.
    # This will be a tuple filled with coordinates
    # Main will then feed in another tuple filled with specific number assets to feed into these positions
    num_coords = ()
    sprites = pygame.sprite.Group() #all sprites used in the state

    def __init__(self,
        anim_bg:bool = True,
        anim_logo:bool = True,
        UI_art:str = "uibox.png",
        ):

        #06/03/2023 - UI - Making a separate brick to the right with highest graphical priority used as a backgorund for the UI
        self.UI_art = UI_art
        self.UI_rect = pygame.Rect(0,0,pygame.display.dimensions[0],pygame.display.dimensions[1])
        self.UI_img = pygame.Surface(pygame.display.dimensions)
        self.UI_img.blit(pygame.transform.scale(anim.all_loaded_images[self.UI_art],(self.UI_rect[2],self.UI_rect[3])),(0,0))

        #06/22/2023 - Animation booleans / setting spritesheet info
        self.anim_bg:bool = anim_bg
        self.anim_logo:bool = anim_logo
        self.animated = self.anim_bg or self.anim_logo


        #06/30/2023 - filling dynamic image sizes for the emblems
        #06/24/2023 - Adding EMBLEMS, which are just different UI symbols to add
        Border.sprites.empty()
        Border.emblems = [
            Em(
                im = "logo.png",
                coord = (
                    pygame.display.dimensions[0] - ( pygame.display.dimensions[0] - (pygame.display.play_dimensions_resize[0] + pygame.display.play_pos[0])),
                    pygame.display.dimensions[1]*0.15 - (anim.all_loaded_images['logo.png'].get_height()/2))), #LOGO
            Em(
                im="score.png",
                coord = (
                    pygame.display.play_dimensions_resize[0] + pygame.display.play_pos[0] + 25,
                    pygame.display.dimensions[1]*0.4)), #SCORE
            Em(
                im="debug.png",
                coord=(
                    pygame.display.play_dimensions_resize[0] + pygame.display.play_pos[0] + 25,
                    pygame.display.dimensions[1]*0.53)), #DEBUG
            Em(
                im="lives.png",
                coord=(
                    pygame.display.dimensions[0]*0.016,
                    pygame.display.dimensions[1] - anim.all_loaded_images['lives.png'].get_height() - 10)), #LIVES
            Em(
                im="weapon.png",
                coord=(
                    pygame.display.dimensions[0] - anim.all_loaded_images['weapon.png'].get_width() - 10,
                    pygame.display.dimensions[1] - anim.all_loaded_images['weapon.png'].get_height() - 10,)), #WEAPON
        ]
        for emblem in Border.emblems:
            Border.sprites.add(emblem)

        #06/25/2023 - giving corresponding images for num_coords
        Border.num_coords = (
            (pygame.display.dimensions[0],pygame.display.dimensions[1]*0.4,True), #Score
            (pygame.display.dimensions[0],pygame.display.dimensions[1]*0.53,True), #FPS
            (pygame.display.dimensions[0],pygame.display.dimensions[1]*0.58,True), #clock offset to be 60fps
            (pygame.display.dimensions[0],pygame.display.dimensions[1]*0.63,True), #offset fps 
        )

        Border.emblems[0].pattern = "jagged"
        

    

    def draw(self,window:pygame.Surface):
        # main graphics
        window.blit(self.UI_img,self.UI_rect)
        Border.sprites.draw(window)

        

        
    def draw_specific(self,window:pygame.Surface,lives:int,nums:tuple):
        for i in range(len(nums)):
            text.display_numbers(
                nums[i],
                (
                    Border.num_coords[i][0],
                    Border.num_coords[i][1]
                    ),
                window=window,
                reverse=Border.num_coords[i][2])

        # displaying lives
        self.display_lives(window=window, location = ( 95, Border.emblems[3].orig_coord[1], ) , lives = lives)
    

    def display_lives(self,window:pygame.Surface,location:tuple = (0,0),lives:int = 3):
        for i in range(lives):
            window.blit(anim.all_loaded_images["life.png"],(location[0] + i*38,location[1]))

    def update(self):
        if not self.animated:return 
        Border.sprites.update()
"""

""" THE PAUSE STATE
to be quite frank this was actually one of the better states here in terms of simplicity
however, it should be a menu sprite instead of its own state

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




"""


"""
EVERYTHING FROM BOSSES
EVERYTHING WAS TOO COMPLICATED
TOO COMPLEX
I HATED IT.
SO NOW HERE IT ALL GOES.
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
"""
