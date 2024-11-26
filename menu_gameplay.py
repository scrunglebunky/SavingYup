import json,pygame,random,text,player,enemies,audio,formation
from emblems import Emblem as Em
from emblems import TextEmblem as TEm
from backgrounds import Background as Bg
from audio import play_sound as psound
from audio import play_song as psong
from backgrounds import Floor as Fl
import gameplay_log as log




class Info():

    # THE BACKGROUND LIST
    backgroundlist = [
        "bg01","bg02","bg03","bg04","bg05","bg06","bg07","bg08",
    ]
    # The further you get in the game, the more backgrounds you unlock
    backgroundlist_unlockchart = {
        0:0, # between level 0 and 5, you are mostly unlocking your base 3 enemies, so the background doesn't change
        5:7, # between levels 5 and.. honestly whatever, you can get any stage as the zone changes normally now
    }
    backgroundlist_unlockable = [] #doubles as pickpool

    # THE ENEMIES TO UNLOCK
    enemylist = list(enemies.loaded.keys()); enemylist.pop(3) #removing enemy D because its an empty class
    enemylist_unlockchart = {
        0:0, # at level 0 you unlock A
        1:2, # you unlock BC past that
        4:9, # you unlock the rest after the first world is complete :3
        # but how do you stop enemies from being re-unlocked?
    }
    enemylist_unlockable = []
    enemylist_pickpool = [] # (the full enemylist, up to the unlocklist value) - the already unlocked enemies 

    
    # THE MOVEMENT PATTERNS TO UNLOCK
    with open("./data/start_patterns.json","r") as start_patterns_raw: startlist = json.load(start_patterns_raw) #this then merges all settings with the default settings
    startlist_unlockchart = {
        0:3, #all 4 are available at first. change later so each enemy is assigned one
        5:7, #the second 4 are available after this
        10:11,
        15:15,
        20:19,
        25:23, #all are unlocked
    }
    startlist_unlockable = []
    startlist_pickpool = [] # (full startlist up to unlocklist value) - already unlocked patterns

   

    # TAKING THE UNLOCK CHART AND (usually the level) AN INDEX VALUE AND FINDING THE UNLOCKABLE LIST
    @staticmethod
    def generate_unlockable(xlist:list, unlockchart:dict,unlockindex:int,):
        # print("---GENERATING UNLOCKABLE")
        output = 0 #the default option is only the first thing to unlock so here
        for k,v in unlockchart.items(): # iterating through everything until it reaches an unlock point it hasnt gotten to yet
            if unlockindex < k:
                break
            else:
                output = v
                continue
        # print(unlockindex, "is under", k, "so final result is index ", output, "out of possible ( 0 through", len(xlist)-1,")")
        # then splitting xlist up to the unlockchart value
        return xlist[:(output+1)]
    

    # TAKING THE UNLOCKABLE LIST AND MAKING A PICKPOOL
    @staticmethod
    def generate_pickpool(unlockable:list,unlocked:list):
        # print("---GENERATING PICKPOOL")
        # print('received',unlockable)
        # print('comparing with',unlocked)
        pickpool = []
        for i in range(len(unlockable)):
            if unlockable[i] not in unlocked:
                pickpool.append(unlockable[i])
        return pickpool
                
    # this is just random.choice, but i'm lazy
    @staticmethod
    def pick_from_pool(pool:list):
        return random.choice(pool)
        
    @staticmethod
    def unlock_enemy(gameplay):
        #generating unlockable, pickpool, and selected enemy 
        enemypick = Info.generate_unlockable(xlist=Info.enemylist,unlockchart=Info.enemylist_unlockchart,unlockindex=gameplay.level)
        enemypick = Info.generate_pickpool(unlockable=enemypick,unlocked=gameplay.char_list)
        #stopping this if there is nothing left to pick
        if len(enemypick) <= 0:
            return
        #then continuing if not
        enemypick = Info.pick_from_pool(enemypick)
        gameplay.char_list.append(enemypick)
        #generating an unlockable, and then just picking an entrance pattern.
        #   pick pool isn't needed
        patternpick = Info.generate_unlockable(xlist=Info.startlist,unlockchart=Info.startlist_unlockchart,unlockindex=gameplay.level)
        patternpick = Info.pick_from_pool(patternpick)
        gameplay.char_start_patterns[enemypick] = patternpick
    
    @staticmethod
    def unlock_bg(gameplay):
        #generating unlockable, pickpool, and selected background
        bgpick = Info.generate_unlockable(xlist=Info.backgroundlist,unlockchart=Info.backgroundlist_unlockchart,unlockindex=gameplay.level)
        bgpick = Info.generate_pickpool(unlockable=bgpick, unlocked=gameplay.backgroundlist_unlocked)
        #sets a new background if there is one to set
        if len(bgpick) > 0:
            bgpick = Info.pick_from_pool(bgpick)
            gameplay.new_bg(bgpick)
        #however, if there are no unique backgrounds left to pick, it just picks an older one
        else:
            bgpick = Info.pick_from_pool(gameplay.backgroundlist_unlocked)
            gameplay.new_bg(bgpick)

    


