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
    first_middle_planet = None
    nearest_neutral_planet = None
    nearest_enemy_planet = None

    def get_planets_to_attack(self, game: PlanetWars) -> List[Planet]:
        """
        :param game: PlanetWars object representing the map
        :return: The planets we need to attack
        """
        return [p for p in game.planets if p.owner != PlanetWars.ME]

    def ships_to_send_in_a_flee(self, source_planet: Planet, dest_planet: Planet) -> int:
        return source_planet.num_ships // 1.5

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

        orders = []

        # (2) Check if i have planets.
        if len(my_planets) == 0:
            return orders

        # (3) If we currently have a 3 fleets in flight, just do nothing.
        # if len(game.get_fleets_by_owner(owner=PlanetWars.ME)) >= 15:
        #     return orders

        # (4) Find my strongest planet.
        my_strongest_planet = max(
            my_planets, key=lambda planet: planet.num_ships)

        # (5) Find the middle planet.
        if(game.turns == 0):
            enemy_planet = enemy_planets[0]
            my_planet = my_planets[0]
            midx, midy = abs(enemy_planet.x+my_planet.x) / \
                2, abs(enemy_planet.y+my_planet.y)/2
            planets = [(abs(planet.x-midx) + abs(planet.y-midy), planet)
                       for planet in neutral_planets]
            planets.sort(key=lambda x: x[0], reverse=False)
            self.first_middle_planet = planets[0][1]

        # (6) Find the weakest neutral planets.
        planets_to_attack = neutral_planets
        if len(planets_to_attack) > 0:
            neutral_weakest_planet = min(
                planets_to_attack, key=lambda planet: planet.num_ships)

        # (7) Send 80% of the ships from my strongest planet to the middle planet or the weakest neutral planet.
        if(self.first_middle_planet.growth_rate >= 3 and self.first_middle_planet.num_ships <= 0.8*(my_strongest_planet.num_ships)):
            return [Order(
                my_strongest_planet,
                self.first_middle_planet,
                self.ships_to_send_in_a_flee(
                    my_strongest_planet, self.first_middle_planet)
            )]

        big_growth_neutral_planets = []
        for neutral_planet in neutral_planets:
            if neutral_planet.growth_rate >= 3:
                big_growth_neutral_planets.append(neutral_planet)

        if len(big_growth_neutral_planets) > 0:
            nearest_neutral_planet = min(
            big_growth_neutral_planets, key=lambda planet: Planet.distance_between_planets(my_strongest_planet, planet))

        if self.nearest_neutral_planet != None:
            return [Order(
                my_strongest_planet,
                self.nearest_neutral_planet,
                self.ships_to_send_in_a_flee(
                    my_strongest_planet, nearest_neutral_planet)
            )]

        big_growth_enemy_planets = []
        for enemy_planet in enemy_planets:
            if enemy_planet.growth_rate >= 3:
                big_growth_enemy_planets.append(enemy_planet)

        if len(big_growth_enemy_planets) > 0:
            nearest_enemy_planet = min(
            big_growth_enemy_planets, key=lambda planet: Planet.distance_between_planets(my_strongest_planet, planet))


        if(game.turns > 0):
            if self.nearest_enemy_planet != None:
                return [Order(
                    my_strongest_planet,
                    self.nearest_enemy_planet,
                    self.ships_to_send_in_a_flee(
                        my_strongest_planet, nearest_enemy_planet)
                )]

            if neutral_planets != None:
                return [Order(
                    my_strongest_planet,
                    neutral_planets,
                    self.ships_to_send_in_a_flee(
                        my_strongest_planet, neutral_planets)
                )]

        return orders


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
    player_bot_to_test = GirlsPowerlBot()
    tester = TestBot(
        player=player_bot_to_test,
        competitors=[
            AttackEnemyWeakestPlanetFromStrongestBot(
            ), AttackWeakestPlanetFromStrongestBot()
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
