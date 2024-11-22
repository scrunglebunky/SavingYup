# program by Andrew Church 2024
""" HEY THERE BUDDY LET'S DO SOME BUSINESS!


HELLO THERE YUP! IT LOOKS LIKE YOU NEED HELP DEFEATING THOSE BAD GUYS!!!
WHY DON'T I HELP A FAIR BIT FOR YA???

The Shop is a class that registers itself as a sprite, kind of like how GamePlay will when I spend the week on optimization :3
It will show up, get drawn to the screen, etc.
It is able to register inputs, and modify the player.
"""

import json,pygame



class Shop(pygame.sprite.Sprite):
    #loading the items index
    with open("./data/items.json") as raw:
        raw_items_index = json.load(raw)
    #adding a "purchased" section
    for i in raw_items_index.keys():
        raw_items_index[i]["purchased"] = 0

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.items_index = dict(Shop.raw_items_index)
