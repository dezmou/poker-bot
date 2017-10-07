from situation2 import *
from random import randint
class Bot:

    def fstr(self, amount):
        return "%.2f" % round(amount, 2)

    def __init__(self, game):
        self.game = game
        with open("/projects/poker/"+self.game.rendu_to_string(), "r") as f:
            self.knows = f.read().split("\n")
        self.act_sit = Situation(game).string
        addLog(self.act_sit)

    def play(self):
        actions = []
        for know in self.knows:
            try:
                if self.knows == "":
                    continue
                sp = know.split("  THEN ")
                sit = sp[0]
                action = sp[1]
                if sit == self.act_sit:
                    # addLog("~~> "+ know + "\n")
                    actions.append(action)
            except:
                pass
        if len(actions) == 0:
            return str(ACTION_CALL)+"_0"
        final = actions[randint(0,len(actions) - 1)]
        if final == "check" or final == "call":
            return str(ACTION_CALL) + "_0"
        if "raise" in final:
            return str(ACTION_RAISE)+"_"+self.fstr(  float(final.split(" ")[1]) * self.game.pot)
        if "fold" in final:
            return str(ACTION_FOLD) + "_0"
        return str(ACTION_CALL) + "_0"
