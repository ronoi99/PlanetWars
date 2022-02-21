from typing import Iterable
from numpy import sort

import pandas as pd
from sqlalchemy import false

from baseline_bot import AttackWeakestPlanetFromStrongestBot, AttackEnemyWeakestPlanetFromStrongestBot, \
    AttackWeakestPlanetFromStrongestSmarterNumOfShipsBot, get_random_map
from planet_wars.battles.tournament import run_and_view_battle, TestBot
from planet_wars.planet_wars import Player, PlanetWars, Order, Planet


class TheTerminator(Player):
    """
    Implement here your smart logic.
    Rename the class and the module to your team name
    """
    def get_closest_neutrals(self, game:PlanetWars) -> Iterable[Order]:
        orders = []
        dis = 99999999999999999
        max_number_ofships = -1
        neutral_to_take = game.get_planets_by_owner(game.NEUTRAL)
        for my_planet in game.get_planets_by_owner(game.ME):
            for neutral_planet in game.get_planets_by_owner(game.NEUTRAL):
                if neutral_planet.distance_between_planets(neutral_planet,my_planet)<dis: 
                    neutral_to_take = neutral_planet
                    dis = neutral_planet.distance_between_planets(neutral_planet,my_planet)
                orders.append(Order(my_planet,neutral_to_take,neutral_planet.num_ships+1))
        return orders
    
    def sorted_neutral_byDistance (self,our_planet: Planet, game:PlanetWars) -> Iterable[Planet]:
        planets = game.get_planets_by_owner(game.NEUTRAL)
        distances = lambda a: a.distance_between_planets(our_planet,a)
        planets.sort(key= distances, reverse=False)
        return planets

    def most_profit_from_sorted (self,our_planet: Planet,game:PlanetWars):
        close_neutrals = self.sorted_neutral_byDistance(our_planet,game)
        profit = lambda a: a.growth_rate
        closest_five =[]
        for i in range(5):
              try:
                   closest_five.append(close_neutrals[i])
              except:
                   continue
        try:
            closest_five.sort(key= profit, reverse=True)
            return closest_five[0]
        except:
            return game.get_planets_by_owner(game.ME)[0]

    def weakest_from_sorted (self,our_planet: Planet,game:PlanetWars):
        close_neutrals = self.sorted_neutral_byDistance(our_planet,game)
        weakest = lambda a: a.num_ships
        closest_five =[]
        for i in range(3):
              try:
                   closest_five.append(close_neutrals[i])
              except:
                   continue
        try:
            closest_five.sort(key= weakest, reverse=False)
            return closest_five[0]
        except:
            return game.get_planets_by_owner(game.ME)[0]
    
    
    def dont_attack_nutral_twice (self,planet_to_attack: Planet, game:PlanetWars) -> bool:
        my_attacks = game.get_fleets_by_owner(game.ME)
        for fleet in my_attacks:
            if planet_to_attack.planet_id == fleet.destination_planet_id:
                return False
        return True
    
    def attack_closest_enemy(self, our_planet: Planet ,game:PlanetWars):
        enemy_planets = game.get_planets_by_owner(game.ENEMY)
        distances = lambda a: a.distance_between_planets(our_planet,a)
        enemy_planets.sort(key= distances, reverse=False)
        try:
            return enemy_planets[0]
        except:
            return our_planet



    def play_turn(self, game: PlanetWars) -> Iterable[Order]:
        """
        See player.play_turn documentation.
        :param game: PlanetWars object representing the map - use it to fetch all the planets and flees in the map.
        :return: List of orders to execute, each order sends ship from a planet I own to other planet.
        """
        # TODO IMPLEMENT HERE YOUR SMART LOGIC
        orders = []
        neutral_planets = []
        for my_planet in game.get_planets_by_owner(game.ME):
            planet_to_attack = self.weakest_from_sorted(my_planet,game)
            if self.dont_attack_nutral_twice(planet_to_attack,game) and planet_to_attack.owner != 1:
                orders.append(Order(my_planet,planet_to_attack,planet_to_attack.num_ships+1))
            else:
                enemy = self.attack_closest_enemy(my_planet,game)
                orders.append(Order(my_planet,enemy,my_planet.num_ships-1))

        
        return orders


def view_bots_battle():
    """
    Runs a battle and show the results in the Java viewer

    Note: The viewer can only open one battle at a time - so before viewing new battle close the window of the
    previous one.
    Requirements: Java should be installed on your device.
    """
    map_str = get_random_map()
    run_and_view_battle(TheTerminator(), AttackWeakestPlanetFromStrongestBot(), map_str)


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
            TheTerminator(), AttackWeakestPlanetFromStrongestSmarterNumOfShipsBot()
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
    #check_bot()
    view_bots_battle()
