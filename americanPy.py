import math
from typing import Iterable, List, Tuple

import pandas as pd
# from undefined import shmerlingBot
# from undefied2 import Undefined
# from awesomebot import awasomeBot
# from rust import HorneyMonkey

from baseline_bot import AttackWeakestPlanetFromStrongestBot, AttackEnemyWeakestPlanetFromStrongestBot, \
    AttackWeakestPlanetFromStrongestSmarterNumOfShipsBot, get_random_map
from planet_wars.battles.tournament import get_map_by_id, run_and_view_battle, TestBot
from planet_wars.planet_wars import Player, PlanetWars, Order, Planet

min_ships_remain = 30
min_ships_in_planet = 45
distance_between_planets = 5


class americanPy(Player):
    """
    Implement here your smart logic.
    Rename the class and the module to your team name
    """

    def play_turn(self, game: PlanetWars) -> Iterable[Order]:
        """
        See player.play_turn documentation.
        :param game: PlanetWars object representing the map - use it to fetch all the planets and flees in the map.
        :return: List of orders to execute, each order sends ship from a planet I own to other planet.
        """

        results = []

        # all neutral planets
        listNeutralByRating = [
            (float(100.0 if planet.growth_rate == 0 else
                   planet.num_ships/planet.growth_rate**3), planet)
            for planet in game.get_planets_by_owner(PlanetWars.NEUTRAL)]

        # all enemy planets
        listEnemyByRating = [
            (float(100.0 if planet.growth_rate == 0 else
                   planet.num_ships/planet.growth_rate**3), planet)
            for planet in game.get_planets_by_owner(PlanetWars.ENEMY)]

        # sort both planets types by their ratings
        listNeutralByRating.sort(key=lambda x: x[0])
        listEnemyByRating.sort(key=lambda x: x[0])

        # get my planets
        my_good_planets = get_plants_not_in_risk(game)
        my_risked_planets = get_plants_in_risk(game)

        # calculate move section
        for planet in my_good_planets:
            # set total ships in a planet to send to other planets if possible
            curr_planet_total_ships = planet.num_ships
            while curr_planet_total_ships > min_ships_in_planet:
                # break
                curr_planet, rating = get_high_priority_planet(
                    my_risked_planets, listNeutralByRating, listEnemyByRating, planet)
                # ship_num = curr_planet.num_ships
                send = calc_needed_ships(
                    planet, curr_planet, curr_planet_total_ships, rating)
                # ships_sent = 50
                curr_planet_total_ships -= send
                if send == 0:
                    break
                results.append(Order(planet, curr_planet, send+10))

        return results


def listNeutralByDist():
    pass


def get_target_planet(my_planets: List[Planet], other_planets: List[Tuple[float, Planet]]):
    # if len(other_planets) > 0:
    other_planets.sort(key=lambda x: get_avg_distance(my_planets, x[1]))
    if len(other_planets):
        return other_planets.pop(0)
    return (0, None)
    # elif len(enemies) > 0:
    #     enemies.sort(key=lambda x: get_avg_distance(my_planets, x[1]))
    #     return enemies.pop(0)
    # else:
    #     return (0, None)


def get_avg_distance(planets: List[Planet], target: Planet):
    total = 0
    for planet in planets:
        total += Planet.distance_between_planets(planet, target)

    return 0 if not total else total // len(planets)


def calc_needed_ships(source: Planet, target: Planet, curr_ships_num: int, rating: float):
    needed = 0
    if target and target.owner == PlanetWars.ME:
        needed = rating + 10
    elif target and target.owner == PlanetWars.ENEMY:
        needed = int(Planet.distance_between_planets(
            source, target) * int(target.growth_rate + 1.5))
    elif target and target.owner == PlanetWars.NEUTRAL:
        needed = target.num_ships + 10
    else:
        return 0
    return min(needed, curr_ships_num - min_ships_remain)


def get_high_priority_planet(my_planets: List[Tuple[float, Planet]], neutral: List[Tuple[float, Planet]], enemy: List[Tuple[float, Planet]], source_planet: Planet):
    if len(my_planets) > 0:
        planet = my_planets.pop(0)
        return (planet[1], planet[0])
    elif len(neutral) > 0:
        neutral.sort(key=lambda x: x[0] +
                     math.sqrt
                     (Planet.distance_between_planets(source_planet, x[1])/4))
        planet = neutral.pop(0)
        return (planet[1], planet[0])
    elif len(enemy) > 0:
        enemy.sort(key=lambda x: x[0] +
                   math.sqrt
                   (Planet.distance_between_planets(source_planet, x[1])/4))
        planet = enemy.pop(0)
        return (planet[1], planet[0])
    else:
        return (None, 0)


def get_plants_not_in_risk(game: PlanetWars):
    my_planets = game.get_planets_by_owner(PlanetWars.ME)
    return [planet for planet in my_planets
            if get_fleets_on_planet(game, planet) == 0 and planet.num_ships > 20]


def get_plants_in_risk(game: PlanetWars):
    my_planets = game.get_planets_by_owner(PlanetWars.ME)
    results = [(float(get_fleets_on_planet(game, planet) - planet.num_ships + get_my_fleet_on_planet(game, planet)), planet) for planet in my_planets
               if get_fleets_on_planet(game, planet) > planet.num_ships + get_my_fleet_on_planet(game, planet)]
    results.sort(key=lambda x: x[0], reverse=True)
    return results


def get_fleets_on_planet(game: PlanetWars, planet: Planet):
    enemy_fleets = game.get_fleets_by_owner(PlanetWars.ENEMY)
    total = 0
    for fleet in enemy_fleets:
        if fleet.destination_planet_id == planet.planet_id:
            total += fleet.num_ships
    return total


def get_my_fleet_on_planet(game: PlanetWars, planet: Planet):
    my_fleet = game.get_fleets_by_owner(PlanetWars.ME)
    total = 0
    for fleet in my_fleet:
        if fleet.destination_planet_id == planet.planet_id:
            total += fleet.num_ships
    return total


def get_all_planets(game: PlanetWars):
    return game.get_planets_by_owner(PlanetWars.ENEMY) + game.get_planets_by_owner(PlanetWars.NEUTRAL)


def view_bots_battle():
    """
    Runs a battle and show the results in the Java viewer

    Note: The viewer can only open one battle at a time - so before viewing new battle close the window of the
    previous one.
    Requirements: Java should be installed on your device.
    """
    map_str = get_random_map()
    # map_str = get_map_by_id(22)
    # run_and_view_battle(awasomeBot(
    # ), americanPy(), map_str)
    #     run_and_view_battle(AttackWeakestPlanetFromStrongestBot(
    # ), AttackEnemyWeakestPlanetFromStrongestBot(), map_str)


def check_bot():
    """
    Test AttackWeakestPlanetFromStrongestBot against the 2 other bots.
    Print the battle results data frame and the PlayerScore object of the tested bot.
    So is AttackWeakestPlanetFromStrongestBot worse than the 2 other bots? The answer might surprise you.
    """
    # AttackWeakestPlanetFromStrongestBot
    # AttackEnemyWeakestPlanetFromStrongestBot / 4 lost
    # AttackWeakestPlanetFromStrongestSmarterNumOfShipsBot / 2 lost
    maps = [get_random_map(i+1) for i in range(99)]
    player_bot_to_test = americanPy()
    tester = TestBot(
        player=player_bot_to_test,
        competitors=[
            HorneyMonkey()
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
    # view_bots_battle()
