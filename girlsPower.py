from typing import Iterable, List
import pandas as pd

from baseline_bot import AttackWeakestPlanetFromStrongestBot, AttackEnemyWeakestPlanetFromStrongestBot, \
    AttackWeakestPlanetFromStrongestSmarterNumOfShipsBot, get_random_map
from planet_wars.battles.tournament import run_and_view_battle, TestBot
from planet_wars.planet_wars import Player, PlanetWars, Order, Planet


class GirlsPowerlBot(Player):
    """
    Implement here your smart logic.
    Rename the class and the module to your team name
    """
    first_middle_plant = None


    def get_planets_to_attack(self, game: PlanetWars) -> List[Planet]:
        """
        :param game: PlanetWars object representing the map
        :return: The planets we need to attack
        """
        return [p for p in game.planets if p.owner != PlanetWars.ME]

    def ships_to_send_in_a_flee(self, source_planet: Planet, dest_planet: Planet) -> int:
        return source_planet.num_ships * 0.8

    def play_turn(self, game: PlanetWars) -> Iterable[Order]:
        """
        See player.play_turn documentation.
        :param game: PlanetWars object representing the map - use it to fetch all the planets and flees in the map.
        :return: List of orders to execute, each order sends ship from a planet I own to other planet.
        """
        # (1) Get all planets owners.
        enemy_planets = game.get_planets_by_owner(owner=PlanetWars.ENEMY)
        my_planets = game.get_planets_by_owner(owner=PlanetWars.ME)
        neutral_planets = game.get_planets_by_owner(owner=PlanetWars.NEUTRAL)

        # (2) Check if i have planets.
        if len(my_planets) == 0:
            return []

        # (3) If we currently have a 3 fleets in flight, just do nothing.
        if len(game.get_fleets_by_owner(owner=PlanetWars.ME)) >= 3:
            return []

        # (4) Find my strongest planet.
        my_strongest_planet = max(
            my_planets, key=lambda planet: planet.num_ships)

        # (5) Find the middle planet.
        planets = [(planet.x + planet.y, planet) for planet in neutral_planets]
        planets.sort(key=lambda x: x[0], reverse=False)
        # print(planets[0])
        
        if(game.turns == 0):
            self.first_middle_plant = planets[0][1]

        print(self.first_middle_plant)

        # (6) Find the neutral planets.
        planets_to_attack = neutral_planets
        if len(neutral_planets) == 0:
            return []
        neutral_weakest_planet = min(
            planets_to_attack, key=lambda planet: planet.num_ships)

        # (7) Send 80% of the ships from my strongest planet to the weakest planet that I do not own.
        # if(first_middle_plant.owner == owner=PlanetWars.ME):
        #     return [Order(
        #     my_strongest_planet,
        #     neutral_weakest_planet,
        #     self.ships_to_send_in_a_flee(
        #         my_strongest_planet, neutral_weakest_planet)
        # )]
        # else:
        return [Order(
            my_strongest_planet,
            neutral_weakest_planet,
            self.ships_to_send_in_a_flee(
                my_strongest_planet, neutral_weakest_planet)
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
    ), GirlsPowerlBot(), map_str)


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

    # To view battle number 4 uncomment the line below
    # tester.view_battle(4)


if __name__ == "__main__":
    # check_bot()
    view_bots_battle()
