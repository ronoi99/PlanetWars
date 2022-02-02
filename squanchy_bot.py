import random
from typing import Iterable, List
from ef_bot import ETerror
from arnon import SquanchyArn
from functools import reduce

from planet_wars.planet_wars import Player, PlanetWars, Order, Planet
from planet_wars.battles.tournament import get_map_by_id, run_and_view_battle, TestBot

import pandas as pd


class SquanchyBot(Player):
    """
    Example of very simple bot - it send flee from its strongest planet to the weakest enemy/neutral planet
    """

    def get_planets_to_attack(self, game: PlanetWars) -> List[Planet]:
        """
        :param game: PlanetWars object representing the map
        :return: The planets we need to attack
        """
        return [p for p in game.planets if p.owner != PlanetWars.ME]

    def ships_to_send_in_a_flee(self, source_planet: Planet, dest_planet: Planet) -> int:
        if source_planet.num_ships < 10:
            return 0
        # return source_planet.num_ships // 2
        return self.get_needed_ships(source_planet, dest_planet) + 2

    def get_my_planets(self, game: PlanetWars):
        return [p for p in game.planets if p.owner == PlanetWars.ME]

    def play_turn(self, game: PlanetWars) -> Iterable[Order]:
        """
        See player.play_turn documentation.
        :param game: PlanetWars object representing the map - use it to fetch all the planets and flees in the map.
        :return: List of orders to execute, each order sends ship from a planet I own to other planet.
        """
        # (1) If we currently have a fleet in flight, just do nothing.
        # if len(game.get_fleets_by_owner(owner=PlanetWars.ME)) >= 1:
        #     return []
        #
        # # (2) Find my strongest planet.
        # my_planets = game.get_planets_by_owner(owner=PlanetWars.ME)
        # if len(my_planets) == 0:
        #     return []
        # my_strongest_planet = max(my_planets, key=lambda planet: planet.num_ships)

        # (3) Find the weakest enemy or neutral planet.
        planets_to_attack = self.get_planets_to_attack(game)
        my_planets = self.get_my_planets(game)
        # if len(planets_to_attack) == 0:
        #     return []
        # enemy_or_neutral_weakest_planet = min(planets_to_attack, key=lambda planet: planet.num_ships)
        if len(my_planets) == 0:
            return

        final_orders = []
        for my_planet in my_planets:
            planets_grades = self.calculate_planet_grade(my_planet, planets_to_attack, "start", game)

            if len(planets_grades) == 0:
                return
            chosen_enemy_planet = max(planets_grades.items(), key=lambda x: x[1])[0]
            final_orders.append(
                Order(my_planet, chosen_enemy_planet,
                      self.ships_to_send_in_a_flee(my_planet, game.get_planet_by_id(chosen_enemy_planet))))
        # (4) Send half the ships from my strongest planet to the weakest planet that I do not own.
        return final_orders

    def calculate_planet_grade(self, source_planet: Planet, enemy_planet_list: List[Planet], game_stage: str,
                               game) -> dict:
        grades_dictionary = {}
        # print("---------", enemy_planet_list)
        planets_distances = [Planet.distance_between_planets(source_planet, i) for i in enemy_planet_list] if len(
            [Planet.distance_between_planets(source_planet, i) for i in enemy_planet_list]) else [50]
        max_distance = max(planets_distances)
        for enemy_planet in enemy_planet_list:
            distance = Planet.distance_between_planets(source_planet, enemy_planet)
            enemy_ship_count = int(enemy_planet.num_ships)
            home_ships = int(source_planet.num_ships)
            enemy_growth = int(enemy_planet.growth_rate)
            home_growth = int(source_planet.growth_rate)

            weight_dict = {
                "start": {"distance": 5, "enemy_ship_count": 3, "home_ships": -2, "enemy_growth": 4, "home_growth": 0}}

            # attack_grade = self.calc_distance_grade(enemy_planet, distance, max_distance,
            #                                         game_stage) + enemy_ship_count * weight_dict[game_stage][
            #                    "enemy_ship_count"] + home_ships * weight_dict[game_stage]["home_ships"] + home_ships * \
            #                weight_dict[game_stage]["enemy_growth"] + home_growth * weight_dict[game_stage][
            #                    "home_growth"]

            attack_grade = self.calc_distance_grade(enemy_planet, distance, max_distance,
                                                    game_stage) + self.calc_attack_potential(source_planet,
                                                                                             enemy_planet, game_stage,
                                                                                             game) + self.calc_size_grade(
                enemy_planet) + 5 if enemy_planet.owner == 2 else 0 + (2 /distance)
            grades_dictionary[enemy_planet.planet_id] = attack_grade

        return grades_dictionary

    def calc_size_grade(self, enemy_planet: Planet):
        return enemy_planet.growth_rate * 3

    def calc_distance_grade(self, enemy_planet: Planet, distance: int, max_distance, game_stage: str):
        if game_stage == "start":
            # print("max ",max_distance)
            # print("dis ",distance)
            return 0

    def calc_attack_potential(self, source_planet, enemy_planet: Planet, game_stage: str, game: PlanetWars):
        my_ships = source_planet.num_ships
        distance = Planet.distance_between_planets(source_planet, enemy_planet)
        enemy_fleets_coming = [i for i in game.get_fleets_by_owner(2) if
                               i.destination_planet_id == enemy_planet.planet_id]

        needed_ships = 0

        if enemy_planet.owner == 0:
            if enemy_fleets_coming:

                needed_ships = abs(
                    enemy_planet.num_ships - sum([i.num_ships for i in enemy_fleets_coming]))
            else:
                needed_ships = enemy_planet.num_ships
        else:
            growth = enemy_planet.growth_rate * distance
            if enemy_fleets_coming:
                needed_ships = enemy_planet.num_ships + sum([i.num_ships for i in enemy_fleets_coming]) + growth
            else:
                needed_ships = enemy_planet.num_ships + growth

        my_fleets_comming = [i for i in game.get_fleets_by_owner(1) if
                             i.destination_planet_id == enemy_planet.planet_id]

        if my_fleets_comming:
            needed_ships = needed_ships + sum([i.num_ships for i in my_fleets_comming])

        if game_stage == "start":
            dif_sh = my_ships - needed_ships
            return (my_ships - needed_ships) * 2

    def get_needed_ships(self, source_planet, enemy_planet):
        distance = Planet.distance_between_planets(source_planet, enemy_planet)
        return enemy_planet.num_ships if enemy_planet.owner == 0 else (
                                                                              distance * enemy_planet.growth_rate) + enemy_planet.num_ships


class AttackWeakestPlanetFromStrongestBot(Player):
    """
    Example of very simple bot - it send flee from its strongest planet to the weakest enemy/neutral planet
    """

    def get_planets_to_attack(self, game: PlanetWars) -> List[Planet]:
        """
        :param game: PlanetWars object representing the map
        :return: The planets we need to attack
        """
        return [p for p in game.planets if p.owner != PlanetWars.ME]

    def ships_to_send_in_a_flee(self, source_planet: Planet, dest_planet: Planet) -> int:
        return source_planet.num_ships // 2

    def play_turn(self, game: PlanetWars) -> Iterable[Order]:
        """
        See player.play_turn documentation.
        :param game: PlanetWars object representing the map - use it to fetch all the planets and flees in the map.
        :return: List of orders to execute, each order sends ship from a planet I own to other planet.
        """
        # (1) If we currently have a fleet in flight, just do nothing.
        if len(game.get_fleets_by_owner(owner=PlanetWars.ME)) >= 1:
            return []

        # (2) Find my strongest planet.
        my_planets = game.get_planets_by_owner(owner=PlanetWars.ME)
        if len(my_planets) == 0:
            return []
        my_strongest_planet = max(my_planets, key=lambda planet: planet.num_ships)

        # (3) Find the weakest enemy or neutral planet.
        planets_to_attack = self.get_planets_to_attack(game)
        if len(planets_to_attack) == 0:
            return []
        enemy_or_neutral_weakest_planet = min(planets_to_attack, key=lambda planet: planet.num_ships)

        # (4) Send half the ships from my strongest planet to the weakest planet that I do not own.
        return [Order(
            my_strongest_planet,
            enemy_or_neutral_weakest_planet,
            self.ships_to_send_in_a_flee(my_strongest_planet, enemy_or_neutral_weakest_planet)
        )]


class AttackEnemyWeakestPlanetFromStrongestBot(AttackWeakestPlanetFromStrongestBot):
    """
    Same like AttackWeakestPlanetFromStrongestBot but attacks only enemy planet - not neutral planet.
    The idea is not to "waste" ships on fighting with neutral planets.

    See which bot is better using the function view_bots_battle
    """

    def get_planets_to_attack(self, game: PlanetWars):
        """
        :param game: PlanetWars object representing the map
        :return: The planets we need to attack - attack only enemy's planets
        """
        return game.get_planets_by_owner(owner=PlanetWars.ENEMY)


class AttackWeakestPlanetFromStrongestSmarterNumOfShipsBot(AttackWeakestPlanetFromStrongestBot):
    """
    Same like AttackWeakestPlanetFromStrongestBot but with smarter flee size.
    If planet is neutral send up to its population + 5
    If it is enemy send most of your ships to fight!

    Will it out preform AttackWeakestPlanetFromStrongestBot? see test_bot function.
    """

    def ships_to_send_in_a_flee(self, source_planet: Planet, dest_planet: Planet) -> int:
        original_num_of_ships = source_planet.num_ships // 2
        if dest_planet.owner == PlanetWars.NEUTRAL:
            if dest_planet.num_ships < original_num_of_ships:
                return dest_planet.num_ships + 5
        if dest_planet.owner == PlanetWars.ENEMY:
            return int(source_planet.num_ships * 0.75)
        return original_num_of_ships


def get_random_map():
    """
    :return: A string of a random map in the maps directory
    """
    random_map_id = random.randrange(1, 100)
    return get_map_by_id(random_map_id)


def view_bots_battle():
    """
    Runs a battle and show the results in the Java viewer

    Note: The viewer can only open one battle at a time - so before viewing new battle close the window of the
    previous one.
    Requirements: Java should be installed on your device.
    """
    map_str = get_random_map()
    run_and_view_battle(SquanchyBot(), SquanchyArn(), map_str)


def check_bot():
    """
    Test AttackWeakestPlanetFromStrongestBot against the 2 other bots.
    Print the battle results data frame and the PlayerScore object of the tested bot.
    So is AttackWeakestPlanetFromStrongestBot worse than the 2 other bots? The answer might surprise you.
    """
    maps = [get_random_map(), get_random_map()]
    player_bot_to_test = SquanchyBot()
    tester = TestBot(
        player=player_bot_to_test,
        competitors=[
            SquanchyArn(), AttackWeakestPlanetFromStrongestSmarterNumOfShipsBot()
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
    check_bot()
    view_bots_battle()
