#CODE BY ANDREW CHURCH
import pygame,anim,random,emblems
from anim import all_loaded_images as img
from emblems import Emblem as Em
from backgrounds import Background as Bg
from text import display_numbers as dn
winrect = pygame.display.rect
xstart = pygame.display.play_dimensions_resize[0] + pygame.display.play_pos[0]
height = pygame.display.dimensions[1] 



class Border():
    sprites = pygame.sprite.Group()
    #define important emblems
    emblems = {
            "logo": Em(
                im = "logo.png",
                coord = (xstart,height*0)), #LOGO
            "score": Em(
                im="g_score.png",
                coord = (xstart,height*0.25)), #SCORE
            "debug": Em(
                im="g_debug.png",
                coord=(xstart,height*0.5)), #DEBUG
            "lives": Em(
                im="g_lives.png",
                coord=(xstart,height*0.3)), #LIVES
            "weapon": Em(
                im="weapon.png",coord=(xstart,height*0.4)), #WEAPON
            }
    #values to associate with the emblems
    values = {"logo":0,"score":0,"debug":0,"lives":0,"weapon":0,}
    #excluding for value draw
    exclude = ("logo","weapon")

    def __init__(self,window:pygame.Surface):
        #add emblems to sprite group
        self.window = window
        #assets for graphics
        self.bg = Bg(img="uibox.png",resize=self.window.get_size(),speed=(0.25,0),border_size=self.window.get_size())
        #adding emblem values
        Border.sprites.empty()
        for value in Border.emblems.values(): Border.sprites.add(value)

    def draw(self,*args,**kwargs):
        self.bg.draw(self.window)
        for sprite in Border.sprites:
            if not sprite.hide: 
                self.window.blit(sprite.image,sprite.rect)
        self.display_values()
        self.display_lives()
    
    def display_values(self):
        for k in Border.emblems.keys():
            if k not in Border.exclude and not Border.emblems[k].hide:
                dn(num=Border.values[k],pos=(Border.emblems[k].rect.right,Border.emblems[k].rect.top),window=self.window)
                
    
    def display_lives(self,*args,**kwargs):
        if Border.values['lives'] < 5 and not Border.emblems['lives'].hide:
            for i in range(Border.values['lives']):
                self.window.blit(img['life.png'], (Border.emblems['lives'].rect.right + i*35,  Border.emblems['lives'].rect.top))
    

    
    def update(self):
        self.bg.update()
        Border.sprites.update()

    def update_values(self,**kwargs):
        Border.values.update(kwargs)

    def change_vis(self,**kwargs):
        for k,v in kwargs.items():
            if k in Border.emblems:
                Border.emblems[k].hide = v
        

