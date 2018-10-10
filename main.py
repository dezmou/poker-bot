# -*- coding: utf-8 -*
# POKER HEADS_UP ENGINE BY MODEZ MARTIN
# run a heads up poker game with server.py
# transform a poker game into situation
# import all situations encounted from Winamax hands history
# incredibledez@gmail.com


from os import listdir
from os.path import isfile, join
import deuces
import json
import traceback
from const import *


class Situation:
    AMOUNT_IS_3BET                  = 14
    NBR_TEST_EVA_FLOP_STRENGHT      = 100
    FLOP_SMALL_POT                  = 12
    FLOP_MID_POT                    = 20
    FLOP_HIGH_POT                   = 30
    TURN_SMALL_POT                  = 18
    TURN_MID_POT                    = 27
    TURN_HIGH_POT                   = 38
    RIVER_SMALL_POT                 = 20
    RIVER_MID_POT                   = 35
    RIVER_HIGH_POT                  = 45

    def to_bb(self, amount):
        return amount / self.game.bb

    def fstr(self, amount):
        return "%.2f" % round(amount, 2)

    def bbs(self, amount):
        return self.fstr(self.to_bb(amount))


    def set_pocket_strenght(self):
        self.hero.cards.sort()
        self.hero.cards.reverse()
        self.pocket_strength = deuces.Card.int_to_str(self.hero.cards[0])[0]+deuces.Card.int_to_str(self.hero.cards[1])[0]
        # self.pocket_strength += "s" if deuces.Card.int_to_str(self.hero.cards[0])[1] == deuces.Card.int_to_str(self.hero.cards[1])[1] else ""

    def sit_preflop(self):
        #rendu_pocket_position_topic_pot_amountCall_
        self.set_pocket_strenght()
        if self.game.to_call == self.game.bb:
            self.preflop_topic = "unopened"
        if self.game.to_call > self.game.bb and self.hero.invest_round <= self.game.bb:
            self.preflop_topic = "opened"
        if self.to_bb(self.game.to_call) >= self.to_bb(self.AMOUNT_IS_3BET):
            self.preflop_topic = "vs-3bet+"
        self.string += self.game.rendu_string[self.game.rendu] + "_"
        self.string += self.pocket_strength + "_"
        self.string += "BTN_" if self.game.button is self.hero else "UTG_"
        self.string += self.preflop_topic

    # TODO merge flop turn river into one function
    def set_flop_strenght(self):
        eva = deuces.Evaluator()
        hero_strenght = eva.evaluate(self.hero.cards, self.game.board[:3])
        nbr_better = 0
        for i in range(self.NBR_TEST_EVA_FLOP_STRENGHT):
            board = json.loads(json.dumps(self.game.board[:3]))
            deck = deuces.Deck()
            for remove in self.hero.cards:
                deck.cards.remove(remove)
            for remove in self.game.board:
                deck.cards.remove(remove)
            # deuces.Card.print_pretty_card(board)
            res = eva.evaluate(deck.draw(2), board)
            if res < hero_strenght:
                nbr_better += 1
        return int((float(self.NBR_TEST_EVA_FLOP_STRENGHT - nbr_better) / self.NBR_TEST_EVA_FLOP_STRENGHT) * 10)

    def set_turn_strenght(self):
        eva = deuces.Evaluator()
        hero_strenght = eva.evaluate(self.hero.cards, self.game.board[:4])
        nbr_better = 0
        for i in range(self.NBR_TEST_EVA_FLOP_STRENGHT):
            board = json.loads(json.dumps(self.game.board[:4]))
            deck = deuces.Deck()
            for remove in self.hero.cards:
                deck.cards.remove(remove)
            for remove in self.game.board:
                deck.cards.remove(remove)
            # deuces.Card.print_pretty_card(board)
            res = eva.evaluate(deck.draw(2), board)
            if res < hero_strenght:
                nbr_better += 1
        return int((float(self.NBR_TEST_EVA_FLOP_STRENGHT - nbr_better) / self.NBR_TEST_EVA_FLOP_STRENGHT) * 10)

    def set_river_strenght(self):
        eva = deuces.Evaluator()
        hero_strenght = eva.evaluate(self.hero.cards, self.game.board)
        nbr_better = 0
        for i in range(self.NBR_TEST_EVA_FLOP_STRENGHT):
            board = json.loads(json.dumps(self.game.board))
            deck = deuces.Deck()
            for remove in self.hero.cards:
                deck.cards.remove(remove)
            for remove in self.game.board:
                deck.cards.remove(remove)
            # deuces.Card.print_pretty_card(board)
            res = eva.evaluate(deck.draw(2), board)
            if res < hero_strenght:
                nbr_better += 1
        return int((float(self.NBR_TEST_EVA_FLOP_STRENGHT - nbr_better) / self.NBR_TEST_EVA_FLOP_STRENGHT) * 10)

    def get_last_raiser(self, rendu = None):
        last = None
        for action in self.game.actions:
            if action.type == ACTION_RAISE:
                if rendu is not None:
                    if rendu == action.rendu:
                        last = action.player
                else:
                    last = action.player
        return last

    def sit_flop(self):
        string = ""
        self.flop_strenght = self.set_flop_strenght()
        string += str(self.flop_strenght) + "_"
        last_raiser = self.get_last_raiser()
        flop_last_raiser = self.get_last_raiser(RENDU_FLOP)
        if flop_last_raiser is not None:
            string += "vs-bet_" if flop_last_raiser is self.op else "vs-raise_"
        elif last_raiser is not None:
            string += "uno-victime_" if last_raiser is self.op else "uno-raiser_"
        else:
            string += "unopened_"
        if self.game.pot > self.FLOP_HIGH_POT:
            string += "HP"
        elif self.game.pot > self.FLOP_MID_POT:
            string += "MP"
        else:
            string += "LP"
        self.string = string

    def sit_turn(self):
        string = ""
        self.turn_strenght = self.set_turn_strenght()
        string += str(self.turn_strenght) + "_"
        last_raiser = self.get_last_raiser()
        flop_last_raiser = self.get_last_raiser(RENDU_TURN)
        if flop_last_raiser is not None:
            string += "vs-bet_" if flop_last_raiser is self.op else "vs-raise_"
        elif last_raiser is not None:
            string += "uno-victime_" if last_raiser is self.op else "uno-raiser_"
        else:
            string += "unopened_"
        if self.game.pot > self.TURN_HIGH_POT:
            string += "HP"
        elif self.game.pot > self.TURN_MID_POT:
            string += "MP"
        else:
            string += "LP"
        self.string = string

    def sit_river(self):
        string = ""
        self.river_strenght = self.set_river_strenght()
        string += str(self.river_strenght) + "_"
        last_raiser = self.get_last_raiser()
        flop_last_raiser = self.get_last_raiser(RENDU_RIVER)
        if flop_last_raiser is not None:
            string += "vs-bet_" if flop_last_raiser is self.op else "vs-raise_"
        elif last_raiser is not None:
            string += "uno-victime_" if last_raiser is self.op else "uno-raiser_"
        else:
            string += "unopened_"
        if self.game.pot > self.RIVER_HIGH_POT:
            string += "HP"
        elif self.game.pot > self.RIVER_MID_POT:
            string += "MP"
        else:
            string += "LP"
        self.string = string

    def __init__(self, game):
        self.string = ""
        try:
            self.game = game
            self.hero = self.game.speak
            self.op = game.get_vs(self.game.speak)
            self.pocket_strength = 0
            self.preflop_topic = ""
            if self.game.rendu == RENDU_PREFLOP:
                self.sit_preflop()
                # self.to_string()
            if self.game.rendu == RENDU_FLOP:
                self.sit_flop()
            if self.game.rendu == RENDU_TURN:
                self.sit_turn()
            if self.game.rendu == RENDU_RIVER:
                self.sit_river()
        except:
            # traceback.print_exc()
            pass


class Action:
    strings = [
        "fold",
        "call",
        "raise",
        "sb",
        "bb"
    ]

    def to_string(self):
        if self.type == ACTION_CALL and self.chips == 0:
            return "check"
        return self.strings[self.type]


    def __init__(self, player ,type, chips):
        self.type = type
        self.chips = chips
        self.player = player
        self.rendu = ""

class Player:
    def __init__(self):
        self.base_chips = 0
        self.chips = 0
        self.cards = []
        self.invest_round = 0
        self.has_play = False
        self.is_allin = False


class Game:
    rendu_string = [
        "preflop",
        "flop",
        "turn",
        "river",
        "end"
    ]

    def to_bb(self, amount):
        return amount / self.bb

    def __init__(self):
        self.board = []
        self.hero = Player()
        self.op = Player()
        self.players = [self.hero, self.op]
        self.button = self.hero
        self.rendu = RENDU_PREFLOP
        self.actions = []
        self.speak = self.hero
        self.sb = 1
        self.bb = 2
        self.to_call = self.bb
        self.pot = 0
        self.winner = None
        self.ended = False
        self.presumed_pot = 0

    def rendu_to_string(self):
        return self.rendu_string[self.rendu]

    def get_player_by_string(self, string):
        if string == "hero":
            return self.hero
        return self.op

    def player_to_string(self, player):
        if player is self.hero:
            return "hero"
        return "op"

    def get_vs(self, player):
        if player is self.hero:
            return self.op
        return self.hero

    def start_game(self):
        self.summary = "CASH - GAME " + str(self.sb) + "/" + str(self.bb) + "\n"
        self.summary += "hero       : "+self.player_to_string(self.hero) + " "+ str(self.hero.chips) + "\n"
        self.summary += "op         : "+self.player_to_string(self.op) + " "+ str(self.op.chips) +"\n"
        self.summary += "button     : "+self.player_to_string(self.button) + "\n\n"
        self.speak = self.button
        self.play(Action(self.speak,ACTION_SB,self.sb))
        self.play(Action(self.speak,ACTION_BB,self.bb))

    def showdown(self):
        eva = deuces.Evaluator()
        self.winner = self.hero if eva.evaluate(self.hero.cards, self.board) < eva.evaluate(self.op.cards, self.board) else self.op
        self.rendu = RENDU_END


    def end_game(self):
        if self.winner is None:
            self.showdown()
        self.ended = True
        self.summary += "pot : "+str(self.pot) + " | presumed : "+str(self.presumed_pot) + "\n"
        self.speak = None

    def next_round(self):
        self.rendu += 1
        self.summary += "###############"+ self.rendu_string[self.rendu] + "\n"
        for player in self.players:
            player.has_play = False
            player.invest_round = 0
        self.to_call = 0
        self.speak = self.get_vs(self.button)
        if self.rendu == RENDU_END:
            self.end_game()

    def filter_action(self, action):
        if action.type == ACTION_RAISE:
            if action.chips <= self.to_call:
                action.type = ACTION_CALL
            elif action.chips < (self.to_call - self.to_call) * 2:
                action.chips = (self.to_call - self.to_call) * 2
        if self.get_vs(action.player).is_allin:
            if action.type != ACTION_FOLD:
                action.type = ACTION_CALL
        if action.type == ACTION_CALL:
            action.chips = self.to_call
        if action.chips >= action.player.chips + action.player.invest_round:
            action.player.is_allin = True
            action.chips = action.player.chips + action.player.invest_round


    def play(self, action):
        if self.ended:
            return
        self.filter_action(action)
        action.rendu = self.rendu
        self.actions.append(action)
        if action.type == ACTION_FOLD:
            self.winner = self.get_vs(action.player)
            self.end_game()
            return
        net = action.chips - action.player.invest_round
        self.pot += net
        action.player.chips += -net
        self.summary += self.player_to_string(action.player) + " " + action.to_string() + " " +str(action.chips) + "(need: "+str(self.to_call) +" posed: "+str(action.player.invest_round) +")\n"
        if self.get_vs(action.player).is_allin:
            action.player.invest_round = action.chips
            self.end_game()
            return
        if self.to_call == action.chips and self.get_vs(action.player).has_play:
            self.next_round()
            return
        action.player.has_play = True if action.type < ACTION_SB else False
        action.player.invest_round = action.chips
        self.to_call = action.chips
        self.speak = self.get_vs(action.player)


