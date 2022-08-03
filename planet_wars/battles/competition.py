import warnings

import pandas as pd

from FireflyZ import FireflyZ_Bot
from Kvutza6 import Kvutza6
from TBA import tba
from americanPy import americanPy
from awasomeBot import awasomeBot
from girlsPower import GirlsPowerlBot
from planet_wars.battles.tournament import Tournament

# Insert Your bot object here, as BotObject(). Don't forget to set BotObject.NAME to your team name
from rust_react_gulp import Rust_react_gulp
from shmerlingBot import shmerlingBot
from the_killers import the_killers
from undefined import Undefined
from yahmam_bot import YahmamBot

PLAYER_BOTS = [
    americanPy(), awasomeBot(), FireflyZ_Bot(), GirlsPowerlBot(), Kvutza6(), Rust_react_gulp(), shmerlingBot(),
    tba(), the_killers(), Undefined(), YahmamBot()
]


ROUND1_MAP = """P 15 15 0 28 5
P 5.775092167744024 9.945603402585451 1 100 5
P 22.37817840199747 7.502778318212037 2 100 5
P 14.290337764612119 10.51936898641209 0 24 3
P 22.46690378782811 25.34395609840424 0 28 4
P 10.828859132954104 27.056270725628874 0 28 4
P 29.719061395649952 12.827948188216832 0 63 2
P 0.27908809793287226 17.159474522554415 0 63 2
P 10.47859056018009 1.5413863220861614 0 60 3
P 15.453365415599462 0.8094438004086548 0 60 3
P 7.574366009785828 18.33206150202184 0 74 3
P 23.070675767779797 16.052077307640506 0 74 3
P 6.415718558715152 16.065026550738125 0 88 5
P 23.52725636556483 13.547392588171654 0 88 5
P 16.824572305027687 20.46843969316639 0 90 1
P 14.827804297343912 20.762225734389318 0 90 1
P 26.458323098955336 10.225402744498432 0 85 5
P 2.65204212371734 13.728039514039232 0 85 5
P 11.902922340652648 18.59937175982182 0 52 1
P 19.00254557026323 17.554798632259995 0 52 1
P 13.36863369359301 16.594772135863842 0 90 3
P 17.021569641837495 16.057312808117224 0 90 3
P 28.612742363253513 15.11549391205284 0 58 5
P 1.9973978593244741 19.03143039916831 0 58 5
P 4.780026960670561 23.75546342198531 0 34 3
P 27.308681116906314 20.44080488720715 0 34 3
P 4.9777283436208375 21.254835473405894 0 37 5
P 26.399110666795405 18.10309071085411 0 37 5
P 18.571498861103997 7.520667608856594 0 80 3
P 9.425606478373874 8.866309919948126 0 80 3"""

if __name__ == '__main__':
    # Display options
    warnings.simplefilter(action='ignore')
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    pd.set_option('expand_frame_repr', False)

    tournament = Tournament(PLAYER_BOTS, [ROUND1_MAP], all_against_all=False)
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