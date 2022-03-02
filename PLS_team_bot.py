from typing import Iterable, List

import pandas as pd
import SOYsauce

from baseline_bot import AttackWeakestPlanetFromStrongestBot, AttackEnemyWeakestPlanetFromStrongestBot, \
    AttackWeakestPlanetFromStrongestSmarterNumOfShipsBot, get_random_map
from planet_wars.battles.tournament import run_and_view_battle, TestBot
from planet_wars.planet_wars import Player, PlanetWars, Order, Planet


class PLS(Player):
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
        if dest_planet.owner == 0:
            return dest_planet.num_ships + 1
        else:
            return (dest_planet.num_ships + dest_planet.growth_rate*Planet.distance_between_planets(source_planet, dest_planet) + 1)
    
    def ships_to_send_in_a_flee_2(self, source_planet: Planet, dest_planet: Planet, num_planets: list) -> int:
        if dest_planet.owner == 0:
            return dest_planet.num_ships + 1
        else:
            return ((dest_planet.num_ships/ len(num_planets)) + dest_planet.growth_rate*Planet.distance_between_planets(source_planet, dest_planet) + 1)


    def closest_Planet(self, game, destination_planet: Planet):
        """find the closest planets"""
        closest_id = Planet
        closest_d = 200
        for i in self.get_planets_to_attack(game):
            if i.growth_rate > 3:
                star = Planet.distance_between_planets(i,destination_planet)
                if star < closest_d:
                    closest_d = star
                    closest_id = i
            else:
                continue
        return closest_id
    
    def weakest_enemy_planet(self, game: PlanetWars):
        planets_to_attack = self.get_planets_to_attack(game)
        enemyp = game.get_planets_by_owner(2)
        enemypover3 = []
        for i in enemyp:
            if i.growth_rate > 2:
                enemypover3.append(i)
        if len(enemypover3) > 0:
            return min(enemypover3, key=lambda planet: planet.num_ships)
        else:
            return min(enemyp, key=lambda planet: planet.num_ships)

    

    def play_turn(self, game: PlanetWars) -> Iterable[Order]:
        """
        See player.play_turn documentation.
        :param game: PlanetWars object representing the map - use it to fetch all the planets and flees in the map.
        :return: List of orders to execute, each order sends ship from a planet I own to other planet.
        """
        # (1) If we currently have a fleet in flight, just do nothing.
        if len(game.get_fleets_by_owner(owner=PlanetWars.ME)) >= 1:
            return []


        # (2) Find my strongest planet.
        my_planets = game.get_planets_by_owner(owner=PlanetWars.ME)
        if len(my_planets) == 0:
            return []
        my_strongest_planet = max(my_planets, key=lambda planet: planet.num_ships)

        my_ships_sum = 0

        for i in my_planets:
            my_ships_sum += i.num_ships
        weakest = self.weakest_enemy_planet(game)

        if len(my_planets) < 4 or my_ships_sum < weakest.num_ships:
            return [Order(
                my_strongest_planet,
                self.closest_Planet(game, my_strongest_planet),
                self.ships_to_send_in_a_flee(my_strongest_planet,  self.closest_Planet(game, my_strongest_planet))
            )]
        else:
            orderlist = []
            weakest 
            for i in my_planets:
                i_order = Order(i, weakest, self.ships_to_send_in_a_flee_2(i, weakest, my_planets))
                orderlist.append(i_order)
            return orderlist
        


def view_bots_battle():
    """
    Runs a battle and show the results in the Java viewer

    Note: The viewer can only open one battle at a time - so before viewing new battle close the window of the
    previous one.
    Requirements: Java should be installed on your device.
    """
    map_str = get_random_map()
    #run_and_view_battle(AttackWeakestPlanetFromStrongestBot(), AttackEnemyWeakestPlanetFromStrongestBot(), map_str)
    run_and_view_battle(PLS(), SOYsauce.SOYsauce(), map_str)


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
    view_bots_battle()
