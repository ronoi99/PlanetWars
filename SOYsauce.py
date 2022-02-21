from typing import Iterable,List

import pandas as pd

from baseline_bot import AttackWeakestPlanetFromStrongestBot, AttackEnemyWeakestPlanetFromStrongestBot, \
    AttackWeakestPlanetFromStrongestSmarterNumOfShipsBot, get_random_map
from planet_wars.battles.tournament import run_and_view_battle, TestBot
from planet_wars.planet_wars import Player, PlanetWars, Order, Planet


class SOYsauce(Player):
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
        growth = dest_planet.growth_rate
        distance = dest_planet.distance_between_planets(source_planet, dest_planet)
        # print(growth, distance)
        if dest_planet.owner == PlanetWars.NEUTRAL:
            return (dest_planet.num_ships + 6)
        else:
            return (dest_planet.num_ships + growth * distance + 5)
    # def choose_planet(planets_to_attack: List[Planet]) -> Planet:
    #     """
    #     :param planets_to_attack: List of planets to attack
    #     :return: The planet to attack
    #     """
    #     print(planets_to_attack)
    #     return random.choice(planets_to_attack)


    def play_turn(self, game: PlanetWars) -> Iterable[Order]:
        """
        See player.play_turn documentation.
        :param game: PlanetWars object representing the map - use it to fetch all the planets and flees in the map.
        :return: List of orders to execute, each order sends ship from a planet I own to other planet.
        """
        # # (1) If we currently have a fleet in flight, just do nothing.
        # if len(game.get_fleets_by_owner(owner=PlanetWars.ME)) >= 1:
        #     return []

        # (2) Find my strongest planet.
        my_planets = game.get_planets_by_owner(owner=PlanetWars.ME)
        if len(my_planets) == 0:
            return []
        my_strongest_planet = max(my_planets, key=lambda planet: planet.num_ships)

        # (3) Find the weakest enemy or neutral planet.
        planets_to_attack = self.get_planets_to_attack(game)
        if len(planets_to_attack) == 0:
            return []
        #self.choose_planet(planets_to_attack)
        
        chosen = planets_to_attack[0]
        chosen.score = (chosen.num_ships/(chosen.growth_rate+0.1)) + chosen.distance_between_planets(my_strongest_planet, chosen)
        #chosen.num_ships / (chosen.growth_rate + .5)+ (chosen.distance_between_planets(my_strongest_planet, chosen)/.5)
        for p in planets_to_attack:
            p.score = (p.num_ships/(p.growth_rate+0.1)) + p.distance_between_planets(my_strongest_planet, p)
            if p.score < chosen.score:
                for y in game.get_fleets_by_owner(owner=PlanetWars.ME):
                 if y.destination_planet_id != p.planet_id:
                     chosen=p

        
        # enemy_or_neutral_weakest_planet = min(planets_to_attack, key=lambda planet: planet.num_ships)

        # (4) Send half the ships from my strongest planet to the weakest planet that I do not own.
        return [Order(
            my_strongest_planet,
            chosen,
            self.ships_to_send_in_a_flee(my_strongest_planet, chosen)
        )]


def view_bots_battle():
    """
    Runs a battle and show the results in the Java viewer

    Note: The viewer can only open one battle at a time - so before viewing new battle close the window of the
    previous one.
    Requirements: Java should be installed on your device.
    """
    map_str = get_random_map()
    run_and_view_battle(AttackWeakestPlanetFromStrongestBot(), AttackEnemyWeakestPlanetFromStrongestBot(), map_str)


def check_bot():
    """
    Test AttackWeakestPlanetFromStrongestBot against the 2 other bots.
    Print the battle results data frame and the PlayerScore object of the tested bot.
    So is AttackWeakestPlanetFromStrongestBot worse than the 2 other bots? The answer might surprise you.
    """
    maps = [get_random_map(), get_random_map()]
    player_bot_to_test = SOYsauce()
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
    check_bot()
    view_bots_battle()
