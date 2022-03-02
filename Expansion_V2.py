
from fileinput import close
from typing import Iterable
import math as mt
import pandas as pd

from baseline_bot import AttackWeakestPlanetFromStrongestBot, AttackEnemyWeakestPlanetFromStrongestBot, \
    AttackWeakestPlanetFromStrongestSmarterNumOfShipsBot, get_random_map
from planet_wars.battles.tournament import run_and_view_battle, TestBot
from planet_wars.planet_wars import Player, PlanetWars, Order, Planet

import TheTerminator
import SOYsauce

class Expansion_V2(Player):
    """
    Implement here your smart logic.
    Rename the class and the module to your team name
    """
    #Daniel Levin Shoham Houta Idan Tal
    def play_turn(self, game: PlanetWars) -> Iterable[Order]:
        """
        See player.play_turn documentation.
        :param game: PlanetWars object representing the map - use it to fetch all the planets and flees in the map.
        :return: List of orders to execute, each order sends ship from a planet I own to other planet.
        """
        # TODO IMPLEMENT HERE YOUR SMART LOGIC
        orders = []
        pln = game.get_planets_by_owner(1)
        for p in pln:
            myFleets = game.get_fleets_by_owner(1)
            neutralPlanets = game.get_planets_by_owner(0)
            neutralPlanets.sort(key=lambda planet: planet.growth_rate, reverse=True)
            orders=[]
            myPlanets = game.get_planets_by_owner(1)
            if (neutralPlanets and myPlanets and game.turns < 5):
                for p in neutralPlanets:
                    if (p.growth_rate!=0):
                        neutralPlanets = game.get_planets_by_owner(0)
                        neutralPlanets.sort(key=lambda planet: planet.growth_rate, reverse=True)
                        myPlanets = game.get_planets_by_owner(1)
                        myPlanets.sort(key=lambda planet: (planet.distance_between_planets(planet, p)))
                        orders.append(Order(
                        int(myPlanets[0].planet_id),
                        p.planet_id,
                        p.num_ships + 1
                ))
                
            enemyPlanets = game.get_planets_by_owner(2)
            enemyPlanets.sort(key=lambda planet: planet.num_ships, reverse=True)
            myPlanets2 = game.get_planets_by_owner(1)
            if (game.turns>20 and myPlanets2 and enemyPlanets):
                for p in enemyPlanets:
                    enemyPlanets = game.get_fleets_by_owner(2)
                    enemyPlanets.sort(key=lambda planet: planet.num_ships, reverse=True)
                    myPlanets2 = game.get_planets_by_owner(1)
                    myPlanets2.sort(key=lambda planet: (planet.distance_between_planets(planet, p)))
                    orders.append(Order(
                    int(myPlanets2[0].planet_id),
                    p.planet_id,
                    p.num_ships + 15 #to do: turn calculation
                ))
                
            myPlanets3=game.get_planets_by_owner(1)
            enemyPlanets2 = game.get_planets_by_owner(2)
            if (enemyPlanets2 and myPlanets3):
                enem_weakest = min(enemyPlanets2, key=lambda planet: planet.num_ships)
                if (game.turns>20):
                    for p in myPlanets3:
                        if p.num_ships > 200:
                            orders.append(Order(
                            int(p.planet_id),
                            enem_weakest.planet_id,
                            150 #to do: turn calculation
                    ))

            enFleets = game.get_fleets_by_owner(2)
            myPlanets3 = game.get_planets_by_owner(1)
            if (enFleets and myPlanets3):
                for fleet in enFleets:
                    myPlanets3 = game.get_planets_by_owner(1)
                    myPlanets3.sort(key=lambda planet: (planet.distance_between_planets(planet, game.get_planet_by_id(fleet.destination_planet_id))))
                    orders.append(Order(
                    int(myPlanets3[0].planet_id),
                    fleet.destination_planet_id,
                    fleet.num_ships+1 #to do: turn calculation
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
    #run_and_view_battle(TheTerminator.TheTerminator(), Expansion_V2(), map_str)
    run_and_view_battle(SOYsauce.SOYsauce(), Expansion_V2(), map_str)


def check_bot():
    """
    Test AttackWeakestPlanetFromStrongestBot against the 2 other bots.
    Print the battle results data frame and the PlayerScore object of the tested bot.
    So is AttackWeakestPlanetFromStrongestBot worse than the 2 other bots? The answer might surprise you.
    """
    maps = [get_random_map(), get_random_map()]
    player_bot_to_test = Expansion_V2()
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
    #check_bot()
    view_bots_battle()