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

# WEEK 1 END, STARTING WEEK TWO.
- Okay so I did get a lot done
    1. Enemies are gradually unlocked as time goes on
    2. The backgrounds and such change as time goes on as well
    3. There is now a shop, and a buttload of upgrades you can use your points to purchase
    4. A lot of the previous code is now unused, and needs to be replaced.
- So now I am going to be extending this period by another week, because college keeps getting in the way of what I want to do.
    1. [ ] Difficulty scaling properly
        - [ ] Enemy attack speed goes up GREATLY during the first 10 or so levels, and then slows down to be more gradual afterwards
        - [ ] For each difficulty level an enemy class passes, they gain 1 health. Newly introduced enemies always have 1 health.
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
        5. [ ] Add a graphic that plays at the start of each level, just a little thing that says "LEVEL x" or "BOSS LEVEL"
- However, I will not be doing this right now. The game will stay in this unfinished, technically-playable state for another week or so now


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
