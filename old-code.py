"""OLD CODE -- WHAT COULD HAVE BEEN
HERE I POST A LOT OF OLDER PIECES OF CODE WITH A LITTLE DESCRIPTION ON TOP OF WHAT IT DID
SADLY I REMOVED MOST OF THE OLD CODE SO THIS IS RATHER EMPTY."""


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