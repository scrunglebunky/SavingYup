# NOTE - this is going to go from top to bottom, not bottom to top

# 11/19/24 FINISHING THIS 
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
- [ ] Difficulty scaling
    - Enemies get more health
        - (health bars?)
    - Level 1 has no coming down
    - Level 2,3, and 4 have it ramp up
    - Level 5 has a difficulty spike but then slows down 
- [ ] Bosses Every 5 levels.
    - These don't require an entire state, and are instead just a one-man rotation
    - [ ] UFO for "YUP"
    - [ ] Big Nope for "NOPE"
    - [ ] Spinning Checkerball eye for "YIPPLES"
    - [ ] Large freaky flower thing for "TOUCH GRASS"
    - [ ] Spooky ghost for "DRAKE"
    - [ ] Big Jellyfish for "BUBBLES"
    - [ ] A large sentient stick of butter for "YELLOW"
    - [ ] Anglerfish for "PINK!!!!!!!!!!!!!!!!!!!"
    - [ ] Fake yup for "YEP..."
    - [ ] The Sun for "SKY"
I will have **one week to do this** (Tue 19th to Tue 26th)

# PART 1 -- REMOVING THE "SKINS"
- So the enemies pull from the Template class, which sets the skin based off an argument
- Usually the enemies get the skin value when spawned from the Formation, which pulls from the world file.
- In order to fix that, I need to remove the skin info being fed to the enemy, and instead have it provide it to the template itself. 