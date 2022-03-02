from typing import Iterable, List

import pandas as pd

from baseline_bot import AttackWeakestPlanetFromStrongestBot, AttackEnemyWeakestPlanetFromStrongestBot, \
    AttackWeakestPlanetFromStrongestSmarterNumOfShipsBot, get_random_map
from planet_wars.battles.tournament import run_and_view_battle, TestBot
from planet_wars.planet_wars import Player, PlanetWars, Order, Planet


class LOL(Player):

    def get_planets_to_attack(self, game: PlanetWars) -> List[Planet]:
        return [p for p in game.planets if p.owner != PlanetWars.ME]

    def ships_to_send_in_a_flee(self, source_planet: Planet, dest_planet: Planet) -> int:
        if dest_planet.owner == PlanetWars.ENEMY:
            return (dest_planet.num_ships +(int(dest_planet.distance_between_planets(source_planet,dest_planet)) * dest_planet.growth_rate) * 1.5)
        elif dest_planet.owner == PlanetWars.NEUTRAL:
            if dest_planet.num_ships < 25:
                return 50
        return (dest_planet.num_ships + 1)


    def play_turn(self, game: PlanetWars) -> Iterable[Order]:
      
        if len(game.get_fleets_by_owner(owner=PlanetWars.ME)) >=3:
            return []

        my_planets = game.get_planets_by_owner(owner=PlanetWars.ME)
        if len(my_planets) == 0:
            return []
        my_strongest_planet = max(my_planets, key=lambda planet: planet.num_ships)

        planets_to_attack = self.get_planets_to_attack(game)
        if len(planets_to_attack) == 0:
            return []
        enemy_or_neutral_nearst = min(planets_to_attack , key=lambda planet: planet.distance_between_planets(my_strongest_planet,planet))


        return [Order(
            my_strongest_planet,
            enemy_or_neutral_nearst,
            self.ships_to_send_in_a_flee(my_strongest_planet, enemy_or_neutral_nearst)
        )]

def view_bots_battle():
    """
    Runs a battle and show the results in the Java viewer

    Note: The viewer can only open one battle at a time - so before viewing new battle close the window of the
    previous one.
    Requirements: Java should be installed on your device.
    """
    map_str = get_random_map()
    run_and_view_battle(AttackWeakestPlanetFromStrongestBot(), LOL(), map_str)


def check_bot():
    """
    Test AttackWeakestPlanetFromStrongestBot against the 2 other bots.
    Print the battle results data frame and the PlayerScore object of the tested bot.
    So is AttackWeakestPlanetFromStrongestBot worse than the 2 other bots? The answer might surprise you.
    """
    maps = [get_random_map(), get_random_map()]
    player_bot_to_test = AttackWeakestPlanetFromStrongestBot()
    tester = TestBot(
        player=player_bot_to_test,
        competitors=[
            AttackEnemyWeakestPlanetFromStrongestBot(), AttackWeakestPlanetFromStrongestSmarterNumOfShipsBot()
        ],
        maps=maps
    )
    tester.run_tournament()

    # for a nicer df printing
    pd.set_option('display.max_columns', 30)
    pd.set_option('expand_frame_repr', False)

    print(tester.get_testing_results_data_frame())
    print("\n\n")
    print(tester.get_score_object())

    # To view battle number 4 uncomment the line below
    # tester.view_battle(4)


if __name__ == "__main__":
    # check_bot()
    view_bots_battle()
