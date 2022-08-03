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

    # def send_fleets(self, game: PlanetWars):
    #     my_planets = game.get_planet_by_id(owner=PlanetWars.ME)
    #     for i in range(len(my_planets)):
    #         pass

    # def get_planet_repayment(self, game: PlanetWars, origin_planet, origin_time, target_planet):
    #     turns_to_target = calculate_distance(
    #         game, PlanetWars, origin_planet, target_planet)
    #     invasion_time = origin_time + turns_to_target
    #     target_strength = get_enemy_ships_at_time(
    #         game, target_planet, invasion_time)
    #     turns_to_repay = target_strength // target_planet.growth + turns_to_target
    #     return turns_to_repay

    # def get_enemy_ships_at_time(self, game: PlanetWars, target_planet, time):
    #     return ((time - game.turns) * target_planet.growth_rate) + target_planet.num_ships

    def calculate_distance(self, game: PlanetWars,  origin_planet: Planet, target_planet: Planet):
        return math.sqrt(((origin_planet.x - target_planet.x)**2 + (origin_planet.y - target_planet.y)**2))

    def find_closest_planet_to_strongest_self_planet(self, game: PlanetWars):
        # (2) Find my strongest planet and enemy's strongest planet.
        my_planets = game.get_planets_by_owner(owner=PlanetWars.ME)
        if len(my_planets) == 0:
            return []
        my_strongest_planet = max(
            my_planets, key=lambda planet: planet.num_ships)
        unconqured_planets = []
        unconqured_planets.extend(game.get_planets_by_owner(2))
        unconqured_planets.extend(game.get_planets_by_owner(0))
        planets_distances = []

        for planet in unconqured_planets:
            planets_distances.append(self.calculate_distance(
                game, my_strongest_planet, planet))
        return min(planets_distances)
        # return min(unconqured_planets, key=lambda planet: self.calculate_distance(
        #     game, my_strongest_planet, planet))

    def get_planets_to_attack(self, game: PlanetWars) -> List[Planet]:
        """
        :param game: PlanetWars object representing the map
        :return: The planets we need to attack
        """
        return self.find_closest_planet_to_strongest_self_planet(game)

    def ships_to_send_in_a_flee(self, source_planet: Planet) -> int:
        return source_planet.num_ships * 4 // 10

    def play_turn(self, game: PlanetWars) -> Iterable[Order]:
        """
        See player.play_turn documentation.
        :param game: PlanetWars object representing the map - use it to fetch all the planets and flees in the map.
        :return: List of orders to execute, each order sends ship from a planet I own to other planet.
        """

        # (1) If we currently have three fleets in flight, just do nothing.
        if len(game.get_fleets_by_owner(owner=PlanetWars.ME)) >= 3:
            return []

        # (2) Find my strongest planet and enemy's strongest planet.
        my_planets = game.get_planets_by_owner(owner=PlanetWars.ME)
        if len(my_planets) == 0:
            return []
        my_strongest_planet = max(
            my_planets, key=lambda planet: planet.num_ships)
        enemy_planets = game.get_planets_by_owner(owner=PlanetWars.ENEMY)
        if len(enemy_planets) == 0:
            return []
        enemy_strongest_planet = max(
            enemy_planets, key=lambda planet: planet.num_ships)
        if my_strongest_planet.num_ships < (enemy_strongest_planet.num_ships-1) // len(game.get_planets_by_owner(1)):
            return []

        # # (3) Find the weakest enemy or neutral planet.
        # planets_to_attack = self.get_planets_to_attack(game)
        # if len(planets_to_attack) == 0:
        #     return []
        # enemy_or_neutral_weakest_planet = min(
        #     planets_to_attack, key=lambda planet: planet.num_ships)

        # (4) Find the closest enemy or neutral planet

        # (5) Send 40% the ships from my strongest planet to the weakest planet that I do not own.
        return [Order(
            my_strongest_planet,
            self.find_closest_planet_to_strongest_self_planet(game),
            self.ships_to_send_in_a_flee(
                my_strongest_planet)
        )]


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
    print(df.won.sum()/df.shape[0]*100)
    print("\n\n")
    print(tester.get_score_object())

    # To view battle number 4 uncomment the line below
    tester.view_battle(4)


if __name__ == "__main__":
    check_bot()
    # view_bots_battle()
