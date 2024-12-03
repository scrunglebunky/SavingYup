import json,pygame,random,text,player,enemies,audio,formation
from emblems import Emblem as Em
from emblems import TextEmblem as TEm
from backgrounds import Background as Bg
from backgrounds import PlatformFollow as PF
from audio import play_sound as psound
from audio import play_song as psong
from backgrounds import Floor as Fl
import gameplay_log as log
from bullets import LOADED as bulletloaded
from anim import AutoImage as AImg
from menu import Menu


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

    

# WHAT IS THIS DOING?
# I have moved everything that involves gameplay into this one simple sprite
# This handles everything, and lets playstate know when to open another menu asset
class GamePlay(Menu):
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
        self.imageraw = pygame.Surface(pygame.display.play_dimensions).convert_alpha()
        self.image = pygame.Surface(pygame.display.play_dimensions_resize).convert_alpha()
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
        self.level = 1 #the total amount of levels passed, usually used for intensities or score
        self.difficulty = 1 + (self.level-1) / 5


        # current running game info, which replaces world data
        # this isn't a dictionary anymore because they're annoying to write
        self.char_list = [] 
        self.char_start_patterns = {}
        self.backgroundlist_unlocked = []
        #unlocking new character/background
        Info.unlock_enemy(gameplay=self)
        Info.unlock_bg(gameplay=self) # this also sets the background
        self.darkness = Bg('darkness.png',(600,800),speed=(0,0))
        #06/01/2023 - loading the formation
        #the formation handles spawning and management of most enemies, but the state manages drawing them to the window and updating them
        self.new_formation()
        # self.new_bg("bg01") # now set by GPI
        self.platform = PF(self.player)

        #timer for updating new level
        self.leveltimer = 0 

    

    
    def update(self):
        #Updating backgrounds - drawing to window
        self.imageraw.fill("white")
        self.background.update()
        self.background.draw(self.imageraw)
        self.darkness.update()
        self.darkness.draw(self.imageraw)
        self.platform.update()
        self.imageraw.blit(self.platform.image,self.platform.rect)
        # if self.floor is not None:
        #     self.floor.update()
        #     self.floor.draw(self.image)    
        #updating all individual sprites, with the fourth group having special priority.
        GamePlay.sprites[0].update()
        GamePlay.sprites[1].update()
        GamePlay.sprites[2].update()
        GamePlay.sprites[0].draw(self.imageraw)
        GamePlay.sprites[1].draw(self.imageraw)
        GamePlay.sprites[2].draw(self.imageraw)
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
            self.playstate.add_queue("gameover")
            self.end()

        # making sure the image transformation finishes
        self.image = pygame.transform.scale(self.imageraw,pygame.display.play_dimensions_resize)

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
            window=self.imageraw,
            #is_demo = self.is_demo
            )
    
    def new_bg(self,bg="bg01",transition_effect:bool=False):
        #06/03/2023 - Loading in the background
        self.background = Bg(bg, resize = (600,800), speed = (0, 1 if bg not in ("bg02","bg03","bg07","bg08") else 0 ))
        # also loading in the floor if it exists
        # self.floor = Fl(
        #     image='floor-default',
        #     player=self.player,
        #     window=self.image,
        #     move=(.25,.25),
        #     scale=(800,800)
        #     ) 
    
    def new_zone(self,shop=True,advance=True):
        # new zone code
        Info.unlock_enemy(gameplay=self)
        Info.unlock_bg(gameplay=self)
        self.playstate.add_queue('advance')
        self.playstate.add_queue('shop')
        self.playstate.add_queue('newlevel')
        self.playstate.add_queue('gameplay')
        # turning active off because a bunch of graphics are playing
        self.end()

    
    def new_level(self):
        # new zone info. If there is a new zone, it does this first.
        if self.level in (0,1,2,3):
            Info.unlock_enemy(gameplay=self)
            Info.unlock_bg(gameplay=self)
            self.playstate.add_queue('newlevel')
            self.playstate.add_queue('gameplay')
            self.end()
        elif self.level%5 == 0:
            self.new_zone()
        else:
            # playing a graphic
            self.playstate.add_queue('newlevel')
            self.playstate.add_queue('gameplay')
            self.end()
        
       
         
            
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

        

    def start(self):
        self.active = self.playstate.gameplayui.active = True
        

    def event_handler(self,event):
        self.player.controls(event)
        match event.type:
            case pygame.KEYDOWN:
                match event.key:
                    case pygame.K_ESCAPE:
                        self.playstate.add_queue('pause')
                        self.end()
                    # DEBUG CODE
                    case pygame.K_3:
                        self.player.health += 1
                    case pygame.K_2:
                        self.player.bullet_dmg = 1
                        self.player.bullet_list = ["default","tripleshot","rocket","wide"]
                        self.player.bullet_time = 0
                        self.player.bullet_max = 1000
                        self.player.health = 999
                        self.player.perks['magnet'] = 1
                        self.player.perks['rocketboots'] = 10
                        self.player.coins += 1
                        self.player.coins *= 1000
                    case pygame.K_0:
                        self.player.hurt()
                    case pygame.K_4:
                        self.formation.state = 'destroy'



