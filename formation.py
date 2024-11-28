# Program by Andrew Church
import random,pygame,math,enemies,random
from anim import all_loaded_images as img

class Formation():
    def __init__(self,
                level,
                sprites,
                player,
                char_list:list,
                start_patterns:list,
                difficulty:float,
                # is_demo:bool=False,
                **kwargs
                ):
        #basic info
        self.state = "start" 
        self.char_list = char_list
        self.start_patterns=start_patterns
        self.sprites = sprites
        self.player = player
        self.level = level
        self.difficulty = difficulty
        self.window = kwargs['window'] if 'window' in kwargs.keys() else None
        # self.is_demo = is_demo #to tell if the game is being used in the title demo -> stops score
        # print(difficulty)png

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
        self.spawn_list = Formation.find_spawn_list(level=self.level, difficulty=self.difficulty, char_list=self.char_list)
        # print(self.spawn_list)
        self.spawned_list = []

        #SPAWN INFO - the game stores the offset value here in order to spawn enemies in special ways, so now they don't all have to spawn in order
        self.spawn_offsets = [] #declaration
        #iterating through spawn list 
        for row in range(len(self.spawn_list)):
            self.spawn_offsets.append([])
            #adding the offset. note it is not labeled because spawn info iterations would work on this one
            for column in range(len(self.spawn_list[row])):self.spawn_offsets[row].append((column*35,row*35))
        
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
        self.pos[0] = (pygame.display.play_dimensions[0]/2) - ((len(self.spawn_list[0])*35)/2)

        #difficulty calculations
        # self.difficulty = self.level//1
        self.difficulty_rounded = int(self.difficulty//1)
        self.attack={
            #throwdown amount = how many enemies are thrown down in an attack stance #goes up once every 10 levels
            "amount":((self.difficulty_rounded//3)+1) if (self.difficulty_rounded <= 6) else 3,
            "max":3+(self.difficulty_rounded*2),
        }
        # DIFFICULTY HARD-CODED CALCULATIONS
        if self.difficulty <= 1.2:
            self.timer['atk'] = 100 
        elif self.difficulty <= 3:
            self.timer['atk'] = 100-(self.difficulty-1.5)*20
        elif self.difficulty <= 5:
            self.timer['atk'] = 40-(self.difficulty-3)*10
        elif self.difficulty <= 8:
            self.timer['atk'] = 30-(self.difficulty-5)*10
        elif self.difficulty <= 10:
            self.timer['atk'] = 10 - (self.difficulty - 8)*1
        self.timer['atk'] = (100 - (self.difficulty*4)) if self.difficulty < 25 else 1
        print(self.difficulty,self.timer["atk"])
        #timer["atk"] = how often enemies are thrown down to attack #goes down a frame every level
        #max_enemies = how many enemies can be down at a time, goes up by 1 every 5 levels
        
        #grace periods get slightly longer and start more often as the game gets harder
        # self.timer['grace_start'] = (480 - self.difficulty*20) if self.difficulty < 10 else 60
        # self.timer['grace_end'] = self.timer['grace_start']+60 + (self.difficulty * 15 if self.difficulty < 4 else 60)

        #a key used to figure out what enemy is to be spawned during the start state.
        self.enter_key = 0 #what is used for spawning entrance values, yada yada yada

    def update(self):
        #updating everything
        self.states[self.state]()
        #timer updates
        self.timer["duration"] += 1
        self.timer["time"] = self.timer["time"] + 1 if self.timer["time"] < self.timer["reset"] else 0 
        # self.timer["grace"] = self.timer["grace"] + 1 if self.timer ["grace"] < self.timer["grace_end"] else 0
        #clear check
        self.cleared = (len(self.spawned_list) <= 0)
    


    def state_start(self):
        #changing around spawn order
        if self.timer['time'] % self.timer['spawn'] == 0:
            #saving values as to what exactly i'm keeping track of
            type_to_spawn = self.spawning_keys[self.spawning_key]
            spawned_id = self.spawn_organized[self.spawning_keys[self.spawning_key]][self.spawning_value]
            offset = self.spawn_offsets[spawned_id[0]][spawned_id[1]]

            # ENTRANCE POINTS/START PATTERNS -- LIKE GALAGA THINK ABOUT IT WHOOPEEEE :3
            #fetching entrance points immediately
            entrance_info = self.start_patterns[type_to_spawn]
            entrance_points = entrance_info['patterns']
            

            #creating enemy
            char = enemies.loaded[type_to_spawn](
                offset=offset,
                pos=self.pos,difficulty=self.difficulty_rounded,sprites=self.sprites,player=self.player,
                entrance_points=entrance_points[self.enter_key] if entrance_points is not None else None,
                entrance_speed=entrance_info['speed'] if entrance_points is not None else None,
                # skin=spawn_skin, # REMOVED the changing skins, and replacing them with defaults.
                trip=entrance_info['shoot'] if entrance_points is not None else [999],
                formation=self,
                window=self.window,
                # is_demo=self.is_demo
            )
            # print("FORMATION",self.difficulty)
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
        if (self.timer["time"] % self.timer["atk"] == 0): #and (self.timer["grace"] < self.timer["grace_start"]):
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
        for i in range(random.randint(1,3)):
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
            add = (self.timer["duration"]*.25)
        self.pos[1] = 45 + (math.sin(self.timer["duration"] * 0.1) * 15) + (self.timer["duration"]*.25) - add
        for char in self.spawned_list:
            char.formationUpdate(self.pos)


    def find_spawn_list(level,difficulty,char_list) -> list:
        ## THIS IS OVERCOMPLICATED
        ## I AM NOT GOING TO KEEP THIS
        ## IT WILL RANDOMLY GENERATE A LIST OF ENEMIES TO SPAWN
        ## IT NO LONGER PICKS PRE-MADE FORMATIONS

        spawn_list = []
        row_min = int(3 if difficulty <= 2 else 5)
        row_max = int(5+difficulty//1 if difficulty < 5 else 10)
        rows,columns = random.randint(row_min,row_max),random.randint(10,12)
        #trip to see if an entire form should be random
        for row in range(rows):
            spawn_list.append([])
            for column in range(columns):
                spawn_list[row].append(random.choice(char_list))
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
        # if window is None: window=self.window
        # if self.image is None or window is None or self.image_hide:
        #     return
        # window.blit(self.image,(self.pos[0]-25,self.pos[1]-75))
        ...
        



