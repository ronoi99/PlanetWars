from dis import dis
from typing import Iterable, List, Tuple

import pandas as pd

from baseline_bot import AttackWeakestPlanetFromStrongestBot, AttackEnemyWeakestPlanetFromStrongestBot, \
    AttackWeakestPlanetFromStrongestSmarterNumOfShipsBot, get_random_map
from planet_wars.battles.tournament import run_and_view_battle, TestBot
from planet_wars.planet_wars import Player, PlanetWars, Order, Planet


class Rust_react_gulp(Player):
    """
    Implement here your smart logic.
    Rename the class and the module to your team name
    """
    MIN_SHIPS_ON_PLANET = 15

    def eval_planet(self, game: PlanetWars, home_planet: Planet, planet: Planet, turns_ahead, attack_radius):
        distance = planet.distance_between_planets(
            planet, home_planet)
        if (distance < attack_radius and planet.owner != game.ME):
            eval = (turns_ahead - (distance)) * \
                planet.growth_rate - planet.num_ships
        else:
            eval = -1000
        return (planet, eval)

    def initial_turn(self, game: PlanetWars, orders):
        home_planet = 0
        for planet in game.planets:
            if (planet.owner == game.ME and planet.num_ships > 50):
                home_planet = planet

                planets_in_d_10 = 0
                for planet in game.planets:
                    if (planet.distance_between_planets(home_planet, planet) <= 10):
                        planets_in_d_10 += 1

                planets_in_d_15 = 0
                if (planets_in_d_10 < 3):
                    for planet in game.planets:
                        if (planet.distance_between_planets(home_planet, planet) <= 15):
                            planets_in_d_15 += 1

                attack_radius = 0
                if (planets_in_d_10 > 3):
                    attack_radius = 11
                elif (planets_in_d_15 > 3):
                    attack_radius = 16
                else:
                    attack_radius = 50

                SHIPS_TO_INVEST = 50
                planet_evaluation_unsorted = list(map(
                    lambda planet: self.eval_planet(game, home_planet, planet, 20, attack_radius), game.planets))

                planet_evaluation_sorted = sorted(
                    planet_evaluation_unsorted, key=lambda x: x[1], reverse=True)

                for planet_eval in planet_evaluation_sorted:
                    ships_to_send = planet_eval[0].num_ships + 5
                    if (planet_eval[1] < 0):
                        continue
                    if (ships_to_send <= SHIPS_TO_INVEST):
                        new_fleet = Order(home_planet.planet_id,
                                          planet_eval[0].planet_id, ships_to_send)
                        SHIPS_TO_INVEST -= ships_to_send
                        orders.append(new_fleet)

    def defenece(self, game: PlanetWars, orders):
        for fleet in game.fleets:
            dest_planet = game.get_planet_by_id(fleet.destination_planet_id)
            # print(str(game.turns) + " Fleet Owner " + str("ME" if fleet.owner == game.ME else "His") +
            #       " Dest Planet Owner " + str("ME" if dest_planet.owner == game.ME else "His"))
            if (fleet.owner == game.ENEMY and dest_planet.owner == game.ME and fleet.total_trip_length == fleet.turns_remaining):
                ships_on_attacked_planet = dest_planet.num_ships + \
                    dest_planet.growth_rate * fleet.turns_remaining
                if (fleet.num_ships > ships_on_attacked_planet):
                    help_amount = fleet.num_ships - ships_on_attacked_planet
                    # SEND HELP IF POSSIBLE
                    for planet in game.planets:
                        if (planet.num_ships > help_amount + self.MIN_SHIPS_ON_PLANET):
                            new_order = Order(
                                planet, dest_planet, help_amount + 1)
                            orders.append(new_order)
                            break

    def play_turn(self, game: PlanetWars) -> Iterable[Order]:
        """
        See player.play_turn documentation.
        :param game: PlanetWars object representing the map - use it to fetch all the planets and flees in the map.
        :return: List of orders to execute, each order sends ship from a planet I own to other planet.
        """
        # TODO IMPLEMENT HERE YOUR SMART LOGIC
        # First turn spread

        orders = []

        if (game.turns % 10 == 0):
            self.initial_turn(game, orders)

        self.defenece(game, orders)

        return orders


def view_bots_battle():
    """
    Runs a battle and show the results in the Java viewer


    Note: The viewer can only open one battle at a time - so before viewing new battle close the window of the
    previous one.
    Requirements: Java should be installed on your device.
    """
    map_str = get_random_map()
    run_and_view_battle(Rust_react_gulp(
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
            AttackEnemyWeakestPlanetFromStrongestBot(
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
    tester.view_battle(4)


if __name__ == "__main__":
    # check_bot()
    view_bots_battle()
