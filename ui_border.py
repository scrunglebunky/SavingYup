#CODE BY ANDREW CHURCH
import pygame,anim,random,emblems,text
from anim import all_loaded_images as img
from emblems import Emblem as Em
from emblems import TextEmblem as TEm
from backgrounds import Background as Bg
winrect = pygame.display.rect
xstart = pygame.display.play_dimensions_resize[0] + pygame.display.play_pos[0]
height = pygame.display.dimensions[1] 



class Border():
    sprites = pygame.sprite.Group()
    spr_logo =  Em(im = "logo.png",coord = (xstart,height*0))
    spr_coins = Em(im="ui_coins.png", coord = (xstart,height*0.2))
    # spr_debug = Em(im="g_debug.png",coord=(xstart,height*0.5))
    spr_lives = Em(im="ui_lives.png",coord=(xstart,height*0.3))
    spr_weapon = Em(im="ui_weapon.png",coord=(xstart,height*0.4),resize=(128,128))
    spr_coins_text = TEm(txt="$0",coord=(xstart+64,height*0.2+32),font = text.terminalfont_30)
    spr_lives_text = TEm(txt="0",coord=(xstart+64,height*0.3+32),font=text.terminalfont_30)
    #adding sprites
    sprites.add(spr_logo,spr_coins,spr_lives,spr_weapon,spr_coins_text,spr_lives_text)
    # setting b g
    bg = Bg(img="empty",resize=(winrect.width,winrect.height),speed=(0.25,0))


    def __init__(self,window:pygame.Surface):
        #add emblems to sprite group
        self.fullwindow = window
        #assets for graphics

    def draw(self,*args,**kwargs):
        # Border.bg.draw(self.fullwindow)
        Border.sprites.draw(self.fullwindow)
    
    def update_gameinfo(self,player):
        self.spr_coins_text.update_text(str(player.coins))
        self.spr_lives_text.update_text(str(player.health))

    def update(self):
        # Border.bg.update()
        Border.sprites.update()

    def update_values(self,**kwargs):
        # Border.values.update(kwargs)
        ...

    def change_vis(self,hide=False,*args):
        for i in Border.sprites:
            if type(i) == Em or type(i) == TEm and i not in args:
                i.hide=hide

