import options,pygame,anim,text
from emblems import Emblem as Em
from emblems import TextEmblem as TEm
from backgrounds import Background as Bg

class Advance(pygame.sprite.Sprite):
    sprites = pygame.sprite.Group()
    spr_title = Em("advancetitle",coord=(200,30),isCenter=True,pattern="jagged")
    bg = Bg("bgADVANCE",resize=(400,400),speed=(10,10))

    def __init__(self,playstate):
        #pygame sprite stuff yada yada yaaaadaaaa
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((400,400)).convert_alpha()
        self.rect = self.image.get_rect()
        # now onto the juicy bits
        # pretty much, the advance menu flashes something telling you that you beat the world
        # gives you a "zone bonus", an "accuracy bonus", and then some random bonus like how many bullets you shot off or how many lives you have
        self.lifespan = 0
        self.active = False



    def update(self):
        Advance.bg.update()
        Advance.bg.draw(self.image)
        Advance.sprites.update()
        Advance.sprites.draw(self.image)