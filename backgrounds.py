#CODE BY ANDREW CHURCH
import pygame,anim,options

#06/23/2023 - WHAT IS A BACKGROUND
# The background is a class that stores an image and a position
# This may be a little overkill for an entire class, but it works for organization purposes in my opinion

class Background():


    def __init__(self,img:str,resize:list,speed:list,**kwargs):
        # It stores an image, a position tuple, and a speed tuple
        self.aimg = anim.AutoImage(host=self,name=img,resize=resize)
        self.size = [self.image.get_width(),self.image.get_height()]
        self.pos = [0,0]
        self.speed = speed[:]



    def update(self):
        #updating image
        self.aimg.update()
        #updates positioning and such
        self.pos[0] += self.speed[0] #x pos
        self.pos[1] += self.speed[1] #y pos
        #resetting positioning
        if abs(self.pos[0]) > self.size[0]:
            self.pos[0] = 0 #x position
            # print('reset x')
        if abs(self.pos[1]) > self.size[1]:
            self.pos[1] = 0 
            # print('reset y')
        

    def draw(self,window:pygame.display,force:bool=False):
        #drawing the image to the window
        window.blit(self.image,self.pos)
        #activating duplicates
        if self.pos != [0,0]:
            self.duplicates(window,pos=self.pos,force=force)


    def change(self,img,resize,speed):
        # It stores an image, a position tuple, and a speed tuple
        self.image = anim.all_loaded_images[img]
        self.image = pygame.transform.scale(self.image,resize)
        self.size = resize.copy()
        self.pos = [0,0]
        self.speed = speed.copy()


    def duplicates(self,window:pygame.display,pos:tuple=None,force:bool=False):
        #7/10/2023 - adding a default position
        pos = self.pos if pos is None else pos 
        #drawing repeats of the background if any of it is offscreen
        #07/10/2023 - instead of individually blitting, it makes a list for easy modification
        blit_list = [ ] 
        # if pos[0] > 0 or force:#LEFT
        blit_list.append((pos[0]-self.size[0],pos[1]))
        # elif pos[0] < 0 or force:#RIGHT
        blit_list.append((pos[0]+self.size[0],pos[1]))
        # if pos[1] > 0 or force:#UP
        blit_list.append((pos[0],pos[1]-self.size[1]))
        # elif pos[1] < 0 or force:#DOWN
        blit_list.append((pos[0],pos[1]+self.size[1]))
        # if pos[0] > 0 and pos[1] > 0 or force:#UPLEFT
        blit_list.append((pos[0]-self.size[0],pos[1]-self.size[1]))
        # if pos[0] > 0 and pos[1] < 0 or force:#DOWNLEFT
        blit_list.append((pos[0]-self.size[0],pos[1]+self.size[1]))
        # if pos[0] < 0 and pos[1] > 0 or force:#UPRIGHT
        blit_list.append((pos[0]+self.size[0],pos[1]-self.size[1]))
        # if pos[0] < 0 and pos[1] < 0 or force:#DOWNRIGHT
        blit_list.append((pos[0]+self.size[0],pos[1]+self.size[1]))


        #displaying all blits
        for blit in blit_list:
             window.blit( 
                self.image,blit
                )


# DO NOT USE ANYMORE.
class Floor():
    def __init__(self,image:str,player:pygame.sprite.Sprite,window:pygame.Surface,move:list=(0,0),scale:tuple=None,):
        self.aimg = anim.AutoImage(host=self,name=image,resize=scale)
        self.window = window
        self.centerx = self.window.get_width()/2
        self.bottom = self.window.get_height()
        self.move = move
        self.player=player
        self.hide = False
    
    def update(self):
        self.aimg.update()

    def draw(self,surf:pygame.Surface) -> None:
        if self.hide: return
        else:
            # print(self.rect.center)
            # self.rect.centerx = self.centerx + (self.centerx-self.player.rect.x)*self.move[0] #stays centered
            # self.rect.centery = self.centery - (self.player.rect.centery - self.player.bar[1])*self.move[1] #moves with the player's y-velocity
            if self.move[0]:
                offsetx = (self.centerx - self.player.rect.x)*self.move[0] 
            if self.move[1]:
                offsety = (self.player.rect.centery - self.player.bar[1])*self.move[1]
            self.rect.centerx = self.centerx + offsetx
            self.rect.bottom = self.bottom - offsety
            surf.blit(self.image,self.rect)

# a platform that follows the player
class PlatformFollow(pygame.sprite.Sprite):
    def __init__(self,player):
        pygame.sprite.Sprite.__init__(self)
        # very simple stuff
        self.aimg = anim.AutoImage(host=self,name="platform")
        self.player = player
        # doing what update does immediately
        self.update()
    
    def update(self):
        self.aimg.update()
        self.rect.top = self.player.bar[1] + 20
        self.rect.centerx = self.player.rect.centerx - self.player.momentum

    def on_collide(*args,**kwargs):
        ...
    def hurt(*args,**kwargs):
        ...