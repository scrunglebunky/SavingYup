# NOTE - this is going to go from top to bottom, not bottom to top

# 11/19/24 FINISHING THIS 
- OKAY so this game was way too polished for me to drop
- But I'm noticing there was a lot more, or moreso less I could have done.
- For one, the main character assets should not change as that makes the game cluttered and confusing
- There should only be one bullet asset
- There shouldn't be worlds, only randomly generated levels that slowly get more chaotic as time goes on.
## WHAT TO DO
- [ ] Make the only available bosses the UFO and the big Nope
- [ ] Remove the "skins" and make the enemies only have one basic skin
    - Enemy A: Nope A
    - Enemy B: Nope B
    - Enemy C: Nope C
    - Surf-Guy: clone of Enemy A
    - Yippee: Special
    - Sandwich: Special
    - Computer: Special
    - Laser-Eye: Special
    - Jellyfish: Special
- [ ] Remove the tutorial/end results
    - There will be less clutter, so they'll learn the complicated stuff themselves
- [ ] Simplify the Game Over.
- [ ] Remove the changing bullets
- [ ] Make a new campaign/world just called "arcade"
    - There is only one enemy
    - New enemies get added every 5 levels
    - Each new enemy class has a randomly-assigned formation pattern that does not change for the entire game
    - World BG/FG will change every 5 levels
I will have **one week to do this** (Tue 19th to Tue 26th)

# PART 1 -- REMOVING THE "SKINS"
- So the enemies pull from the Template class, which sets the skin based off an argument
- Usually the enemies get the skin value when spawned from the Formation, which pulls from the world file.
- In order to fix that, I need to remove the skin info being fed to the enemy, and instead have it provide it to the template itself. 