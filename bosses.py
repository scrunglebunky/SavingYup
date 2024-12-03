import pygame, enemies
from anim import AutoImage as AImg
from emblems import Emblem as Em
from emblems import TextEmblem as TEm

""" 
THE BOSS(ES) BUT NOT REALLY IT'S JUST ONE BOSS
CONGRATULATIONS! YOU'VE GOTTEN PAST 4 LEVELS! BUT TO BEAT THE ZONE, YOU NEED TO BEAT THE BOSS!
KING NOPE IS WHAT HOLDS YOU BACK FROM YOUR NEXT ASCENSION! KILL HIM.

The boss is a pygame.sprite.Sprite asset in the enemies group.
It shares methods with a lot of other sprites: hurt, on_collide, etc.
It shares other attributes with other sprites: health, state, states, aimg, etc.

When the boss is initialized, it sets its values and decides its health, idle state, and available attacks based off difficulty
The boss will be in its Idle state, and after enough time decide an attack to go through based off its attack pool

just listing off the available states
#####
idle_0 # the enemy just sits there not moving, maybe shaking a little bit
idle_1 # it moves back and forth in a sine pattern like atk_sine, scales in speed based off difficulty
idle_2 # it just copies spasm but it doesn't attack this time
idle_3 # copies atk_teleport but also doesn't attack
idle_n
atk_bounce # the enemy points towards you and launches itself at you while bouncing along anything it sees
atk_spasm # the enemy does a bounce to random spots while shooting in all directions each time it hits its point
atk_sine # it moves around back and forth in a sine for both x and y while shooting in all directions (but this time only 1 bullet at a time)
atk_fall # it moves back and forth in a sine pattern (for x) and randomly slams its body down to the bottom of the screen
atk_jump # the enemy moves up and down in a sine pattern, and randomly jumps to the opposite side
atk_teleport # spasm but scarier. he teleports from each spot and does the same shooting stuff
atk_throw # the seashells attack from the crustacean, where the bullets pop out from a differing angle, and then all aim towards the player
atk_children # nope starts giving violent birth and its children slowly move towards you unless you kill them
atk_n
entrance # coming in -- invincible
exit # dying
done # dead
#####
Each of these attacks are actual classes, because they do things on start and end.
The classes take the host boss as an argument.

"""