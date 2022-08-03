from typing import Iterable, List

import pandas as pd

from baseline_bot import AttackWeakestPlanetFromStrongestBot, AttackEnemyWeakestPlanetFromStrongestBot, \
    AttackWeakestPlanetFromStrongestSmarterNumOfShipsBot, get_random_map
from planet_wars.battles.tournament import run_and_view_battle, TestBot
from planet_wars.planet_wars import Player, PlanetWars, Order, Planet
import math


class FireflyZ_Bot(Player):
    """
    Implement here your smart logic.
    Rename the class and the module to your team name
    """
    # TODO IMPLEMENT HERE YOUR SMART LOGIC

    #  Return distance between planets: int
    def get_planets_trip(self,  origin_planet: Planet, target_planet: Planet):
        return math.ceil(math.sqrt(((origin_planet.x - target_planet.x)**2 + (origin_planet.y - target_planet.y)**2)))

    # Returns number of ships needed to conquer target planet at target time: int
    def calc_ships_needed_to_conquer(self, game: PlanetWars, target_planet: Planet, target_turn: int):
        num_of_turns_to_conquer = target_turn - game.turns
        #  Enemy planet
        if target_planet.owner == 2:
            return num_of_turns_to_conquer * target_planet.growth_rate + target_planet.num_ships + 1
        #  Neutral planet
        elif target_planet.owner == 0:
            return target_planet.num_ships + 1
        # My own planet - Should not get here
        else:
            print("AHAHAHAHAHAHA WHY ARE YOU DOING THIS?>?!")
            return 0

    # Returns number of turns for planet rehabilitation: int
    def get_planet_repayment(self, game, origin_planet, departure_time, target_planet):
        turns_to_target = self.get_planets_trip(origin_planet, target_planet)
        invasion_time = departure_time + turns_to_target
        target_strength = self.calc_ships_needed_to_conquer(
            game, target_planet, invasion_time)
        if target_planet.growth_rate == 0:
            return 200
        turns_to_repay = math.ceil(
            target_strength / target_planet.growth_rate) + turns_to_target
        return turns_to_repay

    #  Adds orders to orders list if the orders are valid and have good repayment.
    def for_my_planet_add_orders_to_list(self, game: PlanetWars, my_planet, possible_planets, orders_list):
        possible_planets.sort(key=lambda planet: self.get_planet_repayment(
            game, my_planet, game.turns, planet))
        my_planet_army = my_planet.num_ships
        for possible_planet in possible_planets:
            target_time = game.turns + \
                self.get_planets_trip(my_planet, possible_planet)
            target_army = self.calc_ships_needed_to_conquer(
                game, possible_planet, target_time)
            if my_planet_army > target_army:
                my_planet_army -= target_army
                orders_list.append(
                    Order(my_planet, possible_planet, target_army))
            else:
                break

    def play_turn(self, game: PlanetWars) -> Iterable[Order]:
        """
        See player.play_turn documentation.
        :param game: PlanetWars object representing the map - use it to fetch all the planets and flees in the map.
        :return: List of orders to execute, each order sends ship from a planet I own to other planet.
        """
        orders_list = []
        my_planets = game.get_planets_by_owner(owner=PlanetWars.ME)
        foreign_planets = game.get_planets_by_owner(owner=PlanetWars.ENEMY)
        foreign_planets.extend(
            game.get_planets_by_owner(owner=PlanetWars.NEUTRAL))
        my_fleets = game.get_fleets_by_owner(1)

        for planet in my_planets:
            for fleet in my_fleets:
                for planet in foreign_planets:
                    if fleet.destination_planet_id == planet.planet_id:
                        foreign_planets.remove(planet)
            self.for_my_planet_add_orders_to_list(
                game, planet, foreign_planets, orders_list)

        return orders_list


def view_bots_battle():
    """
    Runs a battle and show the results in the Java viewer

    Note: The viewer can only open one battle at a time - so before viewing new battle close the window of the
    previous one.
    Requirements: Java should be installed on your device.
    """
    map_str = get_random_map()
    run_and_view_battle(AttackWeakestPlanetFromStrongestBot(
    ), AttackEnemyWeakestPlanetFromStrongestBot(), map_str)


def check_bot():
    """
    Test AttackWeakestPlanetFromStrongestBot against the 2 other bots.
    Print the battle results data frame and the PlayerScore object of the tested bot.
    So is AttackWeakestPlanetFromStrongestBot worse than the 2 other bots? The answer might surprise you.
    """
    maps = [get_random_map() for i in range(100)]
    player_bot_to_test = FireflyZ_Bot()
    tester = TestBot(
        player=player_bot_to_test,
        competitors=[
            AttackEnemyWeakestPlanetFromStrongestBot(
            ), AttackWeakestPlanetFromStrongestSmarterNumOfShipsBot()
        ],
        maps=maps
    )
    tester.run_tournament()

    # for a nicer df printing
    pd.set_option('display.max_columns', 30)
    pd.set_option('expand_frame_repr', False)
    df = tester.get_testing_results_data_frame()
    df.won.sum()
    print(df.won.sum()/400*100)
    print("\n\n")
    print(tester.get_score_object())

    # To view battle number 4 uncomment the line below
    tester.view_battle(4)


if __name__ == "__main__":
    check_bot()
    # view_bots_battle()
