import json,pygame,random,text,player,enemies,audio,formation,score
from emblems import Emblem as Em
from emblems import TextEmblem as TEm
from backgrounds import Background as Bg
from audio import play_sound as psound
from audio import play_song as psong
from backgrounds import Floor as Fl
import gameplay_log as log

class GameOver(pygame.sprite.Sprite):
    sprites = pygame.sprite.Group()
    bg = Bg("bgGAMEOVER",resize=(400,400),speed=(0,-5))

    bg2 = Bg("bgGAMEOVER_2.png",resize=(400,400),speed=(0,0))
    spr_playergraphic = Em("gameoverplayer",coord=(200,0),isCenter=True,pattern="jagged")
    spr_resultgraphic = TEm("",coord=(0,0),font=text.terminalfont_20)
    sprites.add(spr_playergraphic,spr_resultgraphic)

    def __init__(self,playstate):
        self.image = pygame.Surface((400,400)).convert_alpha()
        self.rect = self.image.get_rect()
        self.playstate = playstate
        self.active = False
        self.lifespan = 0 
        self.resultsheet = []
        self.displayed = ""
        self.got_highscore = False

    def start(self):
        self.lifespan = 0 
        self.active = True
        # creating a tween so the player slowly falls
        GameOver.spr_playergraphic.tweens["move"] = []
        GameOver.spr_playergraphic.add_tween_pos(cur_pos=GameOver.spr_playergraphic.rect.center,target_pos = (GameOver.spr_playergraphic.rect.centerx,500), speed=0.5, started=True,isCenter = True)
        # high score information
        self.got_highscore = score.check_score(self.playstate.player.coins)
        if self.got_highscore: score.add_score(self.playstate.player.coins,name="YOU!")
        # finishing the log
        log.log_push()
        self.generate_resultsheet()
        self.displayed = "" 

    def update(self):
        # updating/displaying sprites
        GameOver.sprites.update()
        GameOver.bg.update()
        GameOver.bg2.draw(self.image)
        GameOver.bg.draw(self.image)
        GameOver.sprites.draw(self.image)

        # uppdating the graphic text
        self.lifespan += 1
        if self.lifespan % 60 == 0:
            self.displayed = ""
            for i in range(self.lifespan // 60):
                if i < len(self.resultsheet):
                    self.displayed += self.resultsheet[i]
                    GameOver.spr_resultgraphic.update_text(self.displayed)


    def generate_resultsheet(self) -> list:
        out = ["GAME OVER!"]
        out.append( "\nSHOTS: " + str(log.log_total["shots"]))
        out.append( "\nHITS: " + str(log.log_total["hits"]))
        out.append( "\nACCURACY: " + (str(round((log.log_total['hits']/log.log_total['shots'])*100,2))+"%" if log.log_total["shots"] is not 0 else "N/A"))
        out.append( "\nKILLS: " + str(log.log_total["kills"]))
        out.append( "\nDAMAGE TAKEN: " + str(log.log_total["damage"]))
        out.append( "\nFINAL SCORE: " + str(self.playstate.player.coins))
        if self.got_highscore: out.append("\nYOU GOT A HIGH SCORE!")
        out.append( "\nFINAL RANK: " + "GROOOOOOOOVY!") #MAKE THIS CHANGE LATER
        out.append( "\nPRESS ANY KEY TO CONTINUE") #MAKE THIS CHANGE LATER
        self.resultsheet = out


    def event_handler(self,event):
        match event.type:
            case pygame.KEYDOWN:
                if self.lifespan > 60:
                    self.playstate.end("title")
  