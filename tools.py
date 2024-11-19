from math import sqrt,atan2,sin,cos,radians


#a moving point class that calculates the distances and how much to move
class MovingPoint():
    def __init__(self,pointA:tuple,pointB:tuple,speed:int=1,ignore_speed:bool=False,check_finished:bool=False):
        #defining values
        self.pointA,self.pointB = pointA,pointB #saving points
        self.position = list(self.pointA)
        #more arguments
        self.finished = False ; self.check_finished = check_finished
        self.ignore_speed = ignore_speed #A value to make the speed separate from the calc_move_vals function to change speeds separately
        self.speed = speed
        #calculations
        self.finished = MovingPoint.calc_distance_bool(pointA,pointB,self.speed*5) #calculating distance
        self.move_vals = MovingPoint.calc_move_vals(self.pointA,self.pointB,speed = (speed if not ignore_speed else 1)) #calculating values
        
        


    #called every frame
    def update(self):
        self.position[0] += (self.move_vals[0] if not self.ignore_speed else self.move_vals[0]*self.speed)
        self.position[1] += (self.move_vals[1] if not self.ignore_speed else self.move_vals[1]*self.speed)
        #checking for finish, the only need for distance
        if self.check_finished:
            self.finished = MovingPoint.calc_distance_bool(self.position,self.pointB,self.speed*5)


    #updating everything if needed
    def change_all(self,pointB):
        self.pointB = pointB
        if self.check_finished: self.finished = MovingPoint.calc_distance_bool(self.pointA,self.pointB,self.speed*5) #yea
        self.move_vals = MovingPoint.calc_move_vals(self.position,self.pointB,speed=(self.speed if not self.ignore_speed else 1)) #calculating values



    @staticmethod
    def calc_move_vals(pointA:tuple,pointB:tuple,speed:int=1) -> tuple: #calculating how much to move
        angle = atan2(pointB[1] - pointA[1], pointB[0] - pointA[0])
        return (
            cos(angle) * speed,
            sin(angle) * speed
        )
    


    @staticmethod
    def calc_distance(pointA:tuple,pointB:tuple): #calculating distance, self explanatory
        return sqrt(
                ((pointB[0]-pointA[0])**2) + 
                ((pointB[1]-pointA[1])**2)
            ) 



    @staticmethod 
    def calc_distance_bool(pointA:tuple,pointB:tuple,range:float):
        # a WAAAAY less complicated way of using the distance, because it's only subtraction now!
        return (abs(pointA[0]-pointB[0]) < range) and (abs(pointA[1]-pointB[1]) < range)





#an angular version of the movingpoint class
class AnglePoint():
    def __init__(self,pointA:tuple,angle:int,speed=1,static_speed:bool=True,**kwargs):
        self.angle = radians(angle)
        self.speed = speed
        self.static_speed = static_speed
        self.move_vals = AnglePoint.calc_move_vals(angleRAD = self.angle, speed = speed, static_speed = static_speed)
        self.position = list(pointA)
    
    def update(self):
        self.position[0] += self.move_vals[0] * (self.speed if not self.static_speed else 1)
        self.position[1] += self.move_vals[1] * (self.speed if not self.static_speed else 1)
    
    
    @staticmethod
    def calc_move_vals(angleRAD:float,speed:int,static_speed:bool=True):
        return (
            cos(angleRAD) * (speed if static_speed else 1),
            sin(angleRAD) * (speed if static_speed else 1)
        )




#a movingpoint that moves across a list of points
class MovingPoints(MovingPoint):
    def __init__(self,pos:tuple,points:list,speed:int=1,final_pos:list=None):
        self.pos = list(pos)
        self.points = points #points to follow
        self.cur_target = 0 #which point in points to target
        self.speed = speed
        self.finished_part = MovingPoint.calc_distance_bool(self.pos,self.points[self.cur_target],self.speed*5)
        self.move_vals = MovingPoint.calc_move_vals(self.pos,self.points[self.cur_target],self.speed)
        
        #checking for finish
        self.finished = False
        #the final position to go to if finished
        self.final_pos = [final_pos,] if final_pos is not None else None
        #a trigger to see if the final pos has been reached yet
        self.final_trigger = False if self.final_pos is not None else True
        #a trip for events to occur in the host object
        self.trip=False
        
    def update(self):
        if not self.finished:
            #updating
            self.pos[0] += self.move_vals[0]
            self.pos[1] += self.move_vals[1]
            self.finished_part = MovingPoint.calc_distance_bool(self.pos,self.points[self.cur_target],self.speed*5)
            #checking for completion
            if self.finished_part:
                self.cur_target += 1
                #fully completing
                self.finished = self.cur_target >= len(self.points)
                if self.finished and not self.final_trigger:
                    #tripping the final position to go to
                    self.points = self.final_pos
                    self.cur_target = 0 
                    self.final_trigger = True
                    self.finished = False
                    self.distance = MovingPoint.calc_distance_bool(self.pos,self.points[self.cur_target],self.speed*5)
                    self.move_vals = MovingPoint.calc_move_vals(self.pos,self.points[self.cur_target],self.speed)
                    return
                elif self.finished:
                    return
                #if not, updating values
                else:
                    self.distance = MovingPoint.calc_distance(self.pos,self.points[self.cur_target])
                    self.move_vals = MovingPoint.calc_move_vals(self.pos,self.points[self.cur_target],self.speed)
                #no matter what, tripping the switch for evemy movement (REMOVE THIS IF NOT IN YUP)
                self.trip=True



#pygame.Cock but global now
class Clock(): # a redo of pygame.clock to add more values
    def __init__(self,clock,FPS=60): #initiating stuff
        self.FPS = FPS
        self.clock = clock
        self.offset = 1
    def tick(self): #updating clock
        self.clock.tick(self.FPS)
        self.offset = 60/(self.clock.get_fps() if self.clock.get_fps() != 0 else 60)







#global values -- gonna change this to globals soon
demo = False
debug = False


#global logs
log = {"kills":0,"got_away":0,"shots":0,"hits":0,"damage":0}
world_log = log.copy()
def update_log():
    for k,v in world_log.items():
        log[k] = world_log[k]
        world_log[k] = 0