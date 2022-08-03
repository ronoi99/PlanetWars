from random import choice, randint
from typing import Iterable, List, Tuple

import pandas as pd

from baseline_bot import AttackEnemyWeakestPlanetFromStrongestBot, get_random_map
from planet_wars.battles.tournament import run_and_view_battle, TestBot
from planet_wars.planet_wars import Player, PlanetWars, Order, Planet


class PlanetClassifier():
    def __init__(self, game: PlanetWars) -> None:
        self.game = game

    def get_planets_with_scores(self) -> Tuple[Planet, int]:
        planets: List[Planet] = self.game.planets
        planets_with_scores = []
        for planet in planets:
            ship_score = (1/(planet.num_ships+1))*5
            planets_with_scores.append((planet, planet.growth_rate+ship_score))
        return planets_with_scores


class MoveGenerator():
    def __init__(self, game: PlanetWars) -> None:
        self.game = game

    def get_random_move(self):
        selfPlanets = self.game.get_planets_by_owner(self.game.ME)
        allPlanets = self.game.planets
        if not selfPlanets or not allPlanets:
            return []
        myPlanet: Planet = choice(
            selfPlanets)
        return [Order(
                myPlanet,
                choice(allPlanets),
                randint(1, myPlanet.num_ships)
                )]

    def get_best_move(self, planets_with_scores: Tuple[Planet, int]):
        selfPlanets = self.game.get_planets_by_owner(self.game.ME)
        if not selfPlanets:
            return []
        best_attackable_planets = [
            i for i in planets_with_scores if i[0].owner != PlanetWars.ME]
        return [Order(
                myPlanet,
                max(best_attackable_planets, key=lambda x: x[1])[0],
                randint(1, myPlanet.num_ships)
                ) for myPlanet in selfPlanets]


class shmerlingBot(Player):
    """
    Best bot ever
    """

    def play_turn(self, game: PlanetWars) -> Iterable[Order]:
        """
        See player.play_turn documentation.
        :param game: PlanetWars object representing the map - use it to fetch all the planets and flees in the map.
        :return: List of orders to execute, each order sends ship from a planet I own to other planet.
        """
        if len(game.get_fleets_by_owner(game.ME)) > 2:
            return []
        planetClassifier = PlanetClassifier(game)
        moveGenerator = MoveGenerator(game)
        return moveGenerator.get_best_move(planetClassifier.get_planets_with_scores())


def view_bots_battle():
    """
    Runs a battle and show the results in the Java viewer

    Note: The viewer can only open one battle at a time - so before viewing new battle close the window of the
    previous one.
    Requirements: Java should be installed on your device.
    """
    map_str = get_random_map()
    run_and_view_battle(shmerlingBot(
    ), AttackEnemyWeakestPlanetFromStrongestBot(), map_str)


def check_bot():
    """
    Test AttackWeakestPlanetFromStrongestBot against the 2 other bots.
    Print the battle results data frame and the PlayerScore object of the tested bot.
    So is AttackWeakestPlanetFromStrongestBot worse than the 2 other bots? The answer might surprise you.
    """
    maps = [get_random_map(), get_random_map()]
    player_bot_to_test = shmerlingBot()
    tester = TestBot(
        player=player_bot_to_test,
        competitors=[
            AttackEnemyWeakestPlanetFromStrongestBot(
            ), shmerlingBot()
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
