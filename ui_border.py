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
        if Border.values['lives'] < 25 and not Border.emblems['lives'].hide:
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
        


#06/22/2023 - UI BAR CLASS
# The UI bar is something used by playstate to display things such as the score, background image, and logo.

# class BorderOld():
    
#     #06/24/2023 - Adding EMBLEMS, which are just different UI symbols to add
#     emblems = [ ]

#     #06/25/2023 - items to go with emblems
#     # So, there are all of the emblems that show where the score values should go, right?
#     # Well this is going to be the same thing but a little more specific.
#     # This will be a tuple filled with coordinates
#     # Main will then feed in another tuple filled with specific number assets to feed into these positions
#     num_coords = ()
#     sprites = pygame.sprite.Group() #all sprites used in the state

#     def __init__(self,
#         anim_bg:bool = True,
#         anim_logo:bool = True,
#         UI_art:str = "uibox.png",
#         ):

#         #06/03/2023 - UI - Making a separate brick to the right with highest graphical priority used as a backgorund for the UI
#         self.UI_art = UI_art
#         self.UI_rect = pygame.Rect(0,0,pygame.display.dimensions[0],pygame.display.dimensions[1])
#         self.UI_img = pygame.Surface(pygame.display.dimensions)
#         self.UI_img.blit(pygame.transform.scale(anim.all_loaded_images[self.UI_art],(self.UI_rect[2],self.UI_rect[3])),(0,0))

#         #06/22/2023 - Animation booleans / setting spritesheet info
#         self.anim_bg:bool = anim_bg
#         self.anim_logo:bool = anim_logo
#         self.animated = self.anim_bg or self.anim_logo


#         #06/30/2023 - filling dynamic image sizes for the emblems
#         #06/24/2023 - Adding EMBLEMS, which are just different UI symbols to add
#         Border.sprites.empty()
#         Border.emblems = [
#             Em(
#                 im = "logo.png",
#                 coord = (
#                     pygame.display.dimensions[0] - ( pygame.display.dimensions[0] - (pygame.display.play_dimensions_resize[0] + pygame.display.play_pos[0])),
#                     pygame.display.dimensions[1]*0.15 - (anim.all_loaded_images['logo.png'].get_height()/2))), #LOGO
#             Em(
#                 im="score.png",
#                 coord = (
#                     pygame.display.play_dimensions_resize[0] + pygame.display.play_pos[0] + 25,
#                     pygame.display.dimensions[1]*0.4)), #SCORE
#             Em(
#                 im="debug.png",
#                 coord=(
#                     pygame.display.play_dimensions_resize[0] + pygame.display.play_pos[0] + 25,
#                     pygame.display.dimensions[1]*0.53)), #DEBUG
#             Em(
#                 im="lives.png",
#                 coord=(
#                     pygame.display.dimensions[0]*0.016,
#                     pygame.display.dimensions[1] - anim.all_loaded_images['lives.png'].get_height() - 10)), #LIVES
#             Em(
#                 im="weapon.png",
#                 coord=(
#                     pygame.display.dimensions[0] - anim.all_loaded_images['weapon.png'].get_width() - 10,
#                     pygame.display.dimensions[1] - anim.all_loaded_images['weapon.png'].get_height() - 10,)), #WEAPON
#         ]
#         for emblem in Border.emblems:
#             Border.sprites.add(emblem)

#         #06/25/2023 - giving corresponding images for num_coords
#         Border.num_coords = (
#             (pygame.display.dimensions[0],pygame.display.dimensions[1]*0.4,True), #Score
#             (pygame.display.dimensions[0],pygame.display.dimensions[1]*0.53,True), #FPS
#             (pygame.display.dimensions[0],pygame.display.dimensions[1]*0.58,True), #clock offset to be 60fps
#             (pygame.display.dimensions[0],pygame.display.dimensions[1]*0.63,True), #offset fps 
#         )

#         Border.emblems[0].pattern = "jagged"
        

    

#     def draw(self,window:pygame.Surface):
#         # main graphics
#         window.blit(self.UI_img,self.UI_rect)
#         Border.sprites.draw(window)

        

        
#     def draw_specific(self,window:pygame.Surface,lives:int,nums:tuple):
#         for i in range(len(nums)):
#             text.display_numbers(
#                 nums[i],
#                 (
#                     Border.num_coords[i][0],
#                     Border.num_coords[i][1]
#                     ),
#                 window=window,
#                 reverse=Border.num_coords[i][2])

#         # displaying lives
#         self.display_lives(window=window, location = ( 95, Border.emblems[3].orig_coord[1], ) , lives = lives)
    

#     def display_lives(self,window:pygame.Surface,location:tuple = (0,0),lives:int = 3):
#         for i in range(lives):
#             window.blit(anim.all_loaded_images["life.png"],(location[0] + i*38,location[1]))

#     def update(self):
#         if not self.animated:return 
#         Border.sprites.update()
