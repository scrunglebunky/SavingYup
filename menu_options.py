import options,pygame,anim,text
from emblems import Emblem as Em
from emblems import TextEmblem as TEm
from backgrounds import Background as Bg



class Options(pygame.sprite.Sprite):
    # sprite stuff
    sprites = pygame.sprite.Group()
    bg = Bg("bgOPTIONS",resize=(400,400),speed=(-1,1))
    spr_title = TEm("OPTIONS MENU",coord=(200,20),isCenter=True,pattern="jagged")
    spr_cursor = TEm("<",coord=(0,0))
    spr_guide = TEm("ARROW KEYS TO SET\nZ: APPLY\nX: DEFAULTS\nESC: LEAVE",coord=(0,300),font=text.terminalfont_20)
    sprites.add(spr_title,spr_cursor,spr_guide)
    # holder for options text
    options_text = {}
    for option in options.settings.keys():
        options_text[option] = text.load_text(option,font=text.terminalfont_20)
    options_list = list(options.settings.keys())
    
    def __init__(self,playstate):
        pygame.sprite.Sprite.__init__(self)
        self.playstate = playstate
        self.image = pygame.Surface((400,400)).convert_alpha()
        self.rect = self.image.get_rect()
        self.active = False
        self.index = 0

    def draw_options(self):
        y=0
        for key,value in options.settings.items():
            #displaying setting icons
            self.image.blit(Options.options_text[key],(0,50+(35*y)))
            
            #displaying what is currently configured
            if value[0] == "knob":
                text.display_numbers(str(value[1]*100)+"%",(200,50+(35*y)),window=self.image)
            elif value[0] == "switch":
                self.image.blit(
                    anim.all_loaded_images["on.png" if value[1] else "off.png"],
                    (200,50+(35*y))
                    )

            y+=1
    

    def update(self):
        # setting cursor stuff
        Options.spr_cursor.change_pos((300,50+(35*self.index)))

        # updating, moving etc
        Options.bg.update()
        Options.sprites.update()
        Options.bg.draw(self.image)
        Options.sprites.draw(self.image)
        self.draw_options()

    
    def start(self):
        self.active = True
        self.rect.center = (pygame.display.rect.centerx + random.randint(-60,60), pygame.display.rect.centery + random.randint(-60,60))

    
    def event_handler(self,event):
        match event.type:
            case pygame.KEYDOWN:
                match event.key:
                    case pygame.K_UP:  
                        self.index -= 1
                        if self.index < 0:
                            self.index = len(Options.options_list)
                    case pygame.K_DOWN:
                        self.index += 1
                        if self.index >= len(Options.options_list):
                            self.index = 0
                    case pygame.K_LEFT:
                        cur_option = options.settings[Options.options_list[self.index]] 
                        if cur_option[0] == "switch":
                            cur_option[1] = not cur_option[1]
                        elif cur_option[0] == "knob":
                            cur_option[1] -= cur_option[2] if len(cur_option) >= 3 else .1
                            cur_option[1] = round(cur_option[1],2)
                    case pygame.K_RIGHT:
                        cur_option = options.settings[Options.options_list[self.index]]   
                        if cur_option[0] == "switch":
                            cur_option[1] = not cur_option[1]
                        elif cur_option[0] == "knob":
                            cur_option[1] += cur_option[2] if len(cur_option) >= 3 else .1
                            cur_option[1] = round(cur_option[1],2)

                    case pygame.K_z:
                        options.apply_settings()
                    case pygame.K_x:
                        options.restore_defaults()
                    case pygame.K_ESCAPE:
                        self.active = False