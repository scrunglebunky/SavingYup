# program by Andrew Church 2024
""" HEY THERE BUDDY LET'S DO SOME BUSINESS!


HELLO THERE YUP! IT LOOKS LIKE YOU NEED HELP DEFEATING THOSE BAD GUYS!!!
WHY DON'T I HELP A FAIR BIT FOR YA???

The Shop is a class that registers itself as a sprite, kind of like how GamePlay will when I spend the week on optimization :3
It will show up, get drawn to the screen, etc.
It is able to register inputs, and modify the player.
"""
import json,pygame,random,text
from emblems import Emblem as Em
from emblems import TextEmblem as TEm
from backgrounds import Background as Bg
from audio import play_sound as psound
from audio import play_song as psong


class Shop(pygame.sprite.Sprite):
    #loading the items index
    with open("./data/items.json") as raw:
        raw_items_index = json.load(raw)
    # copying indexes from the items json
    purchasable = raw_items_index["INDEX-purchasable"]
    perk = raw_items_index["INDEX-perk"]
    upgrade = raw_items_index["INDEX-up"]
    weapon = raw_items_index["INDEX-weapon"]
    dialog = raw_items_index["INDEX-welcometext"]
    # removing them
    del raw_items_index["INDEX-purchasable"] ,raw_items_index["INDEX-perk"], raw_items_index["INDEX-up"], raw_items_index["INDEX-weapon"], raw_items_index["INDEX-welcometext"]
    # adding a "bought" counter
    for i in raw_items_index.keys():
        raw_items_index[i]["bought"] = 0 
    # sprite list
    sprites = pygame.sprite.Group()

    def __init__(self,player):
        pygame.sprite.Sprite.__init__(self)
        Shop.sprites.empty()

        self.items_index = dict(Shop.raw_items_index)
        self.purchasable = Shop.purchasable.copy()  

        # image and rect codes. This is because the gameplay is initiated by the play state, and has multiple sprite values to handle the images.
        # If I go back to optimize this game, for instance, the gameplay background will also be a sprite
        self.image = pygame.Surface(size=(400,400)).convert_alpha()
        self.rect = self.image.get_rect()


        # if the shop is marked as "active", gameplay pauses and draws this sprite
        self.active = False
        # the index for what item you are on. this them moves the self.sprite_cursor to graphically show everything
        self.index=9999
        self.cur_price=0 
        # the game NEEDS to refer to the player, to see currency, modify the weaponslist, and change values
        self.player=player



        # setting up the individual sprites and background objects
        self.sprites_items = [TEm("TEST",coord=(0,self.image.get_height()*(.06*(i+4))),isCenter=False,font=text.terminalfont_20) for i in range(7)]
        self.sprites_items[6].update_text("LEAVE")
        self.sprites_items[6].change_pos((0,self.image.get_height()*.65))

        self.sprite_shopkeep = Em(im="shopkeeper",coord=(self.image.get_width()*0.75,self.image.get_height()*.45),isCenter=True)
        self.sprite_title = Em(im="shoptitle",coord=(self.image.get_width()*0.5,self.image.get_height()*.1),isCenter=True)
        self.sprite_cursor = TEm(txt = "<", coord = (9999999,999999999),font=text.terminalfont_20)
        self.sprite_icon = Em(
            im="icon_welcome.png",
            coord=(0,self.image.get_height()*.7),
            resize=(128,128),
            )        
        self.sprite_description = TEm(
            txt=random.choice(Shop.dialog),
            coord=(self.sprite_icon.rect.right,self.sprite_icon.coord[1]),
            font=text.terminalfont_20,
            )
        self.sprite_price = TEm(
            txt="$0",
            coord=(self.sprite_icon.rect.right,self.image.get_width()-30),
            font=text.terminalfont_30
        )
        self.sprite_balance = TEm(txt=self.player.coins,coord=(0,0),font=text.terminalfont_30)

        # adding the sprites
        Shop.sprites.add(self.sprites_items, self.sprite_shopkeep,self.sprite_title,self.sprite_cursor, self.sprite_description,self.sprite_icon, self.sprite_price ,self.sprite_balance)
        # creating a background
        self.bg = Bg("bgSHOP",resize=(300,400),speed=(2,2))



        # CREATING A NEW SHOP INSTANCE, SO THIS IS USABLE ON STARTUP. I KNOW ITS WASTEFUL BUT I DONT CARE ITS RUN ONCE
        self.start(False)


    def update(self):
        # updating the background info and drawing them
        self.bg.update()
        self.bg.draw(self.image)

        # updating the sprites and drawing them
        Shop.sprites.update()
        Shop.sprites.draw(self.image)






    # SELECTING ITEMS -- MOVING THE INDEX
    def move_index(self,movetype:int):
        self.index += movetype
        if self.index < 0 : 
            self.index = len(self.sprites_items)-1
        elif self.index > len(self.sprites_items)-1: 
            self.index = 0
        #updating cursor
        self.sprite_cursor.coord = self.sprites_items[self.index].rect.right+16,self.sprites_items[self.index].coord[1]
        #updating the description and icon
        self.set_info()
        # playing a sound
        psound("bap1.wav")
        self.sprite_shopkeep.aimg.change_anim("think")




    def transaction(self):
        # error handling -- just automatically passing if the index thing isn't an item IE like "LEAVE"
        if self.sprites_items[self.index].text not in self.items_index.keys(): return True
        # this handles anything relating to buying, including modifying the "bought" section of the items index
        elif self.player.coins >= self.price:
            psound("cha-ching.wav")
            self.player.coins -= self.price
            self.items_index[self.sprites_items[self.index].text]["bought"] += 1
            self.sprite_shopkeep.aimg.change_anim("happy")
            return True
        else:
            psound("denied.wav")
            self.sprite_shopkeep.aimg.change_anim("angry")
            return False





    # SELECTING ITEMS -- ACTUALLY PURCHASING ITEMS
    def payload(self):
        # OKAY SO THIS IS HARD-CODED.
        # EVERYTHING IS HARD-CODED
        # BECAUSE THEY'RE ITEMS THAT USE RAW VARIABLE NAMES AND NOT DICTIONARIES
        if self.index > abs(len(self.sprites_items)): return #error fixing, so if you press z at the start you don't get error'd
        itm = self.sprites_items[self.index].text

        #checking if the price matches -- note this still runs the transaction.
        success = self.transaction()
        if not success:
            return

        # match statement
        match itm.lower():
            case "leave":
                self.active=False
            # the weapons -- note once you buy these weapons they're removed from the shop forever
            case "rocket":
                self.player.bullet_list.append("rocket")
                self.purchasable.remove("rocket")
                self.sprites_items[self.index].update_text("SOLD")
            case "tripleshot":
                self.player.bullet_list.append("tripleshot")
                self.purchasable.remove("tripleshot")
                self.sprites_items[self.index].update_text("SOLD")
            case "wide":
                self.player.bullet_list.append("wide")
                self.purchasable.remove("wide")
                self.sprites_items[self.index].update_text("SOLD")
            # the upgrades -- base player things
            case "maxbullet_up":
                self.player.bullet_max += 1
                self.items_index["maxbullet_up"]["bought"] += 1
            case "shootrate_up":
                self.player.bullet_time -= 1
                self.items_index["shootrate_up"]["bought"] += 1
            case "health_up":
                self.player.health += 1
                self.items_index["health_up"]["bought"] += 1
            case "dmg_up":
                self.player.bullet_dmg += 1
                self.items_index["dmg_up"]["bought"] += 1
            # perks -- ahahahahaha 
            case "rocketboots":
                self.player.perks['rocketboots'] += 1
                # self.purchasable.remove("rocketboots")
                # self.sprites_items[self.index].update_text("SOLD")
            case "child":
                self.player.add_child()
            case "magnet":
                self.player.perks['magnet'] = True
                self.purchasable.remove("magnet")
                self.sprites_items[self.index].update_text("SOLD")



        self.set_info()


    # SELECTING ITEMS -- SETTING DESCRIPTION/ICON
    def set_info(self):
        # SETTING LOGICAL STUFF
        itm = self.sprites_items[self.index].text if abs(self.index) < len(self.sprites_items) else "WELCOME"
        match itm:
            case "LEAVE":
                self.price = "BYEBYE"
            case "SOLD":
                self.price = "SOLD"
            case "WELCOME":
                self.price = "WELCOME"
            case _:
                self.price =  self.fetch_info(itm,"price_base") * (self.fetch_info(itm,"price_mult_bought") ** self.fetch_info(itm,"bought")) if itm != "LEAVE" else "BYEBYE"

        # SETTING GRAPHICS
        self.sprite_description.update_text(txt=self.fetch_info(txt=itm,field="description"))
        self.sprite_icon.__init__(im=self.fetch_info(txt=itm,field="icon"),
            coord=(0,self.image.get_height()*.7),
            resize=(128,128),
            )     
        self.sprite_price.update_text(txt=("$"+str(self.price)))
        self.sprite_balance.update_text(txt=("YOU HAVE $"+str(self.player.coins)))
        # print(self.player.coins)

    # STARTUP CODE
    def start(self,active:bool=True):
        self.active = active # it auto activates itself
        if active: psong("meowchill.mp3")
        self.sprite_shopkeep.aimg.change_anim("happy")
        self.new_shop_items()
        self.set_info()
        self.rect.center = (pygame.display.rect.centerx + random.randint(-60,60), pygame.display.rect.centery + random.randint(-60,60))
        #welcome text , resetting it
        self.index=9999
        self.sprite_description.update_text(random.choice(Shop.dialog))
        self.sprite_icon.__init__(im="icon_welcome.png",
            coord=(0,self.image.get_height()*.7),
            resize=(128,128),
            )   
        self.sprite_price.update_text(txt=("WELCOME!"))
 
    # STARTUP CODE - SETTING THE ITEMS UP FOR SALE
    def new_shop_items(self):
        purchasable = self.purchasable.copy()
        for i in range(6):
            j = random.randint(0,len(purchasable)-1)
            self.sprites_items[i].update_text(purchasable[j])
            # prevents duplicates, unless for some reason it runs out of items which it really shouldn't.
            if len(purchasable) > 0:
                purchasable.pop(j)

    
    # FETCHING INFO
    def fetch_info(self,txt,field):
        match txt:
            case "LEAVE":
                match field:
                    case "icon":
                        return "icon_door.png"
                    case "description":
                        return "GET OUT. \nPLEASE. GET OUT.\nGET OUT. LEAVE. \nPLEASE LEAVE. PLEASE. I DONT WANT YOU HERE."
                    case _:
                        return 0
            case "SOLD":
                match field:
                    case "icon":
                        return "icon_sold.png"
                    case "description":
                        return "SOLD!\nPLEASURE DOING BUSINESS\nWITH YOU."
                    case _:
                        return 0
            case "WELCOME":
                match field:
                    case "icon":
                        return "icon_welcome.png"
                    case "description":
                        return random.choice(Shop.dialog)
                    case _:
                        return 0
            case _:  
                if txt in self.purchasable:
                    if field in Shop.raw_items_index[txt].keys():
                        return Shop.raw_items_index[txt][field]
        return "NOTFOUND"
     


    # THE CONTROLS
    def event_handler(self,event):
        match event.type:
            case pygame.KEYDOWN:
                match event.key:
                    case pygame.K_UP:
                        self.move_index(-1)
                    case pygame.K_DOWN:
                        self.move_index(1)
                    case pygame.K_z:
                        self.payload()

                        