from dis import dis
from typing import Iterable, List, Tuple
import pandas as pd
# from shmerlingBot import shmerlingBot
# from awasomeBot import awasomeBot
from baseline_bot import AttackWeakestPlanetFromStrongestBot, AttackEnemyWeakestPlanetFromStrongestBot, \
    AttackWeakestPlanetFromStrongestSmarterNumOfShipsBot, get_random_map
from planet_wars.battles.tournament import run_and_view_battle, TestBot
from planet_wars.planet_wars import Player, PlanetWars, Order, Planet


class HorneyMonkey(Player):
    """
    Implement here your smart logic.
    Rename the class and the module to your team name
    """
    MIN_SHIPS_ON_PLANET = 15

    def attack(self, game: PlanetWars, orders: List[Order]):

        def evaluate_enemy_planets(planet_mine: Planet, enemy_planet: Planet):
            distance = planet_mine.distance_between_planets(
                planet_mine, enemy_planet)
            score = 0
            if enemy_planet.num_ships > 0:
                score = enemy_planet.growth_rate ** 2 / \
                    ((distance)*enemy_planet.num_ships)
            return {"score": score, "planet_mine": planet_mine, "enemy_planet": enemy_planet}

        potenial_planets = []
        newOrders: List[Order] = []
        planets_mine_arr = game.get_planets_by_owner(game.ME)
        no_mine_planets = game.get_planets_by_owner(
            game.NEUTRAL)+game.get_planets_by_owner(game.ENEMY)

        for planet_mine in planets_mine_arr:
            for planet in no_mine_planets:

                potenial_planets.append(evaluate_enemy_planets(
                    planet_mine, planet))

        for pp in (sorted(potenial_planets,
                          key=lambda pp: pp.get("score"), reverse=True)):

            order = Order(pp.get("planet_mine"),
                          pp.get("enemy_planet"), 48)

            newOrders.append(order)

        return newOrders

    def play_turn(self, game: PlanetWars) -> Iterable[Order]:
        """
        See player.play_turn documentation.
        :param game: PlanetWars object representing the map - use it to fetch all the planets and flees in the map.
        :return: List of orders to execute, each order sends ship from a planet I own to other planet.
        """
        # TODO IMPLEMENT HERE YOUR SMART LOGIC
        # First turn spread

        orders = []

        return self.attack(game, orders)


def view_bots_battle():
    """
    Runs a battle and show the results in the Java viewer


    Note: The viewer can only open one battle at a time - so before viewing new battle close the window of the
    previous one.
    Requirements: Java should be installed on your device.
    """
    map_str = get_random_map()
    run_and_view_battle(HorneyMonkey(
    ), AttackWeakestPlanetFromStrongestSmarterNumOfShipsBot(), map_str)


def check_bot():
    """
    Test AttackWeakestPlanetFromStrongestBot against the 2 other bots.
    Print the battle results data frame and the PlayerScore object of the tested bot.
    So is AttackWeakestPlanetFromStrongestBot worse than the 2 other bots? The answer might surprise you.
    """
    maps = [get_random_map() for x in range(0, 100)]
    player_bot_to_test = HorneyMonkey()
    tester = TestBot(
        player=player_bot_to_test,
        competitors=[

            awasomeBot()
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
    tester.view_battle(4)


if __name__ == "__main__":
    check_bot()
    # view_bots_battle()
