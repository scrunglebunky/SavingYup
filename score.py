#Code by Andrew Church
import json,pygame,text
from anim import all_loaded_images as img

#07/29/2023 - Keeping track of the high scores, and then creating individual scores and a full scoreboard image
#Loading the score
scores = {}
with open("./data/scores.json","r") as raw:
    scores = json.load(raw)

#debug abilility to reload scores
def reload_scores() -> list:
    with open("./data/scores.json","r") as raw:
        scores = json.load(raw)
    return scores

#organizing scores
def organize_scores(scores:list) -> list:
    #saving the individual values
    values = [score[1] for score in scores]
    #saying which number goes to which name
    temp_key = {}
    for score in scores:
        temp_key[score[1]] = score[0]
    #organizing values
    scores = [ ]; values.sort(reverse=False)
    for value in values:
        scores.append([temp_key[value], value])
    #removing all the excess scores after len() > 10
    if len(scores) > 10:
        while len(scores) > 10:
            scores.pop(0)
    #finish
    return scores
scores = organize_scores(scores)

#saving scores
def save_scores(scores:list) -> None:
    with open("./data/scores.json","w") as raw:
        raw.write(json.dumps(scores))

#adding score
def add_score(scores:list,score:int,name:str) -> list:
    scores.append([name,score])
    scores=organize_scores(scores)
    return scores


#full package
def test() -> bool:
    try:
        s:dict = reload_scores()
        s:dict = organize_scores(s)
        save_scores(s)
        return True
    except:
        return False


############ THE GRAPHICS
#  Creating graphics for each character
def generate_graphic(score,name) -> pygame.Surface:
    #generating the number
    num = text.load_text(score,size=20,resize=(100,25),fg="white",bg="black")
    #generating the name graphic
    name = text.load_text(name,size=20,resize=(125,25),fg="black",bg="white")
    #plastering them together
    full = pygame.Surface((250,25), pygame.SRCALPHA, 32).convert_alpha()
    full.blit(name,(0,0)) ; full.blit(num,(150,0))
    #end
    return full

#generating graphics for all players, though this has to be redone eventually
def regenerate_graphics():
    scores_graphics = []
    for score in scores:
        scores_graphics.append(generate_graphic(score[1],score[0]))
    return scores_graphics
scores_graphics = regenerate_graphics()

#generating a full scoreboard image
def generate_scoreboard(scores_graphics:list = scores_graphics, do_regenerate_graphics:bool=True) -> pygame.Surface:
    full = pygame.Surface((400,600),pygame.SRCALPHA,32).convert_alpha()
    full.blit(img["high_scores.png"],(0,0))
    if do_regenerate_graphics: scores_graphics = regenerate_graphics()
    for i in range(len(scores_graphics)):
        full.blit(scores_graphics[(len(scores_graphics)-1)-i],(75,150+40*i))
    return full
scoreboard = generate_scoreboard()




score=0
def change(num:int):
    if type(num) == int:
        score += num
def reset():
    score = 0
