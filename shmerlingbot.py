from random import choice, random, randrange
from typing import Iterable, List, Tuple
from xmlrpc.client import Boolean

import pandas as pd

from baseline_bot import AttackEnemyWeakestPlanetFromStrongestBot, get_random_map
# from awasomeBot import awasomeBot
# from Wookies import Wookies
from planet_wars.battles.tournament import run_and_view_battle, TestBot
from planet_wars.planet_wars import Player, PlanetWars, Order, Planet
# from moveGenerator import MoveGenerator
# from planetClassifier import PlanetClassifier
# from girlsPower import GirlsPowerlBot


class shmerlingBot(Player):
    """
    Best bot ever
    """

    def __init__(self) -> None:
        super().__init__()
        self.sent_fleets: List[List[Planet, int]] = []

    def get_planets_with_scores(self) -> Tuple[Planet, int]:
        planets: List[Planet] = self.game.planets
        planets_with_scores = []
        for planet in planets:
            ship_score = (3/(planet.num_ships+1))
            planets_with_scores.append((planet, planet.growth_rate+ship_score))
        return planets_with_scores

    def planet_think(self, selfPlanet: Planet, planets_with_scores: Tuple[Planet, int]) -> Planet:
        best_planets = [(planet[0], (planet[1])/(Planet.distance_between_planets(
            selfPlanet, planet[0])+1)) for planet in planets_with_scores if planet[0].owner != self.game.ME]
        if not best_planets:
            return None
        best_planets.sort(key=lambda x: x[1], reverse=True)
        return best_planets

    def random_move(self, planet):
        return Order(planet, choice(self.game.planets),
                     randrange(1, max(planet.num_ships-1, 2)))

    def get_best_move(self, planets_with_scores: Tuple[Planet, int]):
        selfPlanets = self.game.get_planets_by_owner(self.game.ME)

        moves = []
        for i, planet in enumerate(selfPlanets):
            best_planets = self.planet_think(planet, planets_with_scores)

            assaulted_planet_ids = [
                fleet.destination_planet_id for fleet in self.game.get_fleets_by_owner(self.game.ME)]
            if not best_planets or (best_planets[0][0].planet_id in assaulted_planet_ids):
                # moves.append(self.random_move(planet))
                continue
            available_ships = planet.num_ships
            for target_planet in best_planets:
                used_ships = self.get_needed_ships(planet, target_planet[0])
                if used_ships == 0:
                    continue
                moves.append(
                    Order(planet, target_planet[0], used_ships))
                available_ships -= used_ships
                if available_ships < 5:
                    break

        return moves

    def calculate_coming_ships(self, targer_planet: Planet) -> int:
        enemies_fleets = self.game.get_fleets_by_owner(self.game.ENEMY)
        ships_sent = 0
        for fleet in enemies_fleets:
            if fleet.destination_planet_id == targer_planet.planet_id:
                ships_sent += fleet.num_ships
        return ships_sent

    def get_needed_ships(self, self_planet, target_planet: Planet) -> int:
        # if  not enemy : current
        # check if planet is destionation of enemy
        # if enemy : needed = (dist * growth) + current ships

        needed_ships = 0
        if target_planet.owner == self.game.NEUTRAL:
            needed_ships += target_planet.num_ships

        elif target_planet.owner == self.game.ENEMY:
            needed_ships += (target_planet.growth_rate * self_planet.distance_between_planets(
                self_planet, target_planet)) + target_planet.num_ships

        needed_ships += self.calculate_coming_ships(target_planet)
        if self.check_self_targeted(self_planet) == False:
            ships_left = self_planet.num_ships - needed_ships
            if ships_left > 5:
                needed_ships += ships_left - 5
        if needed_ships >= self_planet.num_ships:
            return 0
        return needed_ships + 2

    def check_self_targeted(self, self_planet: Planet):
        enemies_fleets = self.game.get_fleets_by_owner(self.game.ENEMY)
        for fleet in enemies_fleets:
            if fleet.destination_planet_id == self_planet.planet_id:
                return True
        return False

    def play_turn(self, game: PlanetWars) -> Iterable[Order]:
        """
        See player.play_turn documentation.
        :param game: PlanetWars object representing the map - use it to fetch all the planets and flees in the map.
        :return: List of orders to execute, each order sends ship from a planet I own to other planet.
        """
        self.game = game

        if len(game.get_fleets_by_owner(game.ME)) > 2:
            return []

        return self.get_best_move(self.get_planets_with_scores())


def view_bots_battle():
    """
    Runs a battle and show the results in the Java viewer

    Note: The viewer can only open one battle at a time - so before viewing new battle close the window of the
    previous one.
    Requirements: Java should be installed on your device.
    """
    map_str = get_random_map()
    run_and_view_battle(shmerlingBot(
    ), Wookies(), map_str)


def check_bot():
    """
    Test AttackWeakestPlanetFromStrongestBot against the 2 other bots.
    Print the battle results data frame and the PlayerScore object of the tested bot.
    So is AttackWeakestPlanetFromStrongestBot worse than the 2 other bots? The answer might surprise you.
    """
    maps = [get_random_map() for i in range(10)]
    player_bot_to_test = shmerlingBot()
    tester = TestBot(
        player=player_bot_to_test,
        competitors=[
            AttackEnemyWeakestPlanetFromStrongestBot(
            ), shmerlingBot(), # Wookies()
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