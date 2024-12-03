import pygame
# the parent menu class



class Menu(pygame.sprite.Sprite):
    def __init__(self):
        self.basic_init()

    def basic_init(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((400,400)).convert_alpha()
        self.rect = self.image.get_rect()
        self.active = False
        self.visible = False

    def start(self):
        self.active = True
    
    def end(self):
        self.active = False
    
    def event_handler(self,event):
        pass
        