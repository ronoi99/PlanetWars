from typing import Iterable

# from awasomeBot import awasomeBot
# from FireflyZ import FireflyZ_Bot
# from girlsPower import GirlsPowerlBot
# from Kvutza6 import Kvutza6
# from rust_react_gulp import Rust_react_gulp
# from shmerlingBot import shmerlingBot
# from undefined import Undefined

import pandas as pd

from baseline_bot import AttackWeakestPlanetFromStrongestBot, AttackEnemyWeakestPlanetFromStrongestBot, \
    AttackWeakestPlanetFromStrongestSmarterNumOfShipsBot, get_random_map
from planet_wars.battles.tournament import get_map_by_id, run_and_view_battle, TestBot
from planet_wars.planet_wars import Player, PlanetWars, Order, Planet


class Wookies(Player):
    """
    Implement here your smart logic.
    Rename the class and the module to your team name
    """

    def get_planets_by_owner(self, game: PlanetWars, owner):
        return [p for p in game.planets if p.owner == owner]

    def get_closest_planet(self, my_planet, other_planets):
        # First temporary "closest planet" (soon to be replaced)

        closest_planet = other_planets[0]
        smallest_distance = Planet.distance_between_planets(
            my_planet, closest_planet)

        # Go through all enemy planets
        for enemy_planet in other_planets:

            # Checking the current enemy planet
            tested_distance = Planet.distance_between_planets(
                my_planet, enemy_planet)

            # If a closer planet was discovered, set it as the nearest
            if tested_distance < smallest_distance:
                closest_planet = enemy_planet

        return closest_planet

    def get_multi_closest_planets(self, my_planet, other_planets, num_of_planets):
        if len(other_planets) == 0:
            return None
        planets_array = []
        for i in range(num_of_planets):
            closest_planet = self.get_closest_planet(
                my_planet, other_planets)
            planets_array.append(closest_planet)
            other_planets.remove(closest_planet)

        planets_array = sorted(
            planets_array, key=lambda planet: planet.num_ships)
        return planets_array

    def calc_ships(self, planet_enemy, my_strongest_planet):
        growth = planet_enemy.growth_rate
        turns = Planet.distance_between_planets(
            my_strongest_planet, planet_enemy)
        result = planet_enemy.num_ships + (growth * turns) + 1
        return result

    def check_if_fleet(self, game: PlanetWars, planets):
        my_fleets = PlanetWars.get_fleets_by_owner(game, PlanetWars.ME)
        my_dest = set([fleet.destination_planet_id for fleet in my_fleets])
        planets_ids = set([planet.planet_id for planet in planets])
        undestined_planets = list(planets_ids - my_dest)
        undestined_planets = [game.get_planet_by_id(
            id) for id in undestined_planets]
        # print(len(undestined_planets))
        return undestined_planets

    def play_turn(self, game: PlanetWars) -> Iterable[Order]:
        # TODO: if the enemy in the 5 closes - it`s mast to attack him !!!
        # if game.turns < 50:
        #     # print('test')
        
        my_planets = self.get_planets_by_owner(game, PlanetWars.ME)
        if len(my_planets) == 0:
            return []
        my_strongest_planet = max(
            my_planets, key=lambda planet: planet.num_ships)

        neutral_planets = self.get_planets_by_owner(game, PlanetWars.NEUTRAL)
        enemy_planets = self.get_planets_by_owner(game, PlanetWars.ENEMY)
        enemy_neutral_planets = neutral_planets + enemy_planets
        other_planets_after_sort = self.check_if_fleet(
            game, enemy_neutral_planets)

        # print(len(enemy_neutral_planets), len(other_planets_after_sort))
        if len(enemy_neutral_planets) == 0:
            return []

        nearest_planets = self.get_multi_closest_planets(
            my_strongest_planet, other_planets_after_sort, min(5, len(other_planets_after_sort)))

        if nearest_planets is None:
            return []
        array_order = []
        more_ships = my_strongest_planet.num_ships
        if game.turns < 40:
            # print('test')
            for planet in nearest_planets:
                if planet.owner == PlanetWars.ENEMY:
                    return [Order(
                        my_strongest_planet,
                        planet,
                        more_ships
                    )]

        for planet in nearest_planets:
            # PlanetWars.NEUTRAL:
            if more_ships > planet.num_ships and planet.owner == PlanetWars.NEUTRAL:
                array_order.append(
                    Order(
                        my_strongest_planet,
                        planet,
                        planet.num_ships+1
                    )
                )
                more_ships -= planet.num_ships+1

            # PlanetWars.ENEMY:
            elif planet.owner == PlanetWars.ENEMY:
                ships_enemy = self.calc_ships(planet, my_strongest_planet)
                if ships_enemy < more_ships:
                    array_order.append(
                        Order(
                            my_strongest_planet,
                            planet,
                            ships_enemy
                        )
                    )
                    more_ships -= ships_enemy
        # print('array_order: ', array_order)
        return array_order


def view_bots_battle():
    """
    Runs a battle and show the results in the Java viewer

    Note: The viewer can only open one battle at a time - so before viewing new battle close the window of the
    previous one.
    Requirements: Java should be installed on your device.
    """
    map_str = get_random_map()
    run_and_view_battle(Wookies(
    ), AttackEnemyWeakestPlanetFromStrongestBot(), map_str)



def check_bot():
    """
    Test AttackWeakestPlanetFromStrongestBot against the 2 other bots.
    Print the battle results data frame and the PlayerScore object of the tested bot.
    So is AttackWeakestPlanetFromStrongestBot worse than the 2 other bots? The answer might surprise you.
    """
    maps = []

    for i in range(1, 101, 1):
        temp_map = get_map_by_id(i)
        maps.append(temp_map)

    player_bot_to_test = Wookies()
    tester = TestBot(
        player=player_bot_to_test,
        competitors=[
            AttackWeakestPlanetFromStrongestSmarterNumOfShipsBot(),
            AttackEnemyWeakestPlanetFromStrongestBot(),
            AttackWeakestPlanetFromStrongestSmarterNumOfShipsBot(),
            # awasomeBot(),
            # FireflyZ_Bot(),
            # GirlsPowerlBot(),
            # Kvutza6(),
            # Rust_react_gulp(),
            # # shmerlingBot(),
            # Undefined()
        ],
        maps=maps
    )
    tester.run_tournament()

    # for a nicer df printing
    pd.set_option('display.max_columns', 30)
    pd.set_option('expand_frame_repr', False)

    # print(tester.get_testing_results_data_frame())
    print("\n\n")
    print(tester.get_score_object())

    # To view battle number 4 uncomment the line below
    # tester.view_battle(4)


if __name__ == "__main__":
    check_bot()
    # view_bots_battle()
