# DO LATER
import pygame,text
from emblems import Emblem as Em
from emblems import TextEmblem as TEm
from backgrounds import Background as Bg
# Pause menu class
# it has a background and a little picture of yup sitting there at a couch
# it tells you to press esc to unpause
# or press x to go to settings
# or to press c to quit


class Pause(pygame.sprite.Sprite):
    sprites = pygame.sprite.Group()
    bg = Bg("bgPAUSE",resize=(400,400),speed=(1,1))
    spr_text = TEm("PAUSED\nESC: UNPAUSE\nX: OPTIONS\nC: QUIT",font=text.terminalfont_20,hide=False)
    spr_pauseplayer = Em("pauseplayer",coord=(200,200),isCenter=True)
    sprites.add(spr_text,spr_pauseplayer)

    def __init__(self,playstate):
        pygame.sprite.Sprite.__init__(self)
        self.playstate=playstate
        self.image = pygame.Surface((400,400)).convert_alpha()
        self.rect = self.image.get_rect()
        self.active = False


    def update(self):
        Pause.bg.update()
        Pause.bg.draw(self.image)
        Pause.sprites.update()
        Pause.sprites.draw(self.image)
        

    def start(self):
        self.active = True
        self.rect.center = (pygame.display.rect.centerx + random.randint(-60,60), pygame.display.rect.centery + random.randint(-60,60))

    def event_handler(self,event):
        match event.type:
            case pygame.KEYDOWN:
                match event.key:
                    case pygame.K_ESCAPE:
                        self.active = False
                    case pygame.K_x:
                        self.playstate.options.start()
                    case pygame.K_c:
                        self.playstate.end()
