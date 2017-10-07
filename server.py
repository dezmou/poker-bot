#!/projects/venv/bin/python

import sqlite3
import sys
import json
import traceback
import cPickle

from const import *
from poker import *
from bot import *

if len(sys.argv) < 2:
    sys.exit()
try:

    PLAYER_ID           = sys.argv[1]
    PROJECT_PATH        = "/projects/poker"
    PLAYER_JSON_PATH    = PROJECT_PATH + "/players.json"
    def print_log(s):
        with open(PROJECT_PATH + "/server.log", "a") as f:
            f.write(s+"\n")

    def format_sql(s):
        return s.replace("'", "''").replace('"', '""')

    print_log("client play : " + PLAYER_ID)
    db = sqlite3.connect(PROJECT_PATH + '/base.db')
    cursor = db.cursor()
    cursor.execute('SELECT id, act, stats FROM players WHERE id="'+PLAYER_ID+'"')
    res = cursor.fetchone()
    if res is None:
        print_log("new client created")
        hand = BrowserGame()
        hand.hero.chips = 200
        hand.op.chips = 200
        hand.new_hand()
        pi = cPickle.dumps(hand, cPickle.HIGHEST_PROTOCOL)
        query = 'INSERT INTO players (id,act,stats) VALUES (?,?,?)'
        cursor.execute(query,(PLAYER_ID, sqlite3.Binary(pi), "fuckit"))
        db.commit()
        print json.dumps(hand.get_dict())
    else:
        hand = cPickle.loads(str(res[1]))
        if hand.ended:
            st = hand.player_to_string(hand.button)
            hand = BrowserGame()
            if st == "hero":
                hand.button = hand.op
            hand.hero.chips = 200
            hand.op.chips = 200
            hand.new_hand()
        if hand.speak is hand.hero:
            if len(sys.argv) > 2:
                action = sys.argv[2].split("_")
                hand.play(Action(hand.speak,int(action[0]),float(action[1])))
        while hand.speak is hand.op:
            bot = Bot(hand)
            res = bot.play()
            action = res.split("_")
            hand.play(Action(hand.speak, int(action[0]), float(action[1])))

        pi = cPickle.dumps(hand, cPickle.HIGHEST_PROTOCOL)
        query = 'UPDATE players SET act =?, stats =? WHERE id =?'
        cursor.execute(query, (sqlite3.Binary(pi), "damn", PLAYER_ID))
        db.commit()
        print json.dumps(hand.get_dict())

except:
    with open(PROJECT_PATH + "/failure", "a") as f:
        traceback.print_exc()
        f.write(traceback.format_exc())
