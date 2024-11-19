# Program by Andrew Church
import random,pygame,math,enemies,random
from anim import all_loaded_images as img

class Formation():
    def __init__(self,
                level,
                level_in_world,
                world_data,
                sprites,
                player,
                difficulty:float=1.0,
                # is_demo:bool=False,
                **kwargs
                ):
        #basic info
        self.state = "start" 
        self.world_data = world_data
        self.sprites = sprites
        self.player = player
        self.level = level
        self.level_in_world = level_in_world
        self.window = kwargs['window'] if 'window' in kwargs.keys() else None
        # self.is_demo = is_demo #to tell if the game is being used in the title demo -> stops score

        #formation positioning
        self.pos = [pygame.display.rect.center[0],100] #positioning
        self.speed = 1 #how fast it takes for the position to heck off 
        self.cleared = False #if the screen is complete


        self.states = { #the states used, organized into a dictionary to reserve lines
            "start":self.state_start,
            "idle":self.state_idle,
            'destroy':self.state_destroy,
            'leave':self.state_leave,
            'done':self.state_done
        }
        
        self.timer = { #timers used 
            "time":0, #current timer, will check every so and so frames
            "duration":0, #how long the state has been alive for. used for positioning
            "grace":0, #timer for the formation stopping the character spawn waiting
            "grace_start": 0, #how long until the grace period starts
            "grace_end": 0, #how long until the grace period ends
            "spawn":120, #how often it takes for something to spawn
            "reset":720, #when the timer resets
            "dead":30, #how often dead enemies are checked
            "atk":100, #how often an enemy will attack 
        }
        #more info on grace periods lower down near the difficulty settings

        ######SPAWN LIST INFORMATION##############

        #the spawn lists needed, which tell the game what enemies to spawn
        self.spawn_list = self.find_spawn_list(level=self.level_in_world, world_data=self.world_data)
        # self.spawn_list=["BBBBBBBBBBBBBBBBBBBB","BBBBBBBBBBBBBBBBBBBB","BBBBBBBBBBBBBBBBBBBB","BBBBBBBBBBBBBBBBBBBB","BBBBBBBBBBBBBBBBBBBB"]
        # self.spawn_list = [
        #     "CCCCCCCCCCCCCCC","CCCCCCCCCCCCCCC","CCCCCCCCCCCCCCC",
        #     "AAAABBBBBBBAAAA","AAAABBBBBBBAAAA","AAAABBBBBBBAAAA",
        #     "AAAABBBBBBBAAAA","AAAABBBBBBBAAAA","AAAABBBBBBBAAAA",
        #     "DDDDDDDDDDDDDDD",
        # ]
        self.spawned_list = []

        #SPAWN INFO - the game stores the offset value here in order to spawn enemies in special ways, so now they don't all have to spawn in order
        self.spawn_offsets = [] #declaration
        #iterating through spawn list 
        for row in range(len(self.spawn_list)):
            self.spawn_offsets.append([])
            #adding the offset. note it is not labeled because spawn info iterations would work on this one
            for column in range(len(self.spawn_list[row])):self.spawn_offsets[row].append((column*self.world_data["char_distance_x"],row*self.world_data["char_distance_y"]))
        
        #ORGANIZED SPAWN: taking the indexes of the enemies and organizing them based on type
        self.spawn_organized={}
        for row in range(len(self.spawn_list)):
            for column in range(len(self.spawn_list[row])):
                to_add = self.spawn_list[row][column]
                #new element if not in dict
                if to_add in self.spawn_organized.keys():
                    self.spawn_organized[to_add].append((row,column))
                #adding onto pre-existing element if in dict
                else:
                    self.spawn_organized[to_add] = [(row,column)]
        
        # for row in range(len(self.spawn_list)):
        #     for column in range(len(self.spawn_list[row])):
        #         print("|",(row,column),self.spawn_list[row][column],end='')
        #     print('\n')
        
        # for row in range(len(self.spawn_list)):
        #     for column in range(len(self.spawn_list[row])):
        #         print("|",(row,column),self.spawn_offsets[row][column],end='')
        #     print('\n')
               
        # for k,v in self.spawn_organized.items():
        #     print(k,v)
        
        # ITERATION VALUES
        self.spawning_keys = tuple(self.spawn_organized.keys())
        self.spawning_key = 0  #the key of spawn_organized
        self.spawning_value = 0 #the index of spawn_organized

        #########################################

        #figuring out sizes and positioning based on spawn_list size
        self.pos[0] = (pygame.display.play_dimensions[0]/2) - ((len(self.spawn_list[0])*self.world_data["char_distance_x"])/2)

        #difficulty calculations
        self.difficulty = self.level//1
        self.attack={
            #throwdown amount = how many enemies are thrown down in an attack stance #goes up once every 10 levels
            "amount":((self.difficulty//3)+1) if (self.difficulty <= 6) else 3,
            "max":3+(self.difficulty*2),
        }
        self.timer['atk'] = (100 - (self.difficulty*4)) if self.difficulty < 25 else 1
        #timer["atk"] = how often enemies are thrown down to attack #goes down a frame every level
        #max_enemies = how many enemies can be down at a time, goes up by 1 every 5 levels
        
        #grace periods get slightly longer and start more often as the game gets harder
        self.timer['grace_start'] = (480 - self.difficulty*20) if self.difficulty < 10 else 60
        self.timer['grace_end'] = self.timer['grace_start']+60 + (self.difficulty * 15 if self.difficulty < 4 else 60)

        #a key used to figure out what enemy is to be spawned during the start state.
        self.enter_key = 0 #what is used for spawning entrance values, yada yada yada


        #graphical stuff, specifically for the hack world
        self.image = img[self.world_data['formation_img']] if self.world_data['formation_img'] in img.keys() else None
        # print(self.world_data['world_name'],self.world_data['formation_img'])
        self.image_size = (50 + (len(self.spawn_list[0]) * self.world_data['char_distance_x']), 75 + (len(self.spawn_list) * self.world_data['char_distance_y']))
        self.image = pygame.transform.scale(self.image,self.image_size) if self.image is not None else None
        self.image_hide = False

    def update(self):
        #updating everything
        self.states[self.state]()
        #timer updates
        self.timer["duration"] += 1
        self.timer["time"] = self.timer["time"] + 1 if self.timer["time"] < self.timer["reset"] else 0 
        self.timer["grace"] = self.timer["grace"] + 1 if self.timer ["grace"] < self.timer["grace_end"] else 0
        #clear check
        self.cleared = (len(self.spawned_list) <= 0)
    


    def state_start(self):
        #changing around spawn order
        if self.timer['time'] % self.timer['spawn'] == 0:
            #saving values as to what exactly i'm keeping track of
            type_to_spawn = self.spawning_keys[self.spawning_key]
            spawned_id = self.spawn_organized[self.spawning_keys[self.spawning_key]][self.spawning_value]
            offset = self.spawn_offsets[spawned_id[0]][spawned_id[1]]


            #finding the spawning entrance points, like the galaga loop-de-loop
            if type_to_spawn in self.world_data['start_patterns'].keys() and len(self.world_data['start_patterns'][type_to_spawn]) > 0:
                #fetching entrance points immediately
                entrance_info = entrance_points = self.world_data['start_patterns'][type_to_spawn]
                entrance_points = entrance_info['patterns']
            else:
                #if no entrance points
                entrance_points = None
            
            #finding the skin to use
            ### REMOVED IN FINAL AS EACH ENEMY ONLY HAS 1 SKIN.
            # spawn_skin = self.world_data['skins'][type_to_spawn] if type_to_spawn in self.world_data['skins'].keys() else None
            
            #using overwrite to change type_to_spawn, only at the end
            # so pretty much what this does is attribute a different enemy class if it's not the default A,B,C, or D.
            # this won't be needed later.
            # if type_to_spawn in self.world_data['overwrite'].keys():
            #     type_to_spawn = self.world_data['overwrite'][type_to_spawn]


            #creating enemy
            char = enemies.loaded[type_to_spawn](
                offset=offset,
                pos=self.pos,difficulty=self.difficulty,sprites=self.sprites,player=self.player,
                entrance_points=entrance_points[self.enter_key] if entrance_points is not None else None,
                entrance_speed=entrance_info['speed'] if entrance_points is not None else None,
                # skin=spawn_skin, # REMOVED the changing skins, and replacing them with defaults.
                trip=entrance_info['shoot'] if entrance_points is not None else [999],
                formation=self,
                window=self.window,
                # bullet_texture=self.world_data['bullet_texture'], - REMOVED to make the game less confusing
                # is_demo=self.is_demo
            )
            #adding enemy to groups
            self.spawned_list.append(char)
            self.sprites[2].add(char)

            #resetting enter key
            if entrance_points is not None:
                self.enter_key += 1
                if self.enter_key >= len(entrance_points):
                    self.enter_key = 0

            #new column
            self.spawning_value += 1
            self.timer['spawn'] = entrance_info['timer'] if entrance_points is not None else 1 #keeping the timer quick
            #new row / new character set
            if self.spawning_value >= len(self.spawn_organized[self.spawning_keys[self.spawning_key]]):
                self.spawning_value = 0 
                self.spawning_key += 1
                self.enter_key = 0 
                self.timer['spawn'] = 180 #a pause between spawning
            #finished
            if self.spawning_key >= len(self.spawning_keys):
                self.state = 'idle'
                self.timer['duration'] = 0 #keeping the formation from teleporting down and killing you. it will only do that in idle
        
        
        self.update_movement()#keepin 'em moving




    def state_idle(self): #resting state, attacking, etc.
        #running a bunch of predefined methods
        self.check_for_atk()
        self.remove_dead()
        self.update_movement()



    def state_leave(self): #leaving but animated
        #moving
        self.leave_y_momentum -= 0.25
        self.pos[1] += self.leave_y_momentum
        #destroying
        if self.pos[1] <= -1000:
            self.state = "destroy"
        #updating enemy pos
        for char in self.spawned_list:
            char.formationUpdate(self.pos)


    def start_state_leave(self): #starting the leaving animation
        self.leave_y_momentum = 7
        self.state = 'leave'


    def state_destroy(self): #killing everything
        self.empty()
        self.state='done'
    

    def state_done(self):
        ...


    def check_for_atk(self): #throwing down an enemy to attack the player
        #only runs if the timer is ok
        if (self.timer["time"] % self.timer["atk"] == 0) and (self.timer["grace"] < self.timer["grace_start"]):
            #counting all enemies in idle 
            atk_count = 0
            trip = False #a trip to see if the enemies are still entering - WILL NOT ATTACK
            idle_count = []
            for _ in enumerate(self.spawned_list):
                if _[1].info['state'] == 'attack': atk_count += 1
                if _[1].info['state'] == 'enter': trip=True
                elif _[1].info['state'] == 'idle' and _[1].info['atk']: idle_count.append(_[0])
            if (atk_count <= self.attack["max"] and len(idle_count) > 0) and not trip:
                self.make_attack(idle_count)
    

    def make_attack(self,idle_count:list):
        for i in range(self.attack['amount']):
            index = random.randint(0,(len(idle_count)-1))
            choice = idle_count[index]
            if self.spawned_list[choice].info['state'] != 'attack':
                self.spawned_list[choice].change_state('attack')
            idle_count.pop(index)
            if len(idle_count) < 1: 
                break
        return


    def update_movement(self): #updating where the idle position is
        if self.state != "start":
            add = 0 
        else:
            add = (self.timer["duration"]*self.world_data["form_drop_speed"])
        self.pos[1] = 45 + (math.sin(self.timer["duration"] * 0.1) * 15) + add
        for char in self.spawned_list:
            char.formationUpdate(self.pos)


    def find_spawn_list(self,level,world_data) -> list:
        spawn_list = []
        rows,columns = random.randint(5,10),random.randint(10,12)
        if world_data["random"]: 
            #trip to see if an entire form should be random
            for row in range(rows):
                spawn_list.append("")
                for column in range(columns):
                    spawn_list[row] += random.choice(("A","B","C","D"))
        #picking an ordered form from the set
        elif world_data['manual_ordered']:
            #the easy way, since arithmetic SUCKS
            index = level
            while index >= len(world_data['manual_order']):
                index -= len(world_data['manual_order'])
            index = world_data['manual_order'][index]
            spawn_list = world_data['manual_formations'][index]
            del index
        #picking a random form from the set
        else:
            spawn_list = random.choice(world_data["manual_formations"])
        return spawn_list


    def empty(self):
        for enemy in self.spawned_list:
            enemy.kill()
        self.sprites[2].empty()


    def remove_dead(self):
        #06/06/2023 - removing dead enemies
        # The formation copies the list (1), enumerates through the list (2), and deletes all dead items (3)
        if self.timer['time'] % self.timer['dead'] == 0:
            copy=[item for item in self.spawned_list] #(1)
            for _ in enumerate(self.spawned_list,0): #(2)
                if _[1].info['dead']: 
                    self.spawned_list.pop(_[0]) #(3)
                    # print('removed',str(_[0]))
            copy = []


    def draw_img(self,window=None):
        if window is None: window=self.window
        if self.image is None or window is None or self.image_hide:
            return
        window.blit(self.image,(self.pos[0]-25,self.pos[1]-75))
        






#5/30/2023 - FORMATION CODE
# a lot of this is added from RevC as well. 
# class Formation():
    
    

#     def __init__(self,
#                 player, #player object

#                 world_data:dict, #level data info, for positioning and such
#                 sprites:dict, #sprite groups, from main
#                 level:int = 1, #the total amount of levels passed, usually used for intensities or score
#                 level_in_world:int = 1, #the amount of levels completed in the world currently 

#                 **kwargs,
#                  ):
        
#         #5/30/2023 - VARIABLES BASED OFF ARGUMENTS
#         self.state = "start"
#         self.player = player
#         self.world_data = world_data
#         self.level = level
#         self.level_in_world = level_in_world
#         self.sprites = sprites

#         #5/30/2023 - POSITIONING OF FORMATION
#         self.pos = [225,100] #centered position of formation. 
#         self.speed = 1
#         self.direction = random.choice(('l','r'))
#         self.duration = 0
        
#         #05/30/2023 - CHARACTERS' SPAWNING
#         self.spawning_timer = 0 #frame counter in the startup state for how long it takes to spawn a character
#         self.spawning_index = [0,0] #counter for where in self.spawn_list the spawner is currently at, as to not get confused with anything else
#         self.spawned_list = [] #a list of spawned characters, the actual objects for the formation to look at and do checks on ; unordered
#         self.completed_level = False #checking if the level (formation) is complete and needs to be reset;  run with the timers

#         #06/22/2023 - FIGURING OUT WHAT'S IN THE FORMATION BASED ON LEVEL DATA
#         self.spawn_list = [["nope"],["nope"]] #default spawn

#         #06/22/2023 - MANUAL ORDERED
#         if self.world_data["manual_type"] == 1:
#             spawn_len = len(self.world_data["manual_formations"])
#             loops = (self.level_in_world-1) // spawn_len
#             subtractor = loops * spawn_len
#             #IF LOOPED:
#             if self.world_data["manual_loop"] or subtractor < 0:
#                 self.spawn_list = self.world_data["manual_formations"][(self.level_in_world-1) - subtractor] #a list of characters to spawn, and that's it
#             #IF NOT LOOPED: 
#             elif subtractor > 0 and not self.world_data["manual_loop"]:
#                 self.spawn_list = self.random_formation()

#         #06/23/2023 - RANDOM
#         elif self.world_data["manual_type"] == 2:
#             # pick_manual is based off a value called "manual_influence", where if the value is satisfied, it will pick a manual formation instead of a random one
#             pick_manual:bool = (random.randint(1,100) <= self.world_data["manual_influence"])
#             if pick_manual: 
#                 self.spawn_list = random.choice(self.world_data["manual_formations"])
#             # however, it usually just picks something random
#             else:
#                 self.spawn_list = self.random_formation()
        
#         else:
#             self.spawn_list = self.random_formation()


            



#         # #test- spawning A character
#         # self.test = characters.loaded["nope"](sprites=self.sprites,level=self.level,formation_position=self.pos,offset=(0,0),data=self.data,)
#         # self.sprites[0].add(self.test);self.sprites[2].add(self.test)
        
#         #06/06/2023 - Timer for checking things without checking them every frame 
#         self.timer:int = 0
#         self.timer_dead_check:int = 30 #how many frames before checking for a dead character
#         self.timer_dead_copylist = [] #a copy of the character list for kill checking purposes
#         self.timer_reset_rate = 120 #how many frames before the timer resets
    
#         #06/06/23 - calculating center position
#         # Calculate total length of formation, divide by 2, take center screen and subtract by half length
#         # this is why EVERY FORMATION SHOULD HAVE THE SAME LENGTH OF COLUMNS IN EACH ROW NO MATTER WHAT
#         self.pos[0] = ((pygame.display.play_dimensions[0]/2) - (len(self.spawn_list[1])*self.world_data["char_distance_x"] /2))

#         #08/21/2023 - Leave animation
#         # If a game over is encountered, the formation flies off the screen
#         self.leave_y_momentum = 0


#     def update(self):
#         #updating timer
#         self.timer = self.timer + 1 if self.timer < self.timer_reset_rate else 1
#         #updating states
#         if self.state == 'start':self.state_start()
#         if self.state == 'idle':self.state_idle()
#         if self.state == 'destroy':self.state_destroy()
#         if self.state == 'leave':self.state_leave()
#         #updating misc
#         self.remove_dead()
        


#     def state_start(self):
#         #06/06/2023 - SPAWNING CHARACTERS
#         #counts for a set amount of frames and spawns in each character in the formation
#         #think like how space invaders has a set amount of "characters" in a "formation" where they all move, but they all spawn in an order to make it look nice
#         #every time a character is spawned, the timer resets and the index is risen
#         self.spawning_timer += 1
#         if self.spawning_timer >= self.world_data["spawn_time"]:

#             #06/22/2023 - figuring out what character to spawn
#             to_spawn = self.spawn_list[self.spawning_index[1]][self.spawning_index[0]]
            
#             if to_spawn in characters.loaded.keys():
#                 #spawning the character - note the data in spawning_index is what is to be spawned CURRENTLY, not previously
#                 cur_char = characters.loaded[to_spawn](
#                     sprites=self.sprites,
#                     level=self.level,
#                     formation_position=self.pos,
#                     offset=(
#                         self.spawning_index[0]*self.world_data["char_distance_x"],
#                         self.spawning_index[1]*self.world_data["char_distance_y"]),
#                     data=self.data,)
#                 self.spawned_list.append(cur_char)
#                 self.sprites[0].add(cur_char);self.sprites[2].add(cur_char)
            
#             #resetting timer values, raising the value of the spawning_timer's y value
#             self.spawning_timer = 0
#             self.spawning_index[0] += 1
            
#             #the y value of spawning_timer is the x value of the spawn_list, vice versa.
#             if self.spawning_index[0] > (len(self.spawn_list[self.spawning_index[1]])-1):
#                 self.spawning_index[0] = 0;self.spawning_index[1] += 1
#             #checking for being finished
#             if self.spawning_index[1] > (len(self.spawn_list)-1):
#                 self.state = "idle"
#                 self.spawning_index = (0,0)
#                 self.duration = 0 


#     def state_idle(self):
#         self.check_for_atk()
#         self.update_movement()

#     def state_destroy(self):...

#     def state_leave(self):
#         self.leave_y_momentum -= 0.25
#         self.pos[1] += self.leave_y_momentum
#         if self.pos[1] <= -1000:
#             self.state = "destroy"
#         for char in self.spawned_list:
#             char.formationUpdate(self.pos)

#     def start_state_leave(self):
#         self.leave_y_momentum = 7
#         self.state = 'leave'


#     def check_for_atk(self):
#         #06/06/2023 - Spawning in characters
#         # Quick thing to note, I realized there was no need to constantly update everything
#         # So it only updates when a character *needs* to be thrown.
#         if (self.timer%self.world_data['throwdown_time']==0):
#             atk_count = 0
#             idle_char = []
#             #06/06/2023 - Creating values
#             for _ in enumerate(self.spawned_list):
#                 if _[1].state == 'atk': atk_count += 1
#                 elif _[1].state == 'idle': idle_char.append(_[0])
#             #06/06/2023 - Checking for conditions for character throwdown to be complete
#             if atk_count <= self.world_data['max_char'] and len(idle_char) > 0:
#                 self.attack(idle_char)
            
    

#     def attack(self,idle_char:list):
#         for i in range(self.world_data['throwdown_amount']):
#             self.spawned_list[random.choice(idle_char)].stchg('attack')


#     def update_movement(self):
#         self.duration += 1
#         self.pos[1] = math.sin(self.duration * 0.1) * 15 + ((self.duration*0.25) if self.state != "start" else 0)
#         for char in self.spawned_list:
#             char.formationUpdate(self.pos)
    
#     def remove_dead(self):
#         #06/06/2023 - removing dead characters
#         # The formation copies the list (1), enumerates through the list (2), and deletes all dead items (3)
#         if self.timer % self.timer_dead_check == 0:
#             self.timer_dead_copylist.append(item for item in self.spawned_list) #(1)
#             for _ in enumerate(self.spawned_list,0): #(2)
#                 if _[1].dead: 
#                     self.spawned_list.pop(_[0]) #(3)
#                     # print('removed',str(_[0]))
#             self.timer_dead_copylist = []
#             #06/06/2023 - checking for a completed formation   
#             # remember, this is used as a signal/flag externally for the playstate to 
#             self.completed_level = len(self.spawned_list) <= 0

#     def empty(self):
#         for i in range(len(self.spawned_list)):
#             self.spawned_list[i].kill()
#         self.spawned_list = []
#         self.state = "complete"
#         self.completed_level = True

#     def random_formation(self) -> list:
#         #06/23/23 - GENERATING A RANDOM FORMATION FOR LOOPS, OR JUST TYPES IN GENERAL
#         # return [["nope"],["nope"]] #TEMPORARY - CHANGE loaded_characters
#         spawn_list = []
#         # generating sizes 
#         rows = random.randint(self.world_data["char_min_height"],self.world_data["char_max_height"])
#         columns = random.randint(self.world_data["char_min_width"],self.world_data["char_max_width"])
#         # generating spawnsheet
#         for row in range(rows):
#             # adding a new row
#             spawn_list.append([])
#             # adding individual columns
#             for column in range(columns):
#                 spawn_list[row].append(
#                     random.choice(
#                         self.world_data["imports"]
#                         )
#                     )
#         return spawn_list




# OLD FORMATION 1 
# class Formation:
#     def __init__(
#         self, player, level, file=None, total_level=1  # levels in world
#     ):  # total level takes worlds into account
#         # print("==============NEW FORMATION")

#         # DEFINITIONS
#         self.state = "start"  # level's state; "start","idle", and "complete"
#         self.file = file  # level's python file
#         self.player = player  # the player object
#         self.level = level  # current level number ; for intensities

#         self.pos = [0, 100]  # position lol
#         self.direction = random.choice(["l", "r"])  # direction, either 'l' or 'r'
#         self.speed = 0  # speed the formation moves in idle
#         self.current_frame = 0  # calculating when to throw a character down, or when to spawn a character

#         self.total_characters = 0  # total amount of characters
#         self.spawn_list = {}  # spawnlist
#         self.spawned_formation = []  # spawned characters
#         available_char = self.file.imports  # characters that can be randomly generated

#         # calculating characters to use
#         self.used_char = [available_char[0]]
#         if len(available_char) >= 2:
#             chunk = self.file.level_length / (len(available_char) - 1)

#             for _ in range(int(level // chunk)):
#                 if len(self.used_char) < len(available_char):
#                     self.used_char.append(available_char[_ + 1])
#         self.formation_size = [0, 0]  # size of the formation

#         self.spawn_list = self.generate_spawn_list()

#         # FORMATION SIZE
#         # SPAWN*LIST* SIZE
#         self.formation_size[1] = len(self.spawn_list)  # vertical size is figured out
#         for row in self.spawn_list:
#             if (
#                 len(self.spawn_list[row]) > self.formation_size[0]
#             ):  # horizontal size is the longest row
#                 self.formation_size[0] = len(self.spawn_list[row])
#         # CENTERING FORMATION BASED ON SIZE
#         self.pos[0] = 225 - (self.formation_size[0] * self.file.char_distance_x / 2)

#         # formation spawn code
#         self.spawn_list_indexes = []
#         self.columns = 0  # instead of using the y value for some things, we use *columns*, because some blank indexes get left out
#         self.current_row = 0  # this is so we know when to reset columns
#         # this will append every index in the formation spawn list so the start state can add them in order without any complex loops
#         for i in range(len(self.spawn_list)):
#             self.spawned_formation.append([])
#             for j in range(len(self.spawn_list[i])):
#                 self.spawn_list_indexes.append((i, j))
#         # potential item spawn
#         self.items_to_spawn = {}
#         #puts an item in a character if the timing is right and the player has no shield#
#         if (self.player.bullet == "default") and (
#             self.level % self.file.drop_health == 0
#         ):
#             self.items_to_spawn[random.choice(self.spawn_list_indexes)] = (
#                 "health",
#                 None,
#             )
#         #puts a bullet in a character if random chance#
#         if (
#             random.randint(0, 100) < self.file.drop_bullet
#             and len(self.file.bullets) > 0
#         ):
#             self.items_to_spawn[random.choice(self.spawn_list_indexes)] = (
#                 "bullet",
#                 random.choice(self.file.bullets),
#             )
#             # print("CONDITION MET")

#     def update(self):
#         # self-explanatory
#         if self.state == "idle":
#             self.idle()
#         elif self.state == "start":
#             self.start()
#         elif self.state == "exit":
#             self.exit()

#         # self.update_size()
#         self.update_character_formation_pos()
#         if self.state != "start":
#             self.remove_dead()

#     def idle(self):
#         # actually moving
#         self.formation_move()
#         # attacking based on time
#         self.calculate_attack_time()

#     def start(self):
#         # moving formation
#         self.formation_move()

#         # checking if time has passed
#         self.current_frame += 1

#         if self.current_frame >= 20:  # DEBUG - CHANGE TO 6
#             # index = random.randint(0,len(self.spawn_))

#             # resetting timer
#             self.current_frame = 0

#             # breaking out of start state to prevent error
#             if len(self.spawn_list_indexes) <= 0:
#                 self.state = "idle"
#                 return
#             # resetting columns
#             if self.spawn_list_indexes[0][0] != self.current_row:
#                 self.current_row = self.spawn_list_indexes[0][0]
#                 self.columns = 0
#             # spawning a character
#             try:
#                 # adds a character to the formation
#                 self.spawned_formation[self.spawn_list_indexes[0][0]].append(
#                     loaded_characters[
#                         self.spawn_list[self.spawn_list_indexes[0][0]][
#                             self.spawn_list_indexes[0][1]
#                         ]
#                     ].Char(
#                         args={
#                             "groups": groups,
#                             "player": self.player,
#                             "formation_position": self.pos,
#                             "offset": (
#                                 (
#                                     self.spawn_list_indexes[0][1]
#                                     * self.file.char_distance_x
#                                 ),
#                                 (
#                                     self.spawn_list_indexes[0][0]
#                                     * self.file.char_distance_y
#                                 ),
#                             ),
#                             "level": self.level,
#                         }
#                     )
#                 )
#                 #INDEX REFERENCE
#                 #items_to_spawn: KEY, (row,column) ; VALUE, (item_type,item_name)
#                 #spawned_formation: [FIRST BRACKET], LIST OF ROWS ; [SECOND BRACKET], CHARACTERS IN ROW
#                 #
#                 # print(self.spawned_formation)
#                 for key, value in self.items_to_spawn.items():
#                     if key[0] <= (len(self.spawned_formation) - 1):
#                         # print("ROW CONDITION MET |",str(key),"|",str(self.spawned_formation))
#                         if key[1] <= len(self.spawned_formation[key[0]]) - 1:
#                             self.spawned_formation[key[0]][key[1]].container = value
#                             # print("ITEM ADDED")
#                             self.items_to_spawn.pop(key)
#                             break
#                         else:
#                             # print("COLUMN CONDITION NOT MET |", str(key) , str(self.spawned_formation[key[0]]))
#                             pass
#             # ignoring emtpy enemy spaces -
#             except KeyError:
#                 self.spawn_list_indexes.pop(0)
#                 return
#             # adding to group
#             groups["universal"].add(
#                 self.spawned_formation[self.spawn_list_indexes[0][0]][self.columns]
#             )
#             groups["enemy"].add(
#                 self.spawned_formation[self.spawn_list_indexes[0][0]][self.columns]
#             )

#             # instead of using the y value for some things, we use *columns*, because some blank indexes get left out
#             self.columns += 1

#             # deleting index 0 so the next one is in line
#             self.spawn_list_indexes.pop(0)

#     def exit(self):
#         self.current_frame += 1

#         if self.current_frame >= 6:
#             self.current_frame = 0
#             groups["universal"].add(
#                 shared.dieBoom(self.spawned_formation[0][0].rect.center, (50, 50))
#             )
#             self.spawned_formation[0][0].state = "dead"
#             self.spawned_formation[0][0].kill()

#     def calculate_attack_time(self):
#         # calculating when to make a character attack

#         self.current_frame += 1
#         total_attack_enemies = 0

#         # calcuating the amount of enemies attacking
#         for i in range(len(self.spawned_formation)):
#             for j in range(len(self.spawned_formation[i])):
#                 if self.spawned_formation[i][j].state == "attack":
#                     total_attack_enemies += 1
#         # checking if the right amount of enemies are attacking and if enough time has passed
#         if (self.file.maxChar is None or total_attack_enemies < self.file.maxChar) and (
#             self.current_frame >= self.file.spawn_time
#         ):
#             self.attack()
#             self.current_frame = 0

#     def attack(self):
#         # current characters in idle
#         idle_list = []

#         # checks characters and adds ones in idle to idle_list
#         for i in range(len(self.spawned_formation)):
#             for j in range(len(self.spawned_formation[i])):
#                 if self.spawned_formation[i][j].state == "idle":
#                     idle_list.append((i, j))
#         # picking a random character to make attack
#         if len(idle_list) > 0:
#             chosen_list = random.choice(idle_list)
#             del idle_list
#             self.spawned_formation[chosen_list[0]][chosen_list[1]].state = "attack"
#             return

#     def update_character_formation_pos(self):
#         # updating the characters on what the formation position is
#         for i in range(len(self.spawned_formation)):
#             for j in range(len(self.spawned_formation[i])):
#                 self.spawned_formation[i][j].formationUpdate(self.pos)

#     def formation_move(self):
#         # updating the movement

#         # changing the direction from right to left
#         if self.pos[0] >= (500 - (self.formation_size[0] * self.file.char_distance_x)):
#             self.speed -= self.file.speed * 0.025
#             self.direction = "l"
#         # changing the direction from left to right
#         elif self.pos[0] <= 10:
#             self.speed += self.file.speed * 0.025
#             self.direction = "r"
#         # speeding up if no direction change
#         else:
#             if self.direction == "l":
#                 self.speed = self.file.speed * -1
#             elif self.direction == "r":
#                 self.speed = self.file.speed
#         # updating positions based on speed
#         self.pos[0] += self.speed
#         self.pos[1] = math.sin(self.pos[0] / 10) * 10 + 100

#     def random_spawn_list(self):
#         # randomly generates characters and puts them in a formation
#         formation = {}

#         # column size based on current level
#         column_size = int(
#             self.file.char_min_width
#             + (  # minimum value
#                 (self.level / self.file.level_length)
#                 * (self.file.char_max_width - self.file.char_min_width)  # percent
#             )  # amount of variation
#         )
#         row_size = int(
#             self.file.char_min_height
#             + (  # minimum value
#                 (self.level / self.file.level_length)
#                 * (self.file.char_max_height - self.file.char_min_height)  # percent
#             )  # amount of variation
#         )

#         # print(str(self.level) + "|" + str(self.file.level_length) + "|" + str(column_size) + "|" + str(row_size))

#         for i in range(row_size):  # row generation
#             formation[i] = []
#             for j in range(column_size):  # column generation
#                 formation[i].append(random.choice(self.used_char))
#         return formation

#     def generate_spawn_list(self):
#         spawn_list = {}
#         # SPAWNLIST
#         manual = (
#             len(self.file.manual_formations) > 0 and self.file.manual_type != 0
#         )  # boolean value, figures out if formation is manual
#         # manual spawn list
#         if manual:
#             # random manual formation
#             if self.file.manual_type == 1:
#                 # picks a random manual_formation a certain percent of the time, randomly generates one the other percent
#                 if (
#                     random.randint(0, 100) < self.file.manual_influence
#                 ):  # chance picks a manual formation
#                     spawn_list = random.choice(self.file.manual_formations)
#                 else:  # chance picks elsewise
#                     spawn_list = self.random_spawn_list()
#             # ordered manual formation
#             elif self.file.manual_type == 2:
#                 # nonlooping
#                 if not self.file.manual_loop:
#                     # if level is within the length of the formations
#                     if self.level <= len(self.file.manual_formations):
#                         spawn_list = self.file.manual_formations[
#                             self.level - 1
#                         ]  # level -1 because it doesn't start at 0
#                     # if level has surpassed length of the formations
#                     else:
#                         spawn_list = self.random_spawn_list()
#                 # looping
#                 else:
#                     # shedding the looped numbers off of levels
#                     index = self.level - (
#                         len(self.file.manual_formations)
#                         * ((self.level - 1) // len(self.file.manual_formations))
#                     )
#                     # setting formation
#                     spawn_list = self.file.manual_formations[index - 1]
#         # random spawn list
#         else:
#             spawn_list = self.random_spawn_list()
#         return spawn_list

#     def update_size(self):
#         # UPDATING SIZE BASED OFF SPAWN
#         self.formation_size[1] = len(
#             self.spawned_formation
#         )  # vertical size is figured out
#         for row in self.spawned_formation:
#             if len(row) > self.formation_size[0]:  # horizontal size is the longest row
#                 self.formation_size[0] = len(row)

#     def remove_dead(self):
#         # deleting dead characters
#         for row in range(len(self.spawned_formation)):
#             for column in range(len(self.spawned_formation[row])):
#                 if self.spawned_formation[row][column].state == "dead":
#                     self.spawned_formation[row].pop(column)
#                 break
#         # deleting empty rows
#         for row in range(len(self.spawned_formation)):
#             if len(self.spawned_formation[row]) == 0:
#                 self.spawned_formation.pop(row)
#                 break
#         # changing state to "complete" if there are no rows
#         if len(self.spawned_formation) == 0:
#             self.state = "complete"

#     def destroy(self):
#         # deletes all characters
#         for i in range(len(self.spawned_formation)):
#             for j in range(len(self.spawned_formation[i])):
#                 self.spawned_formation[i][j].kill()
#         # empties
#         self.spawned_formation = []
#         self.state = "complete"

