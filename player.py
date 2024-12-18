#Code by Andrew Church
import pygame,anim,math,bullets,audio,tools,random
import gameplay_log as log
# "bar":(
#         "h", #if the bar is horizontal or vertical.
#         450, #x position if vertical, y position if horizontal.
#         (10,590), #the limits on both sides for the player to move on, y positions if vertical, x positions if horizontal
#         1, #gravity. 
#         )



class Player(pygame.sprite.Sprite):

    image = pygame.Surface((30, 30), pygame.SRCALPHA)
    pygame.draw.rect(image,"white",pygame.Rect(0,0,30,30))

    def __init__(self,bar,sprite_groups, demo=False): #again, the demo here is different from tools.demo
        pygame.sprite.Sprite.__init__(self)

        #ARGUMENTATIVE 
        self.bar=bar
        self.sprite_groups = sprite_groups
        self.demo = demo
        

        #IMAGE AND POSITIONING
        self.aimg = anim.AutoImage(host=self,name="YUP",generate_rect=True)
        self.pos = [self.bar[2][1]-((self.bar[2][1]-self.bar[2][0])/2),self.bar[1]]
        

        #MOVEMENT CODE
        self.movement = [
            0, #y velocity
            False, #moving left
            False, #moving right
            False, #jumping
            False, #crouching
            False, #focusing
        ]
        self.movement_old = self.movement[:]

        #how fast the character moves
        self.speed = 7.5
        self.momentum = 0
        self.jumps = 0 # how many times the player has double jumped

        #HEALTH
        self.health = 3
        self.coins = 1
        self.invincibility_counter = 0 
        self.dead = self.health < 1

        #EXTRA
        self.autoshoot = False
        self.autoshoottimer = 0 

        #UPGRADE VALUES -- UNFINISHED
        self.bullet_max = 3 #how many bullets can be on screen at one given time
        self.bullet_time = 16 #shoots once every x frames
        self.bullet_list = ["default"]
        self.bullet_list_index = 0 
        self.current_bullet = self.bullet_list[self.bullet_list_index] #the current bullet being shot at the moment
        self.bullet_lock = False #stop shooting 
        self.bullet_dmg = 1
        # MORE UPGRADE VALUES -- PERKS
        self.perks = {
            "rocketboots":0,
            "child":0,
            "magnet":False,
        }

        # setting the position
        self.rect.center = self.pos


    def update(self):



        #SETTING THE IMAGE. I have no issue resetting the image every frame because it's just a callback to an object
        self.aimg.update()

        # calling to transform the image based on me
        self.image_transformations()

        #collision is just movement
        self.collision()
        self.health_update()

        if self.autoshoot:
            self.autoshoottimer += 1
            # if the autoshoot timer has passed bullet time
            if (self.autoshoottimer >= self.bullet_time) and not self.bullet_lock:
                self.shoot()
                self.autoshoottimer = 0 
        




    def controls(self,event):
        #ENGAGING movement
        if event.type == pygame.KEYDOWN:
            #CALLING MOVEMENT FUNCTIONS
            match event.key:
                case pygame.K_LEFT:
                    self.move(False)
                case pygame.K_RIGHT:
                    self.move(True)
                case pygame.K_UP:
                    self.jump()
                case pygame.K_DOWN:
                    self.crouch(True)
                case pygame.K_LSHIFT:
                    self.focus()
                case pygame.K_RSHIFT:
                    self.focus()
                    
                #SHOOTING
                case pygame.K_z:
                    if not self.bullet_lock:
                        self.shoot()
                        self.autoshoottimer = 0 
                        self.autoshoot = True
                
                # CHANGING WEAPON
                case pygame.K_x:
                    self.bullet_list_index += 1
                    if self.bullet_list_index >= len(self.bullet_list):
                        self.bullet_list_index = 0 
                    self.current_bullet = self.bullet_list[self.bullet_list_index]



            
                    


        #RELEASING movement
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                self.move(False,True)

            if event.key == pygame.K_RIGHT:
                self.move(True,True)

            #un-crouching
            if event.key == pygame.K_DOWN:
                self.crouch(False)
                
            if (event.key == pygame.K_x or event.key == pygame.K_z):
                self.autoshoot = False

            if event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT:
                self.focus(False)
            


        
    def collision(self):
    
        #most collision will now be done in the state, instead of by invidual enemies
        #this is so there's not a huge loop of enemies colliding
        self.momentum = 0 
        multiplier = 0
        if self.movement[1] or self.movement[2]: multiplier += 1
        if self.movement[4]: multiplier *= 0.5
        if self.movement[5]: multiplier *= 0.25
        if self.movement[1]: multiplier *= -1
        self.momentum = self.speed * multiplier
        if (self.pos[0] + self.momentum) < self.bar[2][0] or (self.pos[0] + self.momentum) > self.bar[2][1]: self.momentum = 0
        self.pos[0] += self.momentum        


        #jumping code
        #doing y momentum stuffystuff
        gravity = .3 if not self.movement[5] else 0.1
        self.pos[1] += self.movement[0]*(.33 if self.movement[5] else 1)
        self.movement[0] += gravity if self.movement[0] != 0 else 0
        #landing code
        if self.pos[1]>self.bar[1] and self.movement[0] != 0:
            #finishing the jump, including stopping values
            self.pos[1]=self.bar[1]
            self.movement[0] = 0
            self.aimg.change_anim("land")
            for i in range(5):self.sprite_groups[0].add(bullets.BulletParticle((self.pos[0],self.rect.bottom)))
            self.jumps = 0 #resetting double jump value
            #AUTO CROUCH
            if pygame.key.get_pressed()[pygame.K_DOWN]:
                #crouching
                self.crouch()   


        #updating position
        self.rect.center = self.pos  



    def health_update(self):
        #HEALTH checking
        ##invincibility
        if self.invincibility_counter >= 0: self.invincibility_counter -= 1 
        ##checking for death
        self.dead = self.health < 1



    def on_collide(self,
                   collide_type:int, #the collide_type refers to the sprite group numbers. 0 for universal (not used), 1 for other player elements, 2 for enemies
                   collided:pygame.sprite.Sprite, #the specific object being collided with
                   ):
        ... #moved to enemy classes
            



    def hurt(self,amount:int=1):
        if self.invincibility_counter < 1:
            # actually changing info
            self.health -= amount
            self.invincibility_counter = 60
            if self.health <= 0: 
                self.kill()
            log.log_zone["damage"] += amount

            # graphical / audio stuff
            self.aimg.change_anim("hurt")
            for i in range(20): self.sprite_groups[0].add(bullets.BulletParticle(pos=self.rect.center,texture="redblock"))
            audio.play_sound("ouch.mp3" if self.health > 0 else "scream.mp3")
            
            



    def bounce(self):
        #make the player bounce
        self.movement[0] = self.movement[0] - 7.5 if self.movement[0] <= 0 else -7.5
        self.aimg.change_anim("jump")
        audio.play_sound("boing" + str(random.randint(0,4)) + ".wav")
        for i in range(5):self.sprite_groups[0].add(bullets.BulletParticle((self.pos[0],self.rect.bottom)))

        


    def reset_movement(self):
        self.movement_old = self.movement[:]
        self.movement = [
            self.movement[0], #y velocity
            False, #moving left
            False, #moving right
            self.movement[3], #jumping
            False, #crouching
            False, #focusing
        ]
    
    
    def movement_redo(self):
        self.movement = self.movement_old[:]



    def shoot(self):
        did_shoot = bullets.LOADED[self.current_bullet].shoot(sprite_groups=self.sprite_groups,player=self)
        if not self.movement[4] and did_shoot: 
            self.aimg.change_anim("shoot")
            audio.play_sound("bap1.wav")

    def move(self,dir:bool=True,release:bool=False):
        if not release: 
            if dir:
                self.movement[2] = True
                self.movement[1] = False
            else:
                self.movement[1] = True
                self.movement[2] = False
        elif release:
            if dir:
                self.movement[2] = False
                if pygame.key.get_pressed()[pygame.K_LEFT]: self.movement[1] = True
            else:
                self.movement[1] = False
                if pygame.key.get_pressed()[pygame.K_RIGHT]: self.movement[2] = True


    def jump(self):
        if self.movement[0] == 0:
            self.bounce()
        elif self.jumps < self.perks['rocketboots']:
            self.jumps += 1
            self.bounce()
    

    def crouch(self,down:bool=True):
        if down:
            if self.movement[0] == 0:
                #crouching
                self.aimg.change_anim("crouch")
                self.movement[4] = True
                audio.play_sound("boo.wav")
            else:
                self.movement[0] = 25
        else:
            if self.movement[0] == 0:
                self.movement[4] = False
                self.aimg.change_anim('idle')
                audio.play_sound("womp.wav")
            
    def focus(self,down:bool=True):
        if down:
            self.movement[5] = True
        else:
            self.movement[5] = False


    def image_transformations(self):
         #07/09/2023 - rotating the image based on movement
        try:
            if self.momentum != 0 and not self.movement[4]:
                self.image = pygame.transform.rotate(self.image,self.momentum*-2)
        except:...
        #making the image transparent if invincible
        if self.invincibility_counter > 0 and self.invincibility_counter % 2 == 0: 
            self.image = anim.NONE
        #TEMPORARY -- shrinking the image if focusing
        if self.movement[5]:
            self.image = pygame.transform.scale(self.image,(50,50))
            self.mask = pygame.mask.from_surface(self.image)
            rect = self.image.get_rect()
            rect.center = self.rect.center[:]
            self.rect = rect
        else:
            rect = self.image.get_rect()
            rect.center = self.rect.center[:]
            self.rect = rect
        
    def add_child(self):
        ...


class PlayerDummy(Player):
    def __init__(self,bar,sprite_groups, demo=False):
        Player.__init__(self,bar=bar,sprite_groups=sprite_groups,demo=demo)
        self.check = {
            "move":False,
            "jump":False,
            "crouch":False,
            "fastfall":False,
            "shoot":False,
            "focus":False,
        }

    def reset(self):
        for k in self.check.keys():
            self.check[k] = False

    def move(self,dir:bool=True,release:bool=False):
        Player.move(self,dir,release)
        self.check['move'] = True
    
    def jump(self):
        Player.jump(self)
        self.check['jump'] = True
    
    def crouch(self,down:bool=True):
        Player.crouch(self,down)
        self.check['crouch' if self.movement[0] == 0 else 'fastfall'] = True

    def shoot(self):
        Player.shoot(self)
        self.check['shoot'] = True

    def focus(self,down:bool=True):
        Player.focus(self,down=down)
        self.check['focus'] = True


