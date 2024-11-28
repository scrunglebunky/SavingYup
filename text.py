# ANDREW CHURCH - 2023
import pygame,math,json
pygame.font.init()
terminalfont_50 = pygame.font.Font("./data/font.ttf",50)
terminalfont_30 = pygame.font.Font("./data/font.ttf",30)
terminalfont_20 = pygame.font.Font("./data/font.ttf",20)
terminalfont_10 = pygame.font.Font("./data/font.ttf",10)
terminalfont_15 = pygame.font.Font("./data/font.ttf",15)





#5/30/2023 - LOADING NUMBERS
loaded_nums = {}
load_list = [".","-","+","x","%",0,1,2,3,4,5,6,7,8,9]
for num in load_list:
    loaded_nums[str(num)] = terminalfont_30.render(str(num),False,"white","black")
#5/30/2023 - DISPLAY_NUMBERS
# There is separate function for displaying numbers because I'm not gonna store several numbers as their own stupid variables, as that would take up too much RAM
# What it does here, instead, is split the number into each individual digit and displays them separately 
def display_numbers(num:int,pos:tuple,window:pygame.display,reverse:tuple = False):
    num = str(num) if not reverse else str(num)[::-1]
    width = loaded_nums["8"].get_width() #made width one process to save a sliver of processor space
    for i in range(len(num)):
        window.blit(loaded_nums[num[i]],(
            ( (pos[0]+(width*i)) if not reverse else (pos[0]-(width*(i+1)) ) ,
            pos[1]
            )))


def load_text(
    text: str = "WOW!",
    resize: tuple = None, #if resize
    font: pygame.Font = terminalfont_30,  # the font ; could also be SetFont
    fg: str = "white",  # foreground color
    bg: str = "black",  # background color
    *args,**kwargs
    ):  
        #loading
        image = font.render(
            str(text), True, fg, bg
        )
        # resizing image
        if resize is not None:
            image = pygame.transform.scale(
                image, (resize[0], resize[1])
            )
        return image


class AutoNum():
    #a modification of AutoImage that exclusively handles numbers.
    def __init__(self,text:any,host:pygame.sprite.Sprite = None,make_host_rect:bool=False,font:pygame.font.Font=terminalfont_30,resize=None):
        #loading text
        self.cur = str(text) 
        self.image = font.render(self.cur,False,"white","black")
        self.resize = resize
        if self.resize is not None:
            self.image=pygame.transform.scale(self.image,self.resize)
        self.mask = pygame.mask.from_surface(self.image)
        self.font = font
        #host information
        self.hashost = host is not None
        self.host = host
        self.make_host_rect = make_host_rect

        #loading image
        if self.hashost:
            self.host.image = self.image
            self.host.mask = self.mask
            if make_host_rect:
                self.host.rect = self.image.get_rect()
    
    #updating the numbers -> there is never a need to run the update for this every time
    def update(self):
        pass

    def update_text(self,text:any):
        #making sure it's different
        if str(text) != self.cur:
            #changing it
            self.image = self.font.render(text,False,"white","black")
            if self.resize is not None:
                self.image=pygame.transform.scale(self.image,self.resize)
            if self.hashost:
                self.host.image = self.image
                #saving
                if self.make_host_rect:
                    rect = self.image.get_rect()
                    rect.center = self.host.rect.center
                    self.host.rect = rect