class BrowserGame(Game):

    def get_card_png(self, raw_card):
        card = deuces.Card.int_to_str(raw_card)
        final = card[0].replace("T", "10").replace("A", "ace").replace("J", "jack").replace("Q", "queen").replace("K","king")
        final += "_of_"
        if card[1] == "s":
            final += "spades"
        elif card[1] == "d":
            final += "diamonds"
        elif card[1] == "h":
            final += "hearts"
        elif card[1] == "c":
            final += "clubs"
        final += ".png"
        return final

    def load(self):
        pass

    def get_dict(self):
        game = {}
        game["hero_chips"] = self.hero.chips
        game["op_chips"] = self.op.chips
        game["hero_posed"] = self.hero.invest_round
        game["op_posed"] = self.op.invest_round
        game["summary"] = self.summary.replace("\n", "<br/>")
        game["pot"] = self.pot
        game["board"] = []
        game["to_call"] = self.to_call
        game["min_raise"] = self.to_call  * 2 if self.to_call > 0 else self.bb
        game["bb"] = self.bb
        game["sb"] = self.sb
        game["rendu"] = self.rendu
        if self.rendu != RENDU_PREFLOP:
            for i,card in enumerate(self.board):
                if i >= self.rendu + 2:
                    break
                game["board"].append(self.get_card_png(card))
        game["hero_cards"] = []
        for card in self.hero.cards:
            game["hero_cards"].append(self.get_card_png(card))
        game["ended"] = self.ended
        game["winner"] = self.player_to_string(self.winner)
        game["op_cards"] = []
        if self.ended:
            for card in self.op.cards:
                game["op_cards"].append(self.get_card_png(card))
        game["actions"] = []
        preflop_played = False
        for action in self.actions:
            string = action.to_string()
            if preflop_played:
                if action.type == ACTION_CALL and action.chips == self.bb:
                    string = "check"
            if action.rendu == RENDU_PREFLOP and action.type < ACTION_SB:
                preflop_played = True
            game["actions"].append({
                "type" : action.type,
                "chips" : action.chips,
                "rendu" : action.rendu,
                "player" : self.player_to_string(action.player),
                "string" : string,
            })
        return game


    def new_hand(self):
        deck = deuces.Deck()
        for player in self.players:
            player.cards = deck.draw(2)
        self.board = deck.draw(5)
        self.start_game()


class WinamaxGame(Game):
    HERO_NAME           = "bricolage"

    def get_player_by_line(self, line):
        if self.HERO_NAME in line:
            return self.hero
        return self.op

    def load_init(self):
        started = False
        button_nbr = "1"
        for line in self.lines:
            if line == "":
                continue
            line = line.replace(" and is all-in", "").replace("€", "").replace(" out of position", "").replace("â‚¬",
                                                                                                               "")
            if line == "\n":
                continue
            if "Board:" in line:
                cards = line.split("[")[1].split("]")[0].split(" ")
                self.board = []
                for card in cards:
                    self.board.append(deuces.Card.new(card))
            if " posts small blind " in line:
                self.sb = float(line.split(" posts small blind ")[1])
                continue
            if " posts big blind " in line:
                self.bb = float(line.split(" posts big blind ")[1])
                continue
            if "*** ANTE/BLINDS ***" in line:
                started = True
                continue
            if "Total pot" in line:
                rake = 0
                if not "No rake" in line:
                    rake = float(line.split("Rake ")[1])
                self.presumed_pot = float(line.split("Total pot ")[1].split(" |")[0].replace("k",""))
                if "k" in line.split("Total pot ")[1].split(" |")[0]:
                    self.presumed_pot = self.presumed_pot * 1000
                self.presumed_pot += rake
            if not started:
                if "Seat " in line and " is the button" in line:
                    button_nbr = line.split("#")[1].split(" ")[0]
                elif "Seat " in line:
                    self.get_player_by_line(line).chips = float(line.split("(")[1].split(")")[0])
                    self.get_player_by_line(line).base_chips = self.get_player_by_line(line).chips
                    if button_nbr in line.split(":")[0]:
                        self.button = self.get_player_by_line(line)
            else:
                if "Dealt to " in line:
                    cards = line.split("[")[1].split("]")[0].split(" ")
                    for card in cards:
                        self.hero.cards.append(deuces.Card.new(card))

    def load_actions(self):
        started = False
        for line in self.lines:
            if line == "\n":
                continue
            line = line.replace(" and is all-in", "").replace("€", "").replace(" out of position", "").replace("â‚¬",
                                                                                                               "")
            if "*** ANTE/BLINDS *** " in line:
                started = True
                continue
            if started:
                # if "***" in line:
                #     self.summary += "~~~~>" + line + "\n"
                if " checks" in line:
                    self.summary += "\n~~~~>"+line + "\n"
                    if self.speak is self.hero:
                        sit = Situation(self)
                        if len(sit.string) > 1:
                            print sit.string + "  THEN check"
                    self.play(Action(self.speak,ACTION_CALL,0))

                    continue
                if " calls " in line:
                    self.summary += "\n~~~~>"+line + "\n"
                    if self.speak is self.hero:
                        sit = Situation(self)
                        if len(sit.string) > 1:
                            print sit.string + "  THEN call"
                    self.play(Action(self.speak, ACTION_CALL, 0))
                    continue
                if " folds" in line:
                    self.summary += "\n~~~~>"+line + "\n"
                    if self.speak is self.hero:
                        sit = Situation(self)
                        if len(sit.string) > 1:
                            print sit.string + "  THEN fold"
                    self.play(Action(self.speak, ACTION_FOLD, 0))
                    continue
                if " bets " in line:
                    self.summary += "\n~~~~>"+line + "\n"
                    if self.speak is self.hero:
                        sit = Situation(self)
                        if len(sit.string) > 1:
                            print sit.string + "  THEN raise " + str(float(line.split(" bets ")[1]) / self.pot)
                    amount =  float(line.split(" bets ")[1])
                    self.play(Action(self.speak,ACTION_RAISE,amount))
                    continue
                if " raises " in line:
                    self.summary += "\n~~~~>"+line + "\n"
                    if self.speak is self.hero:
                        sit = Situation(self)
                        if len(sit.string) > 1:
                            print sit.string + "  THEN raise " + str(float(line.split(" to ")[1]) / self.pot)
                    amount = float(line.split(" to ")[1])
                    self.play(Action(self.speak,ACTION_RAISE,amount))
                    continue

    def load(self, lines):
        self.lines = lines
        self.load_init()
        self.start_game()
        # if self.hero.chips < 70 * self.bb:
        #     return
        # if self.op.chips < 70 * self.bb:
        #     return
        self.load_actions()


