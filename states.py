import pygame,os,player,text,random,formation,anim,audio,tools,events,score,enemies,enemies_bosses
import menu_shop as shop
from anim import all_loaded_images as img
from anim import WhiteFlash
from text import display_numbers as dn
from backgrounds import Background as Bg
from backgrounds import Floor as Fl
from emblems import Emblem as Em
from emblems import TextEmblem  as TEm
from bullets import emptyBulletMax as eBM
from bullets import BulletParticle as BP
from math import sin
from player import PlayerDummy as PD
from levels import worlds 
from menu_gameplay import GamePlay as GP
from menu_gameplay import GamePlayUI as GPUI
from menu_gameover import GameOver as GO
from menu_pause import Pause
from menu_options import Options
from menu_lore import Lore

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

    


    def __init__(self,
                 window:pygame.display,
                 border,
                 level:int = 0,
                 oldshop:shop.Shop = None,
                 #is_demo:bool=False, #a way to check if the player is simulated or not
                 ):


        self.next_state = None #Needed to determine if a state is complete
        self.window = window
        self.border = border

        # MENU ASSETS
        # THIS IS THE NEW WAY THAT PLAYSTATE RUNS
        # THE GAMEPLAY, GAMEOVER, SHOP, PAUSE, AND SETTINGS ARE ALL "ASSETS" LIKE THIS
        # NOTE THAT THESE CAN **CONTROL PLAYSTATE** BY CALLING FUNCTIONS. IF PLAYSTATE ENDS OR CHANGES AND YOU DON'T SEE WHY, ONE OF THESE ASSETS DID SOMETHING TO IT.

        #Creating a GAMEPLAY ASSET, which holds all GAMEPLAY INFO in a SPRITE
        self.gameplay = GP(self)
        self.gameplayui = GPUI(self)
        self.player = self.gameplay.player
        self.gameplay.start()
        self.gameplayui.start()

        #Creating a SHOP ASSET
        self.shop = shop.Shop(player=self.player) if oldshop is None else oldshop

        #Creating a GAMEOVER asset
        self.gameover = GO(self)

        #creating a PAUSE asset
        self.pause = Pause(self)

        #creating a OPTIONS asset
        self.options = Options(self)
        
        #creating a LORE asset, which will only start when the game first starts
        self.lore = Lore(self)
        self.lore.start()

        #debug
        # self.shop.start(True)

    def update(self, draw=True):
        ### INTERRUPT CODE -- OPTIONS MENU
        if self.options.active:
            self.options.update()
            self.window.blit(self.options.image,self.options.rect)
            return

        ### INTERRUPT CODE -- PAUSING
        if self.pause.active:
            self.pause.update()
            self.window.blit(self.pause.image,self.pause.rect)
            return

        ### INTERRUPT CODE -- THE GAMEOVER
        if self.gameover.active:
            self.gameover.update()
            self.window.blit(self.gameover.image,self.gameover.rect)
            return

        ### INTERRUPT CODE -- THE LORE SCREEN
        if self.lore.active:
            self.lore.update()
            self.window.blit(self.lore.image,self.lore.rect)
            return

        ### INTERRUPT CODE -- THE SHOP 
        if self.shop.active:
            self.shop.update()
            # note that it re-draws the gameplay window for pretty much a special effect, and then draws the shop over it.
            self.window.blit(self.shop.image,self.shop.rect)
            # ending -- because the shop pauses
            return


        # RUNNING THE GAMEPLAY
        if self.gameplay.active:
            self.gameplay.update()
            self.gameplayui.update()
            self.window.blit(pygame.transform.scale(self.gameplay.image,pygame.display.play_dimensions_resize),self.gameplay.rect)
            self.window.blit(self.gameplayui.image,self.gameplayui.rect)


    def on_start(self,**kwargs):#__init__ v2, pretty much.
        # emptying the bulletmaximum and making sure the player knows which sprite groups to refer to 
        # self.player.sprite_groups = self.sprites
        # self.border.spr_logo.change_pos(pos = (pygame.display.play_dimensions_resize[0],winrect.height*0.05),isCenter=False)
        # self.border.change_vis(False)
        # eBM()
        ...



    def on_end(self,**kwargs): #un-init, kind of
        pygame.mixer.music.stop()
        # if tools.debug: print(self.debug.values())
        # eBM()


    def event_handler(self,event):
        # INTERRUPT CODE -- OPTIONS.ACTIVE
        if self.options.active:
            self.options.event_handler(event)
            return
        # INTERRUPT CODE -- PAUSE.ACTIVE
        if self.pause.active:
            self.pause.event_handler(event)
            return
        # INTERRUPT CODE -- GAMEOVER.ACTIVE
        if self.gameover.active:
            self.gameover.event_handler(event)
            return
        # INTERRUPT CODE -- LORE.ACTIVE
        if self.lore.active:
            self.lore.event_handler(event)
            return
        # INTERRUPT CODE -- SHOP.ACTIVE
        if self.shop.active:
            self.shop.event_handler(event)
            return
        #if self.is_demo: return
        if self.gameplay.active: 
            self.gameplay.event_handler(event)
        #changing what comes next
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                # self.next_state = "options"
                ...
            if tools.debug: 
                ...
        # if event.type == pygame.MOUSEBUTTONDOWN and tools.debug:
        #     pos = tuple(pygame.mouse.get_pos())
        #     pos = [pos[0]-pygame.display.play_pos[0],pos[1]-pygame.display.play_pos[0]]
        #     pos2 = [pygame.display.play_dimensions_resize[0]-pos[0],pos[1]]
        #     self.debug[0].append(pos)
        #     self.debug[1].append(pos2)
        #     print(pos,pos2)


    def end(self,next_state:str="title"):
        self.__init__(window=self.window,oldshop=self.shop,border=self.border)
        self.next_state = next_state







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











