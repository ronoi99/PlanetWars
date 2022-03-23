from typing import Iterable
import math
import numpy as np

import pandas as pd

from baseline_bot import AttackWeakestPlanetFromStrongestBot, AttackEnemyWeakestPlanetFromStrongestBot, \
    AttackWeakestPlanetFromStrongestSmarterNumOfShipsBot, get_random_map
from planet_wars.battles.tournament import run_and_view_battle, TestBot
from planet_wars.planet_wars import Player, PlanetWars, Order, Planet
from ronen_yuval import RonenYuvalBot


class TheKinders(Player):
    """
    Implement here your smart logic.
    Rename the class and the module to your team name
    """
    def __init__(self):
        self.first_planet = None

    def play_turn(self, game: PlanetWars) -> Iterable[Order]:
        """
        See player.play_turn documentation.
        :param game: PlanetWars object representing the map - use it to fetch all the planets and flees in the map.
        :return: List of orders to execute, each order sends ship from a planet I own to other planet.
        """
        if game.turns == 0:
            self.first_planet = game.get_planets_by_owner(owner=PlanetWars.ME)[0]


        my_orders = []
        my_planets = game.get_planets_by_owner(owner=PlanetWars.ME)
        my_planets_static = my_planets.copy()
        enemy_plants = game.get_planets_by_owner(owner=PlanetWars.ENEMY)
        neutral_plants = game.get_planets_by_owner(owner=PlanetWars.NEUTRAL)
        enemy_plants.extend(neutral_plants)
        plants_to_attack = []
        plants_to_attack_from = []
        plant_to_attack = 0
        source_plant = 0
        # def get_start(game: PlanetWars):
        #     df = game.get_planets_data_frame()
        #     df = df.loc[df["owner"]!=1]
        #     df["Distance"] = np.sqrt(df[4].diff() ** 2 + df[5].diff() ** 2)
        #     print(df["Distance"])
        def get_the_closet_plant(game: PlanetWars, my_planets):
            closet_planet = my_planets[0]
            if len(my_planets) != 0:
                my_planet = my_planets[0]
            else:
                return
            min_dist = 1000000
            for i in my_planets:
                for j in enemy_plants:
                    this_dist = Planet.distance_between_planets(i, j)
                    if this_dist < min_dist:
                        min_dist = this_dist
                        closet_planet = j
                        my_planet = i

            my_planets.remove(my_planet)
            return [closet_planet, my_planet]

        my_orders = []
        for i in my_planets_static:
            plants = get_the_closet_plant(game, my_planets)
            plants_to_attack.append(plants[0])
            plants_to_attack_from.append(plants[1])
            if plants[1].num_ships > plants[0].num_ships:
                order = Order(plants[1], plants[0], plants[1].num_ships - 1)
            else:
                if len(my_planets)==0 and len(plants_to_attack)==1:
                    my_planets.append(my_planets_static[0])
                    enemy_plants.remove(plants_to_attack[0])
                    plants = get_the_closet_plant(game, my_planets)
                    if plants[1].num_ships > plants[0].num_ships:
                        order = Order(plants[1], plants[0], plants[1].num_ships - 1)
                    else:
                        continue
                else:
                    my_strongest_planet = max(my_planets_static, key=lambda planet: planet.num_ships)
                    my_planets_static.remove(my_strongest_planet)
                    my_second_strongest_planet = max(my_planets_static, key=lambda planet: planet.num_ships)
                    if len(game.get_fleets_by_owner(owner=1)) == 0:
                        order = Order(my_strongest_planet, my_second_strongest_planet, plants[1].num_ships - 1)
                    else:
                        pass
            try:
                my_orders.append(order)
            except:
                pass
        # my_strongest_planet = max(my_planets, key=lambda planet: planet.num_ships)

        return my_orders






def view_bots_battle():
    """
    Runs a battle and show the results in the Java viewer

    Note: The viewer can only open one battle at a time - so before viewing new battle close the window of the
    previous one.
    Requirements: Java should be installed on your device.
    """
    map_str = get_random_map()
    run_and_view_battle(RonenYuvalBot(), TheKinders(), map_str)


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