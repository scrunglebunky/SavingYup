## CODE BY ANDREW CHURCH
import json,text,pygame,random,audio,tools

#07/04/2023 - ADDING OPTIONS MENU
# The options menu is going to iterate through everything in the settings dictionary and let people modify it with the menu buttons

#06/30/2023 - LOADING IN THE CONFIGURATION FILE
# The config.json file is a dictionary containing info about how the game works
# This file is needed, though there is a default dictionary held here 
with open("./data/config.json","r") as set_raw:
    settings = {   
    "fullscreen": ["switch", False], 
    "mute": ["switch", False], 
    "music_vol": ["knob", 0.5, 0.05], 
    "sound_vol": ["knob", 0.5, 0.05], 
    "high_resolution": ["switch",False],
    }
    settings.update(json.load(set_raw)) #this then merges all settings with the default settings
del set_raw


# pygame.display.dimensions = (settings["screen_width"][1],settings["screen_height"][1]) 
# pygame.display.play_dimensions_resize = (settings["gameplay_width"][1],settings["gameplay_height"][1])
# pygame.display.set_mode(pygame.display.dimensions, pygame.SCALED)


#07/13/2023 - This actually applies the settings 
def apply_settings(border = None):
    print(settings)
    # NOW LISTEN.
    #   THIS IS COOL AND ALL.
    #   BUT THIS ADDS UNNECESSARY DEPTH TO WHAT WAS A SMALL PROJECT.
    #   SO THERE WILL BE VOLUME AND SOME OTHER STUFF, BUT THE RESOLUTION STAYS THE SAME.
    #display
    if settings["high_resolution"][1] == True: 
        pygame.display.dimensions = (1000,800)
        pygame.display.play_dimensions_resize = (600,800)
    else: 
        pygame.display.dimensions = (720,640)
        pygame.display.play_dimensions_resize = (450,600)

    # print(pygame.display.dimensions)
    if settings['fullscreen'][1]:
        pygame.display.set_mode(pygame.display.dimensions,pygame.FULLSCREEN|pygame.SCALED)
    else:
        pygame.display.set_mode(pygame.display.dimensions)

    #sounds
    audio.change_volumes(ostvol = settings["music_vol"][1] , soundvol = settings["sound_vol"][1])
    if settings["mute"][1]: audio.change_volumes(ostvol = 0 , soundvol = 0)
    #fixing ui bar
    if border is not None: border.__init__(window=border.window)
    #writing data
    with open("./data/config.json","w") as data:
        data.write(json.dumps(settings))

apply_settings()


def restore_defaults():
    global settings
    settings = {   
        # FOR SOME REASON I HAVE TO MANUALLY DO THIS FOR NO FUCKING REASON
    "fullscreen": ["switch", False], 
    "mute": ["switch", False], 
    "music_vol": ["knob", 0.5, 0.05], 
    "sound_vol": ["knob", 0.5, 0.05], 
    "high_resolution": ["switch",False],
    }



