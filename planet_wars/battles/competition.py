import warnings

import pandas as pd

from Expansion_V2 import Expansion_V2
from Galaxyconqueror import Galaxyconqueror
from Genghis_Khan import Genghis_Khan
from If_it_run_im_potato import LOL
from PLS_team_bot import PLS
from SOYsauce import SOYsauce
from ShrekBotTwoPointOh import ShrekBot
from TeamRocket import teamRocket
from TheTerminator import TheTerminator
from The_average_group import The_average_group
from avengers_endgame import avengers_endgame
from boby import boby
from myl import mylbot
from planet_wars.battles.tournament import Tournament


# Insert Your bot object here, as BotObject(). Don't forget to set BotObject.NAME to your team name
PLAYER_BOTS = [
    avengers_endgame(), boby(), Expansion_V2(), Galaxyconqueror(), Genghis_Khan(), LOL(),
    mylbot(), PLS(), ShrekBot(), SOYsauce(), teamRocket(), The_average_group(), TheTerminator()
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