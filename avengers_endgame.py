from typing import Iterable

import pandas as pd
from SOYsauce import SOYsauce
from baseline_bot import AttackWeakestPlanetFromStrongestBot, AttackEnemyWeakestPlanetFromStrongestBot, \
    AttackWeakestPlanetFromStrongestSmarterNumOfShipsBot, get_random_map
from planet_wars.battles.tournament import run_and_view_battle, TestBot
from planet_wars.planet_wars import Fleet, Player, PlanetWars, Order, Planet


class avengers_endgame(Player):
    """
    Implement here your smart logic.
    Rename the class and the module to your team name
    """

    def ships_to_send_in_a_flee(self, source_planet: Planet, dest_planet: Planet) -> int:
        if source_planet.num_ships > 2*dest_planet.num_ships:
            return source_planet.num_ships // 2
        return dest_planet.num_ships + 1
        
    def ships_to_send_in_attack(self, source_planet: Planet, dest_planet: Planet) -> int:
            return(dest_planet.growth_rate * Planet.distance_between_planets(source_planet,dest_planet) + dest_planet.num_ships + 1)


    def play_turn(self, game: PlanetWars) -> Iterable[Order]:
        """
        See player.play_turn documentation.
        :param game: PlanetWars object representing the map - use it to fetch all the planets and flees in the map.
        :return: List of orders to execute, each order sends ship from a planet I own to other planet.
        """
        my_planets = game.get_planets_by_owner(owner=PlanetWars.ME)
        if len(my_planets) == 0:
            return []
        #my_strongest_planet = max(my_planets, key=lambda planet: planet.num_ships)
        strongest_planets=game.get_planets_by_owner(owner=PlanetWars.ME)
        strongest_planets.sort(key= lambda x: x.num_ships,reverse=True)
        neutral_planets = game.get_planets_by_owner(owner=PlanetWars.NEUTRAL)
        enemy_planets = game.get_planets_by_owner(owner=PlanetWars.ENEMY)
        orders_list=[]
        for s in strongest_planets:
            enemy_planets.sort(key= lambda x: Planet.distance_between_planets(s,x))
            neutral_planets.sort(key= lambda x: Planet.distance_between_planets(s,x))
            all_fleets = game.get_fleets_by_owner(owner=PlanetWars.ME)
            #all_enemy_fleets = game.get_fleets_by_owner(owner=PlanetWars.ENEMY)
            for p in neutral_planets:
                if p.num_ships < s.num_ships:
                    num_fleets=0
                    for x in all_fleets:
                        if x.destination_planet_id == p.planet_id:
                            break
                        num_fleets+=1
                    if num_fleets==len(all_fleets):
                            orders_list.append(Order(
                            s,
                            p,
                            self.ships_to_send_in_a_flee(s, p)))
            for p in enemy_planets:
                if self.ships_to_send_in_attack(s, p)<= s.num_ships:
                    num_fleets=0
                    for x in all_fleets:
                        if x.destination_planet_id == p.planet_id:
                            break
                        num_fleets+=1
                    if num_fleets==len(all_fleets):
                        orders_list.append(Order(
                            s,
                            p,
                            self.ships_to_send_in_attack(s, p)))
        for o in orders_list:
            index = 0
            for my_o in orders_list:
                if my_o.destination_planet_id == o.destination_planet_id:
                    if my_o.num_ships > o.num_ships:
                        orders_list[index]
                index += 1
        return orders_list



            
        
        

        


def view_bots_battle():
    """
    Runs a battle and show the results in the Java viewer

    Note: The viewer can only open one battle at a time - so before viewing new battle close the window of the
    previous one.
    Requirements: Java should be installed on your device.
    """
    map_str = get_random_map()
    run_and_view_battle(avengers_endgame(), SOYsauce(), map_str)


def check_bot():
    """
    Test AttackWeakestPlanetFromStrongestBot against the 2 other bots.
    Print the battle results data frame and the PlayerScore object of the tested bot.
    So is AttackWeakestPlanetFromStrongestBot worse than the 2 other bots? The answer might surprise you.
    """
    maps = [get_random_map(), get_random_map()]
    player_bot_to_test = avengers_endgame()
    tester = TestBot(
        player=player_bot_to_test,
        competitors=[
            cap(),ironman()
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
    #view_bots_battle()