# WHAT IS **THIS** DOING?
# This pretty much does the job of what the UI_Border did, in terms of displaying ui elements like items and such
# It was genuinely pointless to put those into the window itself, instead of being inside another image like this.
class GamePlayUI(Menu):
    sprites = pygame.sprite.Group()
    width,height=300,500

    spr_logo =  Em(im = "logo.png",coord = (0,0))
    sprites.add(spr_logo)

    spr_coins = Em(im="ui_coins.png", coord = (0,100))
    spr_coins_text = TEm(txt="$0",coord=(64,spr_coins.coord[1]+32),font = text.terminalfont_30)
    sprites.add(spr_coins,spr_coins_text)

    spr_lives = Em(im="ui_lives.png",coord=(0,175))
    spr_lives_text = TEm(txt="0",coord=(64,spr_lives.coord[1]+32),font=text.terminalfont_30)
    sprites.add(spr_lives,spr_lives_text)

    spr_weapon = Em(im="ui_weapon.png",coord=(0,250),resize=(64,64))
    spr_weapon_current = Em("NONERN",coord=spr_weapon.coord,resize=(64,64))
    sprites.add(spr_weapon,spr_weapon_current)

    spr_dmg = Em(im="icon_dmgup.png",coord=(0,325),resize=(32,32))
    spr_dmg_text = TEm(txt="0",coord=(32,spr_dmg.coord[1]),font=text.terminalfont_20)
    sprites.add(spr_dmg,spr_dmg_text)

    spr_shootrate = Em(im="icon_shootrateup.png",coord=(0,355),resize=(32,32))
    spr_shootrate_text = TEm(txt="0",coord=(32,spr_shootrate.coord[1]),font=text.terminalfont_20)
    sprites.add(spr_shootrate,spr_shootrate_text)

    spr_maxbullets = Em(im="icon_maxbulletup.png",coord=(0,385),resize=(32,32))
    spr_maxbullets_text = TEm(txt="0",coord=(32,spr_maxbullets.coord[1]),font=text.terminalfont_20)
    sprites.add(spr_maxbullets,spr_maxbullets_text)

    spr_rocketboots = Em(im="icon_rocketbootperk.png",coord=(0,415),resize=(32,32),hide=True)
    spr_rocketboots_text = TEm(txt="0",coord=(32,spr_rocketboots.coord[1]),font=text.terminalfont_20,hide=True)
    sprites.add(spr_rocketboots,spr_rocketboots_text)

    spr_magnet = Em(im="icon_magnetperk.png",coord=(0,445),resize=(32,32),hide=True)
    sprites.add(spr_magnet)


    
    # invididual sprite images to show upgrades, which are all shrunk down.
    icon_rocketboots = AImg(name="icon_rocketboots.png",resize=(32,32)).image 
    icon_dmgup = AImg(name="icon_dmgup.png",resize=(32,32)).image 
    icon_shootrateup = AImg(name="icon_dmgup.png",resize=(32,32)).image 

    def __init__(self,playstate):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((GamePlayUI.width,GamePlayUI.height)).convert_alpha()
        self.rect = self.image.get_rect()
        self.playstate = playstate #pulls player info from playstate
        self.gameplay:GamePlay = self.playstate.gameplay #the gameplay sprite
        self.player = self.gameplay.player #the player from gameplay
        self.active = False #this isn't used however i am keeping it here for yada yada parent class stuff.

    def update(self):
        self.image.fill("#7f7fff")
        self.update_gameinfo()
        GamePlayUI.sprites.update()
        GamePlayUI.sprites.draw(self.image)
        # active code
        self.active = self.gameplay.active

    def event_handler(self,event):
        ...

    def update_gameinfo(self):
        GamePlayUI.spr_coins_text.update_text(str(self.player.coins))
        GamePlayUI.spr_lives_text.update_text(str(self.player.health))
        GamePlayUI.spr_dmg_text.update_text("x"+str(self.player.bullet_dmg))
        GamePlayUI.spr_maxbullets_text.update_text("x"+str(self.player.bullet_max))
        GamePlayUI.spr_shootrate_text.update_text(str(round((60/(self.player.bullet_time if self.player.bullet_time > 0 else 1)),2))+" DPS")
        GamePlayUI.spr_rocketboots_text.update_text("x"+str(self.player.perks['rocketboots']))
        #changing spr_weapon_current ONLY IF it has changed
        if bulletloaded[self.player.current_bullet].icon != GamePlayUI.spr_weapon_current.aimg.name:
            GamePlayUI.spr_weapon_current.aimg.__init__(host=GamePlayUI.spr_weapon_current,name=bulletloaded[self.player.current_bullet].icon,resize=(64,64))
        #rocketboots sprite
        if self.player.perks['rocketboots'] > 0:
            GamePlayUI.spr_rocketboots.hide = GamePlayUI.spr_rocketboots_text.hide = False
        #magnet sprite
        if self.player.perks['magnet'] is not False:
            GamePlayUI.spr_magnet.hide = False

        # this is more basic info of the placement of the rect but i think it fits here too
        # repositioning if the game resolution has changed
        if self.rect.left != pygame.display.play_dimensions_resize[0]+16:
            self.rect.left = pygame.display.play_dimensions_resize[0]+16

    def draw_nonsprite_gameinfo(self):
        #this draws things like upgrades, shootrate, damage purchases, etc
        if self.player.perks['rocketboots'] > 0:
            ...

    def start(self):
        self.active = True
        self.rect.left = pygame.display.play_dimensions_resize[0]+16

    