class GamePlay(pygame.sprite.Sprite):
    sprites = { #sprites are now state-specific hahaha
            0:pygame.sprite.Group(), #ALL SPRITES
            1:pygame.sprite.Group(), #PLAYER SPRITE, INCLUDING BULLETS ; this is because the player interacts with enemies the same way as bullets
            2:pygame.sprite.Group(), #ENEMY SPRITES
            3:pygame.sprite.Group(), #UI SPRITES
        }

    def __init__(self,playstate):

        #pygame sprite info
        pygame.sprite.Sprite.__init__(self)
        self.playstate = playstate
        # info about what's going on with the game itself
        self.active = False
        self.over = False
        # resetting gameplay log
        log.log_reset()

        #resetting the sprite groups
        for group in GamePlay.sprites.values():
            group.empty()
        
        #image/rect info
        self.image = pygame.Surface(pygame.display.play_dimensions).convert_alpha()
        self.rect = self.image.get_rect()

        self.bar = ( #the field the player is able to move along
            "h", #if the bar is horizontal or vertical.
            pygame.display.play_dimensions[1]*0.90, #x position if vertical, y position if horizontal.
            (20,pygame.display.play_dimensions[0]-20), #the limits on both sides for the player to move on, y positions if vertical, x positions if horizontal
            1, #gravity. 
        )

        #spawning the player in
        self.player = player.Player(bar=self.bar,sprite_groups=GamePlay.sprites)
        GamePlay.sprites[1].add(self.player)

        # level/difficulty info
        self.level = 0 #the total amount of levels passed, usually used for intensities or score
        self.difficulty = 1 + self.level / 5


        # current running game info, which replaces world data
        # this isn't a dictionary anymore because they're annoying to write
        self.char_list = [] 
        self.char_start_patterns = {}
        self.backgroundlist_unlocked = []
        #unlocking new character/background
        Info.unlock_enemy(gameplay=self)
        Info.unlock_bg(gameplay=self)
        #06/01/2023 - loading the formation
        #the formation handles spawning and management of most enemies, but the state manages drawing them to the window and updating them
        self.new_formation()
        # self.new_bg("bg01") # now set by GPI

        #timer for updating new level
        self.leveltimer = 0 

    

    
    def update(self):
        #Updating backgrounds - drawing to window
        self.background.update()
        self.background.draw(self.image)
        if self.floor is not None:
            self.floor.update()
            self.floor.draw(self.image)    
        #updating all individual sprites, with the fourth group having special priority.
        GamePlay.sprites[0].update()
        GamePlay.sprites[1].update()
        GamePlay.sprites[2].update()
        GamePlay.sprites[0].draw(self.image)
        GamePlay.sprites[1].draw(self.image)
        GamePlay.sprites[2].draw(self.image)
        #only updating the formation after checking for events, to prevent the level starting beforehand.
        self.formation.update()
        #calling collision
        self.collision()
        # DEMO PURPOSES -- CHANGE LATER!!! 
        if self.formation.cleared and self.leveltimer > 15:
            self.new_level()
        #updating the wait timer
        elif self.formation.cleared:
            self.leveltimer += 1
        #08/21/2023 - Game Over - making the gameover asset appear if dead
        if self.player.health <= 0:
            self.playstate.gameover.start()

    def collision(self):
        #Detecting collision between players and enemies 
        collidelist=pygame.sprite.groupcollide(GamePlay.sprites[1],GamePlay.sprites[2],False,False,collided=pygame.sprite.collide_mask)
        for key,value in collidelist.items():
            for item in value:
                key.on_collide(2,item)
                item.on_collide(1,key)


    def new_formation(self):
        # creating a new formation
        self.formation = formation.Formation(
            player = self.player,
            # world_data = self.world_data,
            char_list=self.char_list,
            start_patterns=self.char_start_patterns,
            level=self.level,
            difficulty=self.difficulty,
            sprites=GamePlay.sprites,
            window=self.image,
            #is_demo = self.is_demo
            )
    
    def new_bg(self,bg="bg01",transition_effect:bool=False):
        #06/03/2023 - Loading in the background
        self.background = Bg(bg, resize = (600,800), speed = (0, 1 if bg not in ("bg02","bg03","bg07","bg08") else 0 ))
        # also loading in the floor if it exists
        self.floor = Fl(
            image='floor-default',
            player=self.player,
            window=self.image,
            move=(.25,.25),
            scale=(800,800)
            ) 
    
    def new_zone(self,shop=True):
        # new zone code
        Info.unlock_enemy(gameplay=self)
        Info.unlock_bg(gameplay=self)
        if shop: self.playstate.shop.start()

    
    def new_level(self):
        # updating level and difficulty info
        self.level += 1
        self.difficulty = 1 + self.level / 5        
        self.formation.empty()
        # TEST FOR DEMO
        # self.new_zone()
            
        #restarting the formation
        self.new_formation()

        #resetting the level timer
        self.leveltimer = 0 

        if self.level%5 == 0:
            self.new_zone()
        elif self.level in (1,2,3):
            self.new_zone(False)

    def start(self):
        self.active = True

    def event_handler(self,event):
        self.player.controls(event)
