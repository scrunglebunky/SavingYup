# NOTE - this is going to go from top to bottom, not bottom to top

# 11/19/24 WEEK 1, WHAT WAS COMPLETED.
- OKAY so this game was way too polished for me to drop
- But I'm noticing there was a lot more, or moreso less I could have done.
- For one, the main character assets should not change as that makes the game cluttered and confusing
- There should only be one bullet asset
- There shouldn't be worlds, only randomly generated levels that slowly get more chaotic as time goes on.
## WHAT TO DO
- [x] Remove the "skins" and make the enemies only have one basic skin
    - Enemy A: Nope A
    - Enemy B: Nope B
    - Enemy C: Nope C
    - Surf-Guy: clone of Enemy A
    - Yippee: Special
    - Sandwich: Special
    - Computer: Special
    - Laser-Eye: Special
    - Jellyfish: Special
- [x] Remove the tutorial
    - There will be less clutter, so they'll learn the complicated stuff themselves
- [x] Remove the end results
- [x] Remove the demo code from Play State, and remove uses of it from the Title Screen
    - It's extra bloat that isn't needed, and if it is it could be an inhereted class, not integrated
- [ ] Simplify the Game Over, and title screen
- [x] Remove the changing bullets (they can change, but they're not supposed to normally)
- [x] Make a new campaign/world just called "arcade"
    - There is only one enemy
    - New enemies get added every 5 levels
    - Each new enemy class has a randomly-assigned formation pattern that does not change for the entire game
        - [x] this pulls from a random list of **all** the start patterns
- [x] World BG/FG will change every 5 levels
- [ ] Special events that do graphical changes for the funsies
- [x] Sounds.
- [x] A shop that sells upgrades
    - [x] Triple Shot
    - [x] Homing Missile
    - Extra damage

I will have **one week to do this** (Tue 19th to Tue 26th)

# WEEK 2
- Okay so I did get a lot done
    1. Enemies are gradually unlocked as time goes on
    2. The backgrounds and such change as time goes on as well
    3. There is now a shop, and a buttload of upgrades you can use your points to purchase
    4. A lot of the previous code is now unused, and needs to be replaced.
- So now I am going to be extending this period by another week, because college keeps getting in the way of what I want to do.
    1. [x] Difficulty scaling properly
        - [x] Enemy attack speed goes up GREATLY during the first 10 or so levels, and then slows down to be more gradual afterwards
        - [x] For each difficulty level an enemy class passes, they gain 1 health. Newly introduced enemies always have 1 health.
            - [ ] Probably add healthbars to this?
    2. [ ] Bosses
        - This will probably just be one boss with slight changes.
        - For each world ("difficulty level") you've gone through, the boss becomes more powerful
            - extra attack 
            - more health
            - different idle state
        - Note that the formation handles bosses as just another enemy in the formation.
            - It checks if the enemy dies, and then updates for a new formation
    3. OPTIMIZE WHAT WAS ALREADY THERE
        1. [x] Adding the GameOver/highscore state back.
            - The old one was too complicated and convoluted.
            - It just flashes the game over screen, and if you got a high score it prompts you to type your name. 
        2. [x] Optimize the title screen
            - I made emblems.
            - Emblems should be used, not some crappy dictionary thing.
            - Not gonna lie it looks bad but thats intentional
        3. [x] FIX THE UI BORDER
            - THIS ONE IS ALSO LAME
            - IT SHOULD JUST BE PASSED THE PLAYER CLASS AND DRAW IMAGES AND MAKE EMBLEMS
            - Change the images too
            - actually this is just going to become a menu sprite like the other ones
        4. [x] Re-add the advance state back, just as a transition so you know more things are going to be added
        5. [x] Add a graphic that plays at the start of each level, just a little thing that says "LEVEL x" or "BOSS LEVEL"

# WEEK 3
- OKAY so college is getting in the way way too much
- 2 entire days I could have been working on this game were dedicated to studying for finals
- I have a new checklist
    1. CHANGE THE FLOOR ASSET  
        - [ ] There is no longer a floor, just a platform under you that follows you, so you're technically on a ship in space
        - [ ] This stays at the bottom of the player.bar[1] position, and follows your rect.centerx value to seem like it's always catching you
    2. UPDATE THE WAY THAT MENU ASSETS BEHAVE
        - [ ] All of the menu assets behave the same, so I can just iterate through what gets drawn by a list
            - So reference all the menu assets in a dictionary and iterate [for x in x, if x.active then draw and do inputs]
        - [ ] make it so playstate has an "activate queue" so multiple items aren't activated simultaneously
            - playstate.activate_queue = {} 
            - playstate.activate("gameplay")
            - then it repeatedly checks to see if said item de-activates, and then activates the next (after .popping)
        - [ ] give the menu assets a parent class since a lot of them inherit the same values
        - [ ] give menu assets a .visible bool value, so multiple items can be drawn to the screen at the same time
        
        
# DOCUMENTING WHAT I'VE BEEN DOING
## ENEMY/BG UNLOCKING
- World data no longer exists
- The gameplay assets only have lists of unlocked enemies/BGs/start patterns
- This is handled through a class filled with static methods known as Info
## MENU ASSETS
- I got rid of a majority of the "states" and replaced them with "MENU" assets
- These "menu" assets are pygame.sprite.Sprite(s) that handle everything themselves and leave the play state to just hold them
- Doing this, the amount of needed states has been dropped down to just Title and Play.
- advance, gameover, gameplay, lore, options, pause, and shop are all menu assets, handled entirely through playstate
## BOSSES
- There is only one boss: the NOPE
- However, it has a list of attacks it could pull from
- This list of attacks grows per difficulty
