import pygame,text,audio
from emblems import Emblem as Em

class Event():
    sprites = pygame.sprite.Group()
    def __init__(self,kwargs:dict):
        Event.sprites.empty()
        self.playing = True
        self.event = 0
        self.duration = 0 
    def update(self):
        self.duration += 1
        self.update_event(self.event)
    def update_event(self,event=0):
        ...


class NewLevelEvent(Event):
    #HARD CODED - what happens when a new level occurs
    def __init__(self,**kwargs):
        Event.__init__(self,kwargs=kwargs)
        self.level_em = Em( im=None,coord=(100,100),isCenter=True,force_surf = text.load_text(text=('LEVEL ' + str(kwargs['level']) + "!!!"),size=30,add_to_loaded=False) )
        self.window = kwargs['window']
        Event.sprites.add(self.level_em)
    def update_event(self,event=0):
        if self.duration == 1:
            audio.play_sound("tada.mp3")
        if self.event == 0:
            if self.duration > 80:
                self.event += 1
        else:
            Event.sprites.empty()
            self.playing = False
    
        Event.sprites.draw(self.window)
    

