#CODE BY ANDREW CHURCH
import pygame,anim,options

#06/23/2023 - WHAT IS A BACKGROUND
# The background is a class that stores an image and a position
# This may be a little overkill for an entire class, but it works for organization purposes in my opinion

class Background():


    def __init__(self,img:str,resize:list,speed:list,border_size:tuple=pygame.display.play_dimensions,**kwargs):
        # It stores an image, a position tuple, and a speed tuple
        self.aimg = anim.AutoImage(host=self,name=img,resize=resize)
        self.size = [self.image.get_width(),self.image.get_height()]
        self.pos = [0,0]
        self.speed = speed[:]
        self.border = (self.image.get_width(),self.image.get_height())



    def update(self):
        #updating image
        self.aimg.update()
        #updates positioning and such
        self.pos[0] += self.speed[0] #x pos
        self.pos[1] += self.speed[1] #y pos
        #resetting positioning
        if self.pos[0] > self.border[0] or self.pos[0]*-1 > self.border[0]:
            self.pos[0] = 0 #x position
            # print('reset x')
        if self.pos[1] > self.border[1] or self.pos[1]*-1 > self.border[1]:
            self.pos[1] = 0 
            # print('reset y')
        

    def draw(self,window:pygame.display,force:bool=False):
        #drawing the image to the window
        window.blit(self.image,self.pos)
        #activating duplicates
        if self.pos != [0,0]:
            self.duplicates(window,pos=self.pos,force=force)


    def change(self,img,resize,speed,border_size:tuple=pygame.display.play_dimensions):
        # It stores an image, a position tuple, and a speed tuple
        self.image = anim.all_loaded_images[img]
        self.image = pygame.transform.scale(self.image,resize)
        self.size = resize.copy()
        self.pos = [0,0]
        self.speed = speed.copy()
        self.border = border_size


    def duplicates(self,window:pygame.display,pos:tuple=None,force:bool=False):
        #7/10/2023 - adding a default position
        pos = self.pos if pos is None else pos 
        #drawing repeats of the background if any of it is offscreen
        #07/10/2023 - instead of individually blitting, it makes a list for easy modification
        blit_list = [ ] 
        if pos[0] > 0 or force:#LEFT
            blit_list.append((pos[0]-self.size[0],pos[1]))
        elif pos[0] < 0 or force:#RIGHT
            blit_list.append((pos[0]+self.size[0],pos[1]))
        if pos[1] > 0 or force:#UP
            blit_list.append((pos[0],pos[1]-self.size[1]))
        elif pos[1] < 0 or force:#DOWN
            blit_list.append((pos[0],pos[1]+self.size[1]))
        if pos[0] > 0 and pos[1] > 0 or force:#UPLEFT
            blit_list.append((pos[0]-self.size[0],pos[1]-self.size[1]))
        if pos[0] > 0 and pos[1] < 0 or force:#DOWNLEFT
            blit_list.append((pos[0]-self.size[0],pos[1]+self.size[1]))
        if pos[0] < 0 and pos[1] > 0 or force:#UPRIGHT
            blit_list.append((pos[0]+self.size[0],pos[1]-self.size[0]))
        if pos[0] < 0 and pos[1] < 0 or force:#DOWNRIGHT
            blit_list.append((pos[0]+self.size[0],pos[1]+self.size[1]))


        #displaying all blits
        for blit in blit_list:
             window.blit( 
                self.image,blit
                )



class Floor():
    def __init__(self,image:str,player:pygame.sprite.Sprite,window:pygame.Surface,move:list=(0,0),scale:tuple=None,):
        self.image = anim.all_loaded_images[image] if scale is None else pygame.transform.scale(anim.all_loaded_images[image],scale)
        self.rect = self.image.get_rect()
        self.centerx = (window.get_width()//2)
        self.centery = window.get_height()
        self.move = move
        self.player=player
        self.hide = False
    
    def update(self):...

    def draw(self,surf:pygame.Surface) -> None:
        if self.hide: return
        else:
            self.rect.centerx = self.centerx + (self.centerx-self.player.rect.x)*self.move[0] #stays centered
            self.rect.centery = self.centery - (self.player.rect.centery - self.player.bar[1])*self.move[1] #moves with the player's y-velocity
            surf.blit(self.image,self.rect)