import warnings

import pandas as pd

from FireflyZ import FireflyZ_Bot
from HorneyMonkey import HorneyMonkey
from Kvutza6 import Kvutza6
from Wookies import Wookies
from americanPy import americanPy
from awasomeBot import awasomeBot
from girlsPower import GirlsPowerlBot
from planet_wars.battles.tournament import Tournament

# Insert Your bot object here, as BotObject(). Don't forget to set BotObject.NAME to your team name
from shmerlingbot import shmerlingBot
from tba import tba
from the_killers import the_killers
from undefined import Undefined
from yahmam_bot import YahmamBot

PLAYER_BOTS = [
    americanPy(), awasomeBot(), FireflyZ_Bot(), GirlsPowerlBot(), HorneyMonkey(), Kvutza6(), shmerlingBot(),
    tba(), the_killers(), Undefined(), Wookies(), YahmamBot()
]


ROUND2_MAP = """P 15 15 0 43 1
P 11.114072097364033 22.64553445227421 1 100 5
P 18.885927902635963 7.35446554772579 2 100 5
P 6.930398156851366 11.06419220434527 0 73 1
P 23.069601843148636 18.935807795654732 0 73 1
P 8.464341714844089 11.812346466598989 0 43 1
P 21.53565828515591 18.18765353340101 0 43 1
P 17.007871967271754 15.321010314082814 0 36 5
P 12.992128032728246 14.678989685917188 0 36 5
P 25.438481257658367 20.22656069592056 0 59 3
P 4.561518742341633 9.77343930407944 0 59 3
P 11.090851907463446 12.780335591321368 0 65 4
P 18.909148092536558 17.21966440867863 0 65 4
P 12.907703910648491 7.052178765948909 0 75 1
P 17.09229608935151 22.94782123405109 0 75 1
P 11.780774009384144 27.339326702495185 0 20 4
P 18.21922599061583 2.6606732975048075 0 20 4"""

if __name__ == '__main__':
    # Display options
    warnings.simplefilter(action='ignore')
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    pd.set_option('expand_frame_repr', False)

    tournament = Tournament(PLAYER_BOTS, [ROUND2_MAP], all_against_all=False)
    battle_results = tournament.run_tournament()
    # player_scores_df = tournament.get_player_scores_data_frame()
    battle_results_df = tournament.get_battle_results_data_frame()
    # print(player_scores_df)
    print(battle_results_df)

    # player_scores_df.to_parquet("./player_scores_df.parquet")
    battle_results_df.to_parquet("./battle_results_df.parquet")
    # player_scores_df.to_csv("./player_scores_df.csv")
    battle_results_df.to_csv("./battle_results_df.csv")
    # TODO commit the saved df so all players can see the battle results