if __name__ == "__main__":
    # b = BrowserGame()
    # b.hero.chips = 200
    # b.op.chips = 200
    # b.sb = 10
    # b.bb = 20
    # b.new_hand()
    # b.start_game()
    # while not b.rendu == RENDU_TURN:
    #     if b.rendu == RENDU_FLOP:
    #         s = Situation(b)
    #     b.play(Action(b.speak,ACTION_CALL,0))
    # print b.summary

    FILES_PATH          = "/projects/poker/bricolageHands/"
    onlyfiles              = [f for f in listdir(FILES_PATH) if isfile(join(FILES_PATH, f))]
    nbrhand = 0
    succes = 0
    failure = 0
    for fi_name in onlyfiles:
        with open(FILES_PATH + fi_name, "r") as f:
            fi = f.read()
            if not " - CashGame - " in fi or not " 2-max " in fi:
                continue
            hands_str = fi.split("Winamax Poker - ")
            for i, hand_str in enumerate(hands_str):
                try:
                    if hand_str == "":
                        continue
                    if not "" in hand_str:
                        continue
                    game = WinamaxGame()
                    game.load(hand_str.split("\n"))
                    if game.pot < 1000:
                        # print str(nbrhand)+" ~~~>"+str(game.pot) + " " + str(game.presumed_pot)
                        pass
                    if str(game.pot) != str(game.presumed_pot) and game.pot < 1000:
                        # print hand_str
                        # print game.summary
                        # raw_input()
                        failure += 1
                    else:
                        succes += 1
                    nbrhand += 1
                except:
                    failure += 1
                    print traceback.format_exc()

    # print "failure : " + str(failure)
    # print "succes  :" + str(succes)
