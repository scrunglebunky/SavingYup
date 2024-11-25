import pygame,os,player,text,random,formation,anim,audio,tools,events,score,enemies,enemies_bosses,shop
from anim import all_loaded_images as img
from anim import WhiteFlash
from text import display_numbers as dn
from text import text_list as tl
from backgrounds import Background as Bg
from backgrounds import Floor as Fl
from emblems import Emblem as Em
from emblems import TextEmblem  as TEm
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
                 oldshop:shop.Shop = None,
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


        #Creating a SHOP ASSET
        if oldshop == None:
            self.shop = shop.Shop(player=self.player)
        else:
            self.shop = oldshop
        #changing the shop's position
        self.shop.rect.center = pygame.display.rect.center









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

        

    
    def update(self, draw=True):
       


        ### INTERRUPT CODE -- THE SHOP 
        if self.shop.active:
            self.shop.update()
            # note that it re-draws the gameplay window for pretty much a special effect, and then draws the shop over it.
            self.fullwindow.blit(pygame.transform.scale(self.window,pygame.display.play_dimensions_resize),pygame.display.play_pos)
            self.fullwindow.blit(self.shop.image,self.shop.rect)
            # ending -- because the shop pauses
            return




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
        if self.formation.cleared and self.leveltimer > 15:
            self.new_level()

        #updating the wait timer
        elif self.formation.cleared:
            self.leveltimer += 1
        
        #08/21/2023 - Game Over - opening a new state if the player is dead
        if self.player.health <= 0:
            self.next_state = "title"
            #re-initializing itself
            self.__init__(window=self.fullwindow,oldshop=self.shop)

        # FINALLY DRAWING EVERYTHING TO THE SCREEN AT THE **END** BECAUSE IM NOT A PSYCHOPATH
        self.fullwindow.blit(pygame.transform.scale(self.window,pygame.display.play_dimensions_resize),pygame.display.play_pos)



    
    def on_start(self,**kwargs):#__init__ v2, pretty much.
        # emptying the bulletmaximum and making sure the player knows which sprite groups to refer to 
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
        self.background = Bg(bg, resize = (600,800), speed = (0,1))
        # also loading in the floor if it exists
        self.floor = Fl(
            image='floor-default',
            player=self.player,
            window=self.window,
            move=(.25,.25),
            scale=(800,800)
            ) 
        # print(self.floor.image, self.floor.rect.center, self.floor.hide)

    def new_zone(self,shop=True):
        # new zone code
        GPI.unlock_enemy(playstate=self)
        GPI.unlock_bg(playstate=self)
        if shop: self.shop.new_shop()


        
    
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

        if self.level%5 == 0:
            self.new_zone()
        elif self.level in (1,2,3):
            self.new_zone(False)

    def event_handler(self,event):
        # INTERRUPT CODE -- SHOP.ACTIVE
        if self.shop.active:
            self.shop.event_handler(event)
            return
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
# THIS ALSO HAS TO BE UPDATED
# USE THE EMBLEMS I GAVE YOU DAMNIT
class Title(Template):
    emblems = {}
    emblems_perm = {}
    sprites=pygame.sprite.Group()
    em_continue = TEm(txt="PRESS Z TO CONTINUE\nARROW KEYS MOVE, Z SHOOTS, X CHANGES WEAPON")

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
        Title.em_continue.change_pos((winrect.centerx,winrect.bottom*.8),isCenter=True)

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

        Title.em_continue.update()

        self.window.blit(Title.em_continue.image,Title.em_continue.rect)
        
        # self.window.blit(self.hiscoresheet,self.image_placements['score'])
        
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






