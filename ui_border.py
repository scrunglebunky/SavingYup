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

    bg = Bg(img="bgBORDER",resize=(winrect.width,winrect.height),speed=(0.25,0))


    def __init__(self,window:pygame.Surface):
        #add emblems to sprite group
        self.fullwindow = window
        #assets for graphics

    def draw(self,*args,**kwargs):
        Border.bg.draw(self.fullwindow)
        Border.sprites.draw(self.fullwindow)
    
    def update_gameinfo(self,player):
        # self.spr_coins_text.update_text(str(player.coins))
        # self.spr_lives_text.update_text(str(player.health))
        ...

    def update(self):
        Border.bg.update()
        Border.sprites.update()

    def update_values(self,**kwargs):
        # Border.values.update(kwargs)
        ...

    def change_vis(self,hide=False,*args):
        for i in Border.sprites:
            if type(i) == Em or type(i) == TEm and i not in args:
                i.hide=hide

