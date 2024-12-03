import options,pygame,anim,text,random
from emblems import Emblem as Em
from emblems import TextEmblem as TEm
from backgrounds import Background as Bg
import gameplay_log as log

class Advance(pygame.sprite.Sprite):
    sprites = pygame.sprite.Group()
    spr_title = Em("advancetitle.png",coord=(200,50),isCenter=True,pattern="jagged")
    spr_resultgraphic = TEm(txt="",coord=(0,200),font=text.terminalfont_20)
    sprites.add(spr_title,spr_resultgraphic)
    bg = Bg("bgPAUSE",resize=(400,400),speed=(10,10))

    def __init__(self,playstate):
        #pygame sprite stuff yada yada yaaaadaaaa
        pygame.sprite.Sprite.__init__(self)
        self.playstate = playstate
        self.image = pygame.Surface((400,400)).convert_alpha()
        self.rect = self.image.get_rect()
        # now onto the juicy bits
        # pretty much, the advance menu flashes something telling you that you beat the world
        # gives you a "zone bonus", an "accuracy bonus", and then some random bonus like how many bullets you shot off or how many lives you have
        self.lifespan = 0
        self.active = False
        self.resultsheet = []
        self.bonuses = {

        }
        self.displayed = ""
        



    def update(self):
        Advance.bg.update()
        Advance.bg.draw(self.image)
        Advance.sprites.update()
        Advance.sprites.draw(self.image)

        # uppdating the graphic text
        self.lifespan += 1
        if self.lifespan % 60 == 0:
            self.displayed = ""
            for i in range(self.lifespan // 60):
                if i < len(self.resultsheet):
                    self.displayed += self.resultsheet[i]
                    Advance.spr_resultgraphic.update_text(self.displayed)
                else:
                    # note that since a new level starts
                    # it will run the newlevel thing itself
                    # to prevent the sounds from overlapping
                    self.active = False



    def start(self):
        self.bonuses = {}
        # generating and applying bonuses prematurely
        self.generate_bonuses_and_text()
        self.apply_bonuses()
        # resetting info
        self.lifespan = 0
        self.active = True
        # resetting some sprites
        Advance.spr_resultgraphic.update_text("")
        # updating rect
        self.rect.center = (pygame.display.rect.centerx + random.randint(-60,60), pygame.display.rect.centery + random.randint(-60,60))


    def generate_bonuses_and_text(self) -> list:
        out = ["YOU BEAT A ZONE!"]
        #accuracy bonus information
        accuracy = round(((log.log_total['hits']/log.log_zone['shots']) if log.log_zone['shots'] is not 0 else 1) ,2)
        accuracybonus = accuracy * 1000 * self.playstate.gameplay.difficulty
        out.append( "\nACCURACY BONUS: " + str(accuracy*100) + "% * 100 * " + str(self.playstate.gameplay.difficulty) + " = " + str(accuracybonus))
        self.bonuses["accuracy"] = accuracybonus
        #kills bonus information
        killbonus = log.log_zone['kills']*50*self.playstate.gameplay.difficulty
        out.append("\nKILL BONUS: " + str(log.log_zone["kills"]) + " * 50 * " + str(self.playstate.gameplay.difficulty) + " = " + str(killbonus))
        self.bonuses['kill'] = killbonus
        #ouch bonus information
        ouchbonus = log.log_zone['damage'] * 100 * self.playstate.gameplay.difficulty
        out.append( "\nOUCH BONUS: " + str(log.log_zone["damage"]) + "* 100 * " + str(self.playstate.gameplay.difficulty) + " = " + str(ouchbonus))
        self.bonuses['ouch'] = ouchbonus
        out.append( "\nSCORE BEFORE: " + str(self.playstate.player.coins))
        out.append( "\nSCORE AFTER: " + str(self.playstate.player.coins + sum([bonus for bonus in self.bonuses.values()])))
        out.append( "\nWORLD RANK: " + "GROOVY!") #MAKE THIS CHANGE LATER
        out.append( "\nOKAY BYE") #MAKE THIS CHANGE LATER
        self.resultsheet = out

    def apply_bonuses(self):
        self.playstate.player.coins += round(sum([bonus for bonus in self.bonuses.values()]),0)

    
    def event_handler(self,event):
        match event.type:
            case pygame.KEYDOWN:
                self.lifespan += 60 - (self.lifespan % 60) - 1
                self.update()