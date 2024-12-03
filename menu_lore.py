import options,pygame,anim,text,random
from emblems import Emblem as Em
from emblems import TextEmblem as TEm
from backgrounds import Background as Bg
from menu import Menu

class Lore(Menu):
    #same sprite group stuff
    sprites = pygame.sprite.Group()
    spr_text = TEm("BASE DIALOG",coord=(0,250))
    spr_images = Em("loreimages",coord=(0,0),resize=(400,250),current_anim="0")
    sprites.add(spr_images,spr_text)
    #lore/text info
    textlist = [
        "THE EVIL NOPES\nARE TRYING TO TAKE OVER","THE YUP'S HOME PLANET",
        "YUP SEES THEM OUT\nOF HER HOUSE AND IS LIKE","\n \"WOW I NEED TO STOP THAT\"",
        "SHE BLASTS OFF\nEQUIPPED WITH HER YUP GUN\nREADY TO DEFEND",
        "ITS UP TO YOU\nTO KILL THEM.\nGO!!!!!!!!!!!",
    ]

    def __init__(self,playstate):
        pygame.sprite.Sprite.__init__(self)
        #sprite/parameter info
        self.playstate = playstate
        self.image = pygame.Surface((400,400)).convert_alpha()
        self.rect = self.image.get_rect()
        #info
        self.active = False
        self.finished = False
        self.index = 0 
        # setting the image/text
        Lore.spr_text.update_text(Lore.textlist[self.index])
        Lore.spr_images.aimg.change_anim(str(self.index))

    def update(self):
        self.image.fill("black")
        Lore.sprites.update()
        Lore.sprites.draw(self.image)

    def start(self):
        self.__init__(self.playstate)
        self.active = True
        self.rect.center = (pygame.display.rect.centerx + random.randint(-60,60), pygame.display.rect.centery + random.randint(-60,60))

    
    def newframe(self):
        self.index += 1
        #checking if over
        if self.index >= (len(Lore.textlist)):
            self.active = False
            self.finished = True
        # updating the image, indexing info
        else:
            Lore.spr_text.update_text(Lore.textlist[self.index])
            Lore.spr_images.aimg.change_anim(str(self.index))

    def event_handler(self,event):
        match event.type:
            case pygame.KEYDOWN:
                self.newframe()