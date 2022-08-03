from math import gamma
from typing import Iterable, List, Tuple

import pandas as pd
from Kvutza6 import Kvutza6
from FireflyZ import FireflyZ_Bot
from girlsPower import GirlsPowerlBot
# from rust_react_gulp import Rust_react_gulp
# from the_killers import the_killers
# from shmerlingBot import shmerlingBot

from baseline_bot import AttackWeakestPlanetFromStrongestBot, AttackEnemyWeakestPlanetFromStrongestBot, \
    AttackWeakestPlanetFromStrongestSmarterNumOfShipsBot, get_random_map
from planet_wars.battles.tournament import run_and_view_battle, TestBot
from planet_wars.planet_wars import Player, PlanetWars, Order, Planet
# from shmerlingBot import shmerlingBot


class awasomeBot(Player):
    """
    Implement here your smart logic.
    Rename the class and the module to your team name
    """
    def __init__(self) -> None:
        super().__init__()
    def get_all_non_mine_planets(self,game:PlanetWars):
        all_planets = game.get_planets_by_owner(PlanetWars.NEUTRAL)
        enemy_planets = game.get_planets_by_owner(PlanetWars.ENEMY)
        for p in enemy_planets:
            all_planets.append(p)
        return all_planets
    
    def get_all_positive_groth_planets(self,game:PlanetWars) -> List[Planet]:
        all_planets = self.get_all_non_mine_planets(game)
        positive_planets = []
        for planet in all_planets:
            if(planet.growth_rate > 2):
                positive_planets.append(planet)
        if(len(positive_planets) ==0): return all_planets
        return positive_planets
            
    def get_closest_planet(self,game:PlanetWars,my_planet:Planet, list_of_planets: List[Planet]):
        if(len(list_of_planets) == 0):
            return []
        closest_planet = list_of_planets[0]
        for p in list_of_planets:
            distance = Planet.distance_between_planets(p,my_planet)
            closest_planet_distance = Planet.distance_between_planets(my_planet,closest_planet)
            if(distance < closest_planet_distance):
                closest_planet = p
        return closest_planet
    
    def remove_enemy_planets(self,game:PlanetWars,list_of_planets:List[Planet]):
        new_list = []
        for planet in list_of_planets:
            if(planet.owner != game.ENEMY):
                new_list.append(planet)
        return new_list
    
    def bear_poked(self,game:PlanetWars) -> Tuple[List[Planet],Planet,Planet]: 
        NEAR_ALARM = 3
        all_enemy_planets = game.get_planets_by_owner(game.ENEMY)
        all_my_planets = game.get_planets_by_owner(game.ME)
        for ep in all_enemy_planets:
            for mp in all_my_planets:
                if(Planet.distance_between_planets(ep,mp) <= NEAR_ALARM):
                    return [self.get_my_friends(game,mp),mp,ep]
        return []
    
    def get_my_friends(self,game:PlanetWars,planet:Planet):
        all_me_planets = game.get_planets_by_owner(game.ME)
        without_me = []
        if(len(all_me_planets) < 4):
            return []
        for p in all_me_planets:
            if(p.planet_id != planet.planet_id):
                without_me.append(p) 
        return without_me
        
    
    def play_turn(self, game: PlanetWars) -> Iterable[Order]:
        """
        See player.play_turn documentation.
        :param game: PlanetWars object representing the map - use it to fetch all the planets and flees in the map.
        :return: List of orders to execute, each order sends ship from a planet I own to other planet.
        """ 
        orders = []
        my_planets = game.get_planets_by_owner(game.ME)
        all_positive_planets = self.get_all_positive_groth_planets(game)
        if(len(my_planets) == 1):
            all_positive_planets = self.remove_enemy_planets(game,all_positive_planets)
        if(len(my_planets) == 0):
            return []

        bear_poked_list = self.bear_poked(game)
        if(len(bear_poked_list) != 0):
            # print("THe bear got poked!")
            my_friends = []
            if(len(bear_poked_list[0]) != 0):
                my_friends = [bear_poked_list[0][0],bear_poked_list[0][1]]
            me = bear_poked_list[1]
            enemy = bear_poked_list[2]
            total_points = enemy.num_ships + 50
            each_ships = total_points // (len(my_friends)+1)
            for p in my_friends:
                orders.append(Order(p,enemy,each_ships))
            orders.append(Order(me,enemy,each_ships))
        
            
        for mp in my_planets:
            closest_planet = self.get_closest_planet(game,mp,all_positive_planets)
            if(closest_planet != []):
                orders.append(Order(mp,closest_planet,closest_planet.num_ships + 30))
        return orders


def view_bots_battle():
    """
    Runs a battle and show the results in the Java viewer

    Note: The viewer can only open one battle at a time - so before viewing new battle close the window of the
    previous one.
    Requirements: Java should be installed on your device.
    """
    map_str = get_random_map()
    run_and_view_battle(Kvutza6(), awasomeBot(), map_str)


def check_bot():
    """
    Test AttackWeakestPlanetFromStrongestBot against the 2 other bots.
    Print the battle results data frame and the PlayerScore object of the tested bot.
    So is AttackWeakestPlanetFromStrongestBot worse than the 2 other bots? The answer might surprise you.
    """
    maps = [get_random_map(), get_random_map(),get_random_map(),get_random_map(),get_random_map()]
    player_bot_to_test = awasomeBot()
    tester = TestBot(
        player=player_bot_to_test,
        competitors=[
            FireflyZ_Bot(),GirlsPowerlBot(),Rust_react_gulp(),Kvutza6()
        ],
        maps=maps
    )
    tester.run_tournament()

    # for a nicer df printing
    pd.set_option('display.max_columns', 30)
    pd.set_option('expand_frame_repr', False)

    # print(tester.get_testing_results_data_frame())
    # print("\n\n")
    # print(tester.get_score_object())

    # To view battle number 4 uncomment the line below
    # tester.view_battle(4)


if __name__ == "__main__":
    #check_bot()
    view_bots_battle()
