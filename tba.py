from typing import Iterable, List
from numpy import choose, source

import pandas as pd
# from GirlsPower import GirlsPowerlBot
# from awasomeBot import awasomeBot

from baseline_bot import AttackWeakestPlanetFromStrongestBot, AttackEnemyWeakestPlanetFromStrongestBot, \
    AttackWeakestPlanetFromStrongestSmarterNumOfShipsBot, get_random_map
from planet_wars.battles.tournament import run_and_view_battle, TestBot
from planet_wars.planet_wars import Fleet, Player, PlanetWars, Order, Planet
# from shmerlingBot import shmerlingBot
# from tba_old import tba_old


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
        classify = []
        for i in to_attack:
            classify.append({"grow": i.growth_rate, "num_ships": i.num_ships,
                             "distance": i.distance_between_planets(self.source(game), i), "id": i.planet_id})
        scores = []
        for i in classify:
            our_fleets = [f for f in game.fleets if f.owner == 1]
            if len(our_fleets) > 0:
                for fleet in our_fleets:
                    if i["id"] != fleet.destination_planet_id:
                        scores.append({"score": i["grow"]*2 /
                                       (i["num_ships"]+i["distance"]*15), "id": i["id"]})
            else:
                scores.append({"score": i["grow"]*2 /
                               (i["num_ships"]+(i["distance"]*15)), "id": i["id"]})
        max = {"score": 0, "id": -1}
        for i in scores:
            if i["score"] > max["score"]:
                max["score"] = i["score"]
                max["id"] = i["id"]
        chosen = max
        return chosen["id"]

    def ships_to_send_in_a_flee(self, game, source_planet: Planet, dest_planet: Planet) -> int:
        dest: Planet = game.get_planet_by_id(int(dest_planet))
        if dest == None:
            return 0
        if dest.owner != 0:
            to_be = dest.num_ships + ((dest.growth_rate+1) *
                                      source_planet.distance_between_planets(self.source(game), dest))
        else:
            to_be = dest.num_ships
        if(source_planet.num_ships > to_be):
            return to_be+1
        return 0

    def source(self, game):
        my_planets = game.get_planets_by_owner(owner=PlanetWars.ME)
        my_strongest_planet = max(
            my_planets, key=lambda planet: planet.num_ships)
        return my_strongest_planet

    def append_order(self, game, orders):
        orders.append(Order(self.source(game), self.get_planets_to_attack(
            game), self.ships_to_send_in_a_flee(game, self.source(game), self.get_planets_to_attack(game))))
        return orders

    def play_turn(self, game: PlanetWars) -> Iterable[Order]:
        """
        See player.play_turn documentation.
        :param game: PlanetWars object representing the map - use it to fetch all the planets and flees in the map.
        :return: List of orders to execute, each order sends ship from a planet I own to other planet.
        """
        my_planets = game.get_planets_by_owner(owner=PlanetWars.ME)
        if len(my_planets) == 0:
            return []
        orders = []
        self.append_order(game, orders)
        return orders


def view_bots_battle():
    """
    Runs a battle and show the results in the Java viewer

    Note: The viewer can only open one battle at a time - so before viewing new battle close the window of the
    previous one.
    Requirements: Java should be installed on your device.
    """
    map_str = get_random_map()
    run_and_view_battle(tba(
    ), tba_old(), map_str)


def check_bot():
    """
    Test AttackWeakestPlanetFromStrongestBot against the 2 other bots.
    Print the battle results data frame and the PlayerScore object of the tested bot.
    So is AttackWeakestPlanetFromStrongestBot worse than the 2 other bots? The answer might surprise you.
    """
    maps = [get_random_map(), get_random_map()]
    player_bot_to_test = tba()
    tester = TestBot(
        player=player_bot_to_test,
        competitors=[
            awasomeBot(
            ), tba_old()
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
