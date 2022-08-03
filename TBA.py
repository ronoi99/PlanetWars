from typing import Iterable, List
from numpy import source

import pandas as pd

from baseline_bot import AttackWeakestPlanetFromStrongestBot, AttackEnemyWeakestPlanetFromStrongestBot, \
    AttackWeakestPlanetFromStrongestSmarterNumOfShipsBot, get_random_map
from planet_wars.battles.tournament import run_and_view_battle, TestBot
from planet_wars.planet_wars import Player, PlanetWars, Order, Planet


class tba(Player):
    """
    Implement here your smart logic.
    Rename the class and the module to your team name
    """

    def get_planets_to_attack(self, game: PlanetWars) -> List[Planet]:
        """
        :param game: PlanetWars object representing the map
        :return: The planets we need to attack
        """
        to_attack = [p for p in game.planets if p.owner != PlanetWars.ME]
        enemy_or_neutral_weakest_planet = min(
            to_attack, key=lambda planet: planet.num_ships)
        return enemy_or_neutral_weakest_planet

    def ships_to_send_in_a_flee(self, source_planet: Planet, dest_planet: Planet) -> int:
        return source_planet.num_ships // 2

    def source(self, game):
        my_planets = game.get_planets_by_owner(owner=PlanetWars.ME)
        my_strongest_planet = max(
            my_planets, key=lambda planet: planet.num_ships)
        return my_strongest_planet

    def append_order(self, game, orders):
        orders.append(Order(self.source(game), self.get_planets_to_attack(
            game), self.ships_to_send_in_a_flee(self.source(game), self.get_planets_to_attack(game))))
        return orders

    def play_turn(self, game: PlanetWars) -> Iterable[Order]:
        """
        See player.play_turn documentation.
        :param game: PlanetWars object representing the map - use it to fetch all the planets and flees in the map.
        :return: List of orders to execute, each order sends ship from a planet I own to other planet.
        """
        orders = []
        self.append_order(game, orders)
        return orders
        # # (4) Send half the ships from my strongest planet to the weakest planet that I do not own.
        # return [Order(
        #     my_strongest_planet,
        #     enemy_or_neutral_weakest_planet,
        #     self.ships_to_send_in_a_flee(
        #         my_strongest_planet, enemy_or_neutral_weakest_planet)
        # )]


def view_bots_battle():
    """
    Runs a battle and show the results in the Java viewer

    Note: The viewer can only open one battle at a time - so before viewing new battle close the window of the
    previous one.
    Requirements: Java should be installed on your device.
    """
    map_str = get_random_map()
    run_and_view_battle(tba(
    ), AttackWeakestPlanetFromStrongestSmarterNumOfShipsBot(), map_str)


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
            tba(
            ), AttackWeakestPlanetFromStrongestSmarterNumOfShipsBot()
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