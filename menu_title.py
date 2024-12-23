# DO LATER
import pygame,text,random,audio
from emblems import Emblem as Em
from emblems import TextEmblem as TEm
from backgrounds import Background as Bg
from menu import Menu

# Title joins the Menu classes as i consolidate all the previous states into one!
# I wish the me from a year ago was smart enough to do all this but whatever!
class Title(Menu):
    sprites = pygame.sprite.Group()
    bg = Bg("title_image.jpg",resize=(400,400),speed=(1,1))
    # spr_text = TEm("PAUSED\nESC: UNPAUSE\nX: OPTIONS\nC: QUIT",font=text.terminalfont_20,hide=False)
    # spr_pauseplayer = Em("pauseplayer.png",coord=(200,200),isCenter=True)
    # sprites.add(spr_text,spr_pauseplayer)
    # options
    options = ['PLAY','LORE','ABOUT','HIGHSCORES','OPTIONS','QUIT']
    # sprites
    spr_options = [ ] 
    for i in range(len(options)):
        spr_options.append(
            TEm(
                txt=str(options[i]),
                coord=(200,200+i*25),isCenter=True,
                font=text.terminalfont_20
            )
        )
    spr_title = Em(im="logo.png",coord=(200,100),isCenter=True,pattern="sine",resize=(200,150))
    spr_cursor = TEm(txt=">",coord=(spr_options[0].rect.left-20,spr_options[0].rect.centery),isCenter=True,pattern="jagged",font=text.terminalfont_20)
    sprites.add(spr_options,spr_title,spr_cursor)

    def __init__(self,playstate):
        pygame.sprite.Sprite.__init__(self)
        # basic info used everywhere else for the image and activity and such
        self.playstate=playstate
        self.image = pygame.Surface((400,400)).convert_alpha()
        self.rect = self.image.get_rect()
        self.active = False
        # info used for the menus, also used elsewhere
        self.index = 0 



    def update(self):
        Title.bg.update()
        Title.bg.draw(self.image)
        Title.sprites.update()
        Title.sprites.draw(self.image)
        

    def payload(self):
        # this runs the selected option
        match Title.options[self.index].lower():
            case 'play':
                self.playstate.add_queue('gameplay')
                self.end()
            case 'lore':
                self.playstate.add_queue('lore')
                self.playstate.add_queue('title')
                self.end()
            case 'options':
                self.playstate.add_queue('options')
                self.playstate.add_queue('title')
                self.end()
            case 'quit':
                self.playstate.add_queue('quit')
                self.end()

    
    def change_index(self,val:int):
        self.index += val
        Title.spr_cursor.change_pos(pos=(Title.spr_options[self.index].rect.left-20,Title.spr_options[self.index].rect.centery),isCenter=True)
        


    def start(self):
        self.active = True
        self.rect.center = (pygame.display.rect.centerx + random.randint(-60,60), pygame.display.rect.centery + random.randint(-60,60))
        # audio.play_song("kurosaki.mp3")

    def event_handler(self,event):
        match event.type:
            case pygame.KEYDOWN:
                match event.key:
                    case pygame.K_UP:
                        if self.index > 0:
                            self.change_index(-1)
                    case pygame.K_DOWN:
                        if self.index < len(Title.options)-1:
                            self.change_index(1)
                    case pygame.K_z:
                        self.payload()
                    case pygame.K_ESCAPE:
                        self.end()



# HIGH SCORE SCREEEN SUBMENU
class HighScoreScreen(Menu):...
# ABOUT SCREEN SUBMENU
class AboutScreen(Menu):...

