import options,pygame,anim,text,random
from emblems import Emblem as Em
from emblems import TextEmblem as TEm
from backgrounds import Background as Bg
import gameplay_log as log
from audio import play_sound as psound
from menu import Menu

class NewLevel(Menu):
    sprites = pygame.sprite.Group()
    spr_level = Em("newlevel_level.png",coord=(0,0),pattern="jagged")
    spr_level_number = TEm("0",coord=(200,0),resize=(100,100))
    sprites.add(spr_level,spr_level_number)
    bg = Bg("bgPAUSE",(300,300),(5,5))

    def __init__(self,playstate,endtime:int=60):
        # basic pygame.sprite stuff
        self.image = pygame.Surface((300,100)).convert_alpha()
        self.rect = self.image.get_rect()
        # playstate argument
        self.playstate = playstate
        """WHAT DOES NEWLEVEL DO
        This is run AFTER THE LEVEL INFORMATION IS UPDATED
        This is run BEFORE THE NEXT LEVEL ACTUALLY STARTS
        It runs for about 120 frames, plays a sound, yada yada
        This is purely graphical, and does not modify any values."""
        # timer for how long this lasts + active info
        self.active = False
        self.lifespan = 0
        self.endtime = endtime
    
    def update(self):
        # updating the timer
        self.lifespan += 1
        if self.lifespan >= self.endtime:
            self.end()
        # basic sprite + draw stuff
        NewLevel.bg.update()
        NewLevel.bg.draw(self.image)
        NewLevel.sprites.update()
        NewLevel.sprites.draw(self.image)
        
        


    def start(self,endtime:int=60):
        # resets the lifespan timer 
        self.lifespan = 0
        self.active = True
        self.endtime = endtime
        # updates the level number
        NewLevel.spr_level_number.update_text(str(self.playstate.gameplay.level))
        # plays a sound
        # psound("tada.mp3")
        # positioning
        self.rect.center = (pygame.display.rect.centerx + random.randint(-60,60), pygame.display.rect.centery + random.randint(-60,60))

    
    def event_handler(self,event):
        ...