from typing import Iterable

import pandas as pd

from baseline_bot import AttackWeakestPlanetFromStrongestBot, AttackEnemyWeakestPlanetFromStrongestBot, \
    AttackWeakestPlanetFromStrongestSmarterNumOfShipsBot, get_random_map
from planet_wars.battles.tournament import run_and_view_battle, TestBot, get_map_by_id
from planet_wars.planet_wars import Player, PlanetWars, Order, Planet

class AlexDavidBot(Player):
    """
    Implement here your smart logic.
    Rename the class and the module to your team name
    """

    def closest_planets(self, game: PlanetWars, planet: Planet):
        my_attacked_planets = [p for p in game.get_planets_by_owner(game.ME) if self.is_under_attack(game, p)]
        return sorted([*game.get_planets_by_owner(game.NEUTRAL), *game.get_planets_by_owner(game.ENEMY), *my_attacked_planets], key=lambda x: Planet.distance_between_planets(x, planet))

    def close_planets_under_attack(self, game: PlanetWars, planet: Planet):
        return sorted([*game.get_planets_by_owner(game.NEUTRAL), *game.get_planets_by_owner(game.ENEMY)], key=lambda x: Planet.distance_between_planets(x, planet))

    def my_strongest_planet(self, game: PlanetWars):
        return max(game.get_planets_by_owner(game.ME), key=lambda x: x.num_ships)

    def highest_neutral_planet(self, game: PlanetWars):
        return max(game.get_planets_by_owner(game.NEUTRAL), key=lambda x: x.growth_rate)

    def is_under_attack(self, game: PlanetWars, dest_planet: Planet) -> int:
        for fleet in game.get_fleets_by_owner(game.ENEMY):
            if fleet.destination_planet_id == dest_planet.planet_id:
                return True
        return False

    def is_my_fleet_on_the_way(self, game: PlanetWars, dest_planet: Planet) -> int:
        for fleet in game.get_fleets_by_owner(game.ME):
            if fleet.destination_planet_id == dest_planet.planet_id:
                return True
        return False

    def ships_needed_to_win(self, game: PlanetWars, source_planet: Planet, dest_planet: Planet) -> int:
        if dest_planet.owner == PlanetWars.ME:
            return 25
        if dest_planet.owner == PlanetWars.NEUTRAL:
            return dest_planet.num_ships
        else:
            return dest_planet.num_ships + dest_planet.growth_rate * Planet.distance_between_planets(source_planet, dest_planet)
        # if enemy fleet on the way? etc..

    def play_turn(self, game: PlanetWars) -> Iterable[Order]:
        """
        See player.play_turn documentation.
        :param game: PlanetWars object representing the map - use it to fetch all the planets and flees in the map.
        :return: List of orders to execute, each order sends ship from a planet I own to other planet.
        """
        if game.turns < 0:
            return

        if (len(game.get_planets_by_owner(game.ME))==0):
            return []

        if (len(game.get_planets_by_owner(game.ENEMY)) + len(game.get_planets_by_owner(game.NEUTRAL)) == 0):
            return []


        orders = []
        for planet in game.get_planets_by_owner(game.ME):
            if self.is_under_attack(game, planet):
                continue
            source_planet = planet
            skips = 0
            available_ships = planet.num_ships
            for dest_planet in sorted(self.closest_planets(game, source_planet)[:8], key= lambda x: (x.growth_rate + 25/(x.num_ships+1))*(1,1,3)[x.owner])[::-1]:
                ships_needed_to_win = max(10, self.ships_needed_to_win(game, source_planet, dest_planet) + 2)

                if available_ships >= ships_needed_to_win:
                    orders.append(Order(
                        source_planet,
                        dest_planet,
                        ships_needed_to_win
                    ))
                    available_ships -= ships_needed_to_win
                else:
                    skips +=1
                if skips >= 2:
                    break
        return orders

# class AlexDavidBot2(Player):
#     """
#     Implement here your smart logic.
#     Rename the class and the module to your team name
#     """
#     def closest_planets(self, game: PlanetWars, planet: Planet):
#         return sorted([*game.get_planets_by_owner(game.NEUTRAL), *game.get_planets_by_owner(game.ENEMY)], key=lambda x: Planet.distance_between_planets(x, planet))
#
#     def closest_other_planets(self, game: PlanetWars, planet: Planet):
#         return sorted([*game.get_planets_by_owner(game.NEUTRAL), *game.get_planets_by_owner(game.ENEMY)],
#                       key=lambda x: Planet.distance_between_planets(x, planet))
#
#     def closest_my_planets(self, game: PlanetWars, planet: Planet):
#         return sorted(game.get_planets_by_owner(game.ME),
#                       key=lambda x: Planet.distance_between_planets(x, planet))
#
#     def defend_allies(self, game: PlanetWars, planet: Planet, ally_planet_number=5):
#         planets_to_defend = {}
#         enemy_fleets = game.get_fleets_by_owner(game.ENEMY)
#         for ally_planet in self.closest_my_planets(game, planet)[:ally_planet_number]:
#             enemy_fleets_count = [enemy_fleet.num_ships for enemy_fleet in enemy_fleets if enemy_fleet.destination_planet_id == ally_planet.planet_id]
#             if ally_planet.num_ships < sum(enemy_fleets_count):
#                 planets_to_defend[ally_planet] = sum(enemy_fleets_count) - ally_planet.num_ships
#         return planets_to_defend
#
#
#     def my_strongest_planet(self, game: PlanetWars):
#         return max(game.get_planets_by_owner(game.ME), key=lambda x: x.num_ships)
#
#     def highest_neutral_planet(self, game: PlanetWars):
#         return max(game.get_planets_by_owner(game.NEUTRAL), key=lambda x: x.growth_rate)
#
#     def is_my_fleet_on_the_way(self, game: PlanetWars, dest_planet: Planet) -> int:
#         for fleet in game.get_fleets_by_owner(game.ME):
#             if fleet.destination_planet_id == dest_planet.planet_id:
#                 return True
#         return False
#
#     def ships_needed_to_win(self, game: PlanetWars, source_planet: Planet, dest_planet: Planet) -> int:
#         if dest_planet.owner == PlanetWars.NEUTRAL:
#             return dest_planet.num_ships
#         else:
#             return dest_planet.num_ships + dest_planet.growth_rate * Planet.distance_between_planets(source_planet, dest_planet)
#         # if enemy fleet on the way? etc..
#
#     def maximum_available_for_attack(self, game: PlanetWars, planet: Planet):
#         attacking_fleets = [fleet.num_ships for fleet in game.get_fleets_by_owner(game.ENEMY) if fleet.destination_planet_id==planet.planet_id]
#         reinforcement_fleets = [fleet.num_ships for fleet in game.get_fleets_by_owner(game.ME) if
#                             fleet.destination_planet_id == planet.planet_id]
#         # print(sum(attacking_fleets), sum(reinforcement_fleets))
#         return planet.num_ships - sum(attacking_fleets) + sum(reinforcement_fleets)
#
#
#     def play_turn(self, game: PlanetWars) -> Iterable[Order]:
#         """
#         See player.play_turn documentation.
#         :param game: PlanetWars object representing the map - use it to fetch all the planets and flees in the map.
#         :return: List of orders to execute, each order sends ship from a planet I own to other planet.
#         """
#
#         if (len(game.get_planets_by_owner(game.ME))==0):
#             return []
#
#         if (len(game.get_planets_by_owner(game.ENEMY)) + len(game.get_planets_by_owner(game.NEUTRAL)) == 0):
#             return []
#
#
#         orders = []
#         print(game.turns)
#         if game.turns == 0:
#             return []
#         for planet in game.get_planets_by_owner(game.ME):
#             source_planet = planet
#             for dest_planet in sorted(self.closest_planets(game, source_planet)[:8], key= lambda x: (x.growth_rate, x.growth_rate*4)[x.owner==game.ENEMY])[::-1]:
#                 ships_needed_to_win = max(10, self.ships_needed_to_win(game, source_planet, dest_planet) + 1)
#                 orders.append(Order(
#                     source_planet,
#                     dest_planet,
#                     ships_needed_to_win
#                 ))
#         return orders


def view_bots_battle(map_id: int):
    """
    Runs a battle and show the results in the Java viewer

    Note: The viewer can only open one battle at a time - so before viewing new battle close the window of the
    previous one.
    Requirements: Java should be installed on your device.
    """
    map_str = get_map_by_id(map_id)
    run_and_view_battle(Arrakis(), AlexDavidBot(),  map_str)

def run_all_maps():
    """
    Runs a battle and show the results in the Java viewer

    Note: The viewer can only open one battle at a time - so before viewing new battle close the window of the
    previous one.
    Requirements: Java should be installed on your device.
    """
    results = []
    lost_maps = []
    for i in range(100):
        map_str = get_map_by_id(i+1)
        results.append(run_battle(RonCoolBot(), AlexDavidBot(),  map_str)[0].winner)
        if results[-1] == 1:
            lost_maps.append(i+1)
    lost_maps2 = []
    for i in range(100):
        map_str = get_map_by_id(i + 1)
        results.append(run_battle(AlexDavidBot(), RonCoolBot(), map_str)[0].winner)
        if results[-1] == 2:
            lost_maps2.append(i + 1)
   # print(f'Player 1 wins: {len([result for result in results if result == 1])}, Player 2 wins {len([result for result in results if result == 2])}')
    print(lost_maps, lost_maps2)
    print(len(lost_maps), len(lost_maps2))


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
    #view_bots_battle(2)
    run_all_maps()