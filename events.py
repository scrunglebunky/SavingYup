import pygame,text,audio,enemies,json, random
from emblems import Emblem as Em

## WHAT IS EVENTS
# EVENTS is a hard-coded list of events that occur during gameplay
# this could be score bonuses, end-world graphics, transitions, and more!
# they are able to freeze the game, or not
# they can also be skipped to just add the payload at the end
# they can be stacked
# EVENTS ALSO HOLDS HARD-CODED GAMEPLAY INFO, LIKE WHAT BACKGROUNDS TO SET AT WHAT TIME, AND WHAT ENEMIES TO ADD IN

# NOTE TERMINOLOGY ABOUT THINGS
# xlist IS THE FULL LIST OF AVAILABLE CHARACTERS
# xlist_unlocked IS WHAT HAS ALREADY BEEN LOADED AND USABLE
# xlist_unlockchart IS A CHART OF WHAT STATS BECOME UNLOCKED AT WHAT POINT
# xlist_unlockable IS xlist ONLY UP TO THE UNLOCKABLE POINT
# xlist_pickpool IS xlist_unlockable WITH xlist_unlocked ITEMS REMOVED
# pickpool is only needed for enemies, unlockable is fine for everything else



class GamePlayInfo():

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
    def pick_from_pool(pool:list):
        return random.choice(pool)
        
    def unlock_enemy(playstate):
        #generating unlockable, pickpool, and selected enemy 
        enemypick = GamePlayInfo.generate_unlockable(xlist=GamePlayInfo.enemylist,unlockchart=GamePlayInfo.enemylist_unlockchart,unlockindex=playstate.level)
        enemypick = GamePlayInfo.generate_pickpool(unlockable=enemypick,unlocked=playstate.char_list)
        #stopping this if there is nothing left to pick
        if len(enemypick) <= 0:
            return
        #then continuing if not
        enemypick = GamePlayInfo.pick_from_pool(enemypick)
        playstate.char_list.append(enemypick)
        #generating an unlockable, and then just picking an entrance pattern.
        #   pick pool isn't needed
        patternpick = GamePlayInfo.generate_unlockable(xlist=GamePlayInfo.startlist,unlockchart=GamePlayInfo.startlist_unlockchart,unlockindex=playstate.level)
        patternpick = GamePlayInfo.pick_from_pool(patternpick)
        playstate.char_start_patterns[enemypick] = patternpick
    
    def unlock_bg(playstate):
        #generating unlockable, pickpool, and selected background
        bgpick = GamePlayInfo.generate_unlockable(xlist=GamePlayInfo.backgroundlist,unlockchart=GamePlayInfo.backgroundlist_unlockchart,unlockindex=playstate.level)
        bgpick = GamePlayInfo.generate_pickpool(unlockable=bgpick, unlocked=playstate.backgroundlist_unlocked)
        #sets a new background if there is one to set
        if len(bgpick) > 0:
            bgpick = GamePlayInfo.pick_from_pool(bgpick)
            playstate.new_bg(bgpick)
        #however, if there are no unique backgrounds left to pick, it just picks an older one
        else:
            bgpick = GamePlayInfo.pick_from_pool(playstate.backgroundlist_unlocked)
            playstate.new_bg(bgpick)



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
    

