from fileinput import close
from typing import Iterable
import math as mt
import pandas as pd

from baseline_bot import AttackWeakestPlanetFromStrongestBot, AttackEnemyWeakestPlanetFromStrongestBot, \
    AttackWeakestPlanetFromStrongestSmarterNumOfShipsBot, get_random_map
from planet_wars.battles.tournament import run_and_view_battle, TestBot
from planet_wars.planet_wars import Player, PlanetWars, Order, Planet

def ngetPlanets(self, game: PlanetWars, spec=0): #get planets neutral by default
    return (game.get_planets_by_owner(self, owner=spec))

class Expansion_V1(Player):
    """
    Implement here your smart logic.
    Rename the class and the module to your team name
    """

    def distance(self, dx,dy,sx,sy) -> float:
        return (mt.sqrt((dx-sx)^2 + (dy-sy)^2))

    def ngetPlanets(self, game: PlanetWars, spec=0): #get planets neutral by default
        return (game.get_planets_by_owner(self, owner=spec))
    #Daniel Levin Shoham Houta Idan Tal
    def play_turn(self, game: PlanetWars) -> Iterable[Order]:
        """
        See player.play_turn documentation.
        :param game: PlanetWars object representing the map - use it to fetch all the planets and flees in the map.
        :return: List of orders to execute, each order sends ship from a planet I own to other planet.
        """
        # TODO IMPLEMENT HERE YOUR SMART LOGIC
        
        neutralPlanets = game.get_planets_by_owner(0)
        neutralPlanets.sort(key=lambda planet: planet.growth_rate, reverse=True)
        orders=[]
        if (True):
            for p in neutralPlanets:
                neutralPlanets = game.get_planets_by_owner(0)
                neutralPlanets.sort(key=lambda planet: planet.growth_rate, reverse=True)
                myPlanets = game.get_planets_by_owner(1)
                myPlanets.sort(key=lambda planet: (planet.distance_between_planets(planet, p)))
                orders.append(Order(
                int(myPlanets[-1].planet_id),
                p.planet_id,
                p.num_ships + 1
            ))
            
        enemyPlanets = game.get_planets_by_owner(2)
        enemyPlanets.sort(key=lambda planet: planet.num_ships, reverse=True)
        
        if (game.turns>20):
            for p in enemyPlanets:
                enemyPlanets = game.get_fleets_by_owner(2)
                enemyPlanets.sort(key=lambda planet: planet.num_ships, reverse=True)
                myPlanets2 = game.get_planets_by_owner(1)
                myPlanets2.sort(key=lambda planet: (planet.distance_between_planets(planet, p)))
                orders.append(Order(
                int(myPlanets2[-1].planet_id),
                p.planet_id,
                p.num_ships + 15 #to do: turn calculation
            ))
            
        myPlanets3=game.get_planets_by_owner(1)
        enemyPlanets2 = game.get_planets_by_owner(2)
        if (enemyPlanets2):
            enem_weakest = min(enemyPlanets2, key=lambda planet: planet.num_ships)
            if (game.turns>20):
                for p in myPlanets3:
                    if p.num_ships > 200:
                        orders.append(Order(
                        int(p.planet_id),
                        enem_weakest.planet_id,
                        150 #to do: turn calculation
                ))

        return orders

def view_bots_battle():
    """
    Runs a battle and show the results in the Java viewer

    Note: The viewer can only open one battle at a time - so before viewing new battle close the window of the
    previous one.
    Requirements: Java should be installed on your device.
    """
    map_str = get_random_map()
    run_and_view_battle(AttackWeakestPlanetFromStrongestBot(), Expansion_V1(), map_str)


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
