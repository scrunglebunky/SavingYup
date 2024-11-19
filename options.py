## CODE BY ANDREW CHURCH
import json,text,pygame,random,audio,tools

#07/04/2023 - ADDING OPTIONS MENU
# The options menu is going to iterate through everything in the settings dictionary and let people modify it with the menu buttons

#06/30/2023 - LOADING IN THE CONFIGURATION FILE
# The config.json file is a dictionary containing info about how the game works
# This file is needed, though there is a default dictionary held here 
# This is held in the options file instead of MAIN, so all items can access it
settingsDEFAULT = {
    "fullscreen":["switch",False],

    "mute":["switch",False],
    "music_vol":["knob",0.5,0.05],
    "sound_vol":["knob",0.5,0.05],

    "screen_width":["knob",900,5],
    "screen_height":["knob",675,5],
    "gameplay_width":["knob",450,5],
    "gameplay_height":["knob",600,5],

    "moving_backgrounds":["switch",True]
}
# loading in the file
with open("./data/config.json","r") as set_raw:
    settings = settingsDEFAULT.copy()
    settings.update(json.load(set_raw)) #this then merges all settings with the default settings
del set_raw

pygame.display.dimensions = (settings["screen_width"][1],settings["screen_height"][1]) 
pygame.display.play_dimensions_resize = (settings["gameplay_width"][1],settings["gameplay_height"][1])
pygame.display.set_mode(pygame.display.dimensions, pygame.SCALED)

#07/13/2023 - finishing the rest of the imports now that the settings are complete
import anim

#07/13/2023 - This actually applies the settings 
def apply_settings(border = None):
    #display
    pygame.display.dimensions = (settings["screen_width"][1],settings["screen_height"][1]) 
    pygame.display.play_dimensions_resize = (settings["gameplay_width"][1],settings["gameplay_height"][1])
    # print(pygame.display.dimensions)
    pygame.display.set_mode(pygame.display.dimensions, pygame.SCALED if not settings['fullscreen'][1] else pygame.FULLSCREEN|pygame.SCALED)
    #sounds
    audio.change_volumes(ostvol = settings["music_vol"][1] , soundvol = settings["sound_vol"][1])
    if settings["mute"][1]: audio.change_volumes(ostvol = 0 , soundvol = 0)
    #fixing ui bar
    if border is not None: border.__init__(window=border.window)
    #writing data
    with open("./data/config.json","w") as data:
        data.write(json.dumps(settings))
apply_settings()


#SETTINGS (KNOB) INDEX MEANINGS:
# [type,current_setting,iteration_amount,min,max]

#07/13/2023 - Adding each individual text asset to the text module
for item in settings.keys():
    text.loaded_text[str(item)] = pygame.font.Font("./data/font.ttf",30)
    text.loaded_text[str(item)] = text.loaded_text[str(item)].render(str(item),False,"white","black")
    text.loaded_text[str(item)] = pygame.transform.scale(text.loaded_text[str(item)], (150,text.loaded_text[str(item)].get_height()))

text.loaded_text["PRESS P TO APPLY"] = pygame.font.Font("./data/font.ttf",30)
text.loaded_text["PRESS P TO APPLY"] = text.loaded_text["PRESS P TO APPLY"].render("PRESS P TO APPLY",False,"white","black")

class State():    

    def __init__(self,window:pygame.Surface,border):
        self.next_state = None #Needed to determine if a state is complete
        self.return_state = "title" #so the state knows what specifically to return to upon exit - specific to options

        self.window=window
        self.pos = 0
        self.keys = tuple(settings.keys())
        self.settings = settings

        self.disp_pos = pygame.display.play_pos[0]+50,pygame.display.play_pos[1]+150 
        self.apgr_pos = (100,500)
        self.logo_pos = (50,25)

        self.border = border

    def on_start(self,return_state:str="title",**kwargs): #__init__ v2, pretty much.
        self.return_state = return_state
        if tools.demo: #auto exit for demo
            self.next_state = self.return_state

    def on_end(self,**kwargs):... #un-init, kind of
    

    def update(self):
        self.display_options()

    def display_options(self):
        #displaying options
        y=0
        for key,value in settings.items():
            #displaying setting icons
            self.window.blit(text.loaded_text[key],(self.disp_pos[0],self.disp_pos[1]+(35*y)))
            
            #displaying what is currently configured
            if value[0] == "knob":
                text.display_numbers(value[1],(self.disp_pos[0]+300,self.disp_pos[1]+(35*y)),window=self.window)
            elif value[0] == "switch":
                self.window.blit(
                    anim.all_loaded_images["on.png" if value[1] else "off.png"],
                    (self.disp_pos[0]+300,self.disp_pos[1]+(35*y))
                    )

            y+=1

        #special stuff
        self.window.blit(anim.all_loaded_images["cursor.png"],(self.disp_pos[0] - 25 ,self.disp_pos[1]+(self.pos*35)))
        self.window.blit(text.loaded_text["PRESS P TO APPLY"],(self.apgr_pos[0]+random.randint(-5,5),self.apgr_pos[1]+random.randint(-5,5)))
        self.window.blit(anim.all_loaded_images["config_menu.png"],(self.logo_pos[0]+random.randint(-2,2),self.logo_pos[1]+random.randint(-2,2)))

    def event_handler(self,event):
        if event.type == pygame.KEYDOWN:
            #navigating the menus
            if event.key == pygame.K_UP:
                self.pos = self.pos-1 if self.pos > 0 else (len(self.keys)-1)
            if event.key == pygame.K_DOWN:
                self.pos = self.pos+1 if self.pos < (len(self.keys)-1) else 0
            #switching or moving up
            if event.key == pygame.K_RIGHT:
                mod_value = settings[self.keys[self.pos]]
                if mod_value[0] == "switch":
                    mod_value[1] = False if mod_value[1] else True
                elif mod_value[0] == "knob":
                    mod_value[1] += mod_value[2]
                    mod_value[1] = round(mod_value[1],len(str(mod_value[2])))
            if event.key == pygame.K_LEFT:
                mod_value = settings[self.keys[self.pos]]
                if mod_value[0] == "switch":
                    mod_value[1] = False if mod_value[1] else True
                elif mod_value[0] == "knob":
                    mod_value[1] -= mod_value[2]
                    mod_value[1] = round(mod_value[1],len(str(mod_value[2])))
            if event.key == pygame.K_p:
                apply_settings(border = self.border )
            #exitting
            if event.key == pygame.K_ESCAPE:
                self.next_state = self.return_state

    

        

