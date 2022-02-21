import math
from typing import Iterable

import pandas as pd
from typing import Iterable, List

from zmq import EVENT_CLOSED
from baseline_bot import AttackWeakestPlanetFromStrongestBot, AttackEnemyWeakestPlanetFromStrongestBot, \
    AttackWeakestPlanetFromStrongestSmarterNumOfShipsBot, get_random_map
from planet_wars.battles.tournament import run_and_view_battle, TestBot
from planet_wars.planet_wars import Fleet, Player, PlanetWars, Order, Planet


class The_average_group(Player):
    """
    Implement here your smart logic.
    Rename the class and the module to your team name
    """
    def Biggest_owned_star(self, game: PlanetWars) -> Planet:
        counts_of_ships = 0
        returned_planet = Planet
        for p in game.planets:
            if (p.owner == PlanetWars.ME):
                if(counts_of_ships < p.num_ships):
                    counts_of_ships = p.num_ships
                    returned_planet = p
        return returned_planet  
    
    def distance_stars(self, game: PlanetWars):
            """
            Checks who is the 5 closest stars to our current stars
            return list of planets
            """
            Current_star = self.Biggest_owned_star(game)
            list_dis_planet = []
            for p in game.planets:
                distance = math.sqrt(pow(Current_star.x-p.x,2)+pow(Current_star.y-p.y,2))
                list_dis_planet.append({"Planet": p,
                                        "Distance":distance})
            list_dis_planet = sorted(list_dis_planet,key=lambda x:x["Distance"])
            return list_dis_planet

    def five_not_owned_closest_stars(self, game: PlanetWars):
        list_all_star = self.distance_stars(game)
        list_not_owned =[]
        for p in list_all_star:
            if p["Planet"].owner != PlanetWars.ME:
                list_not_owned.append({"Planet":p["Planet"],"Distance":p["Distance"]})
        return list_not_owned

    def owned_attacked_planets(self,game:PlanetWars) -> List[Planet]:
        list_planet = []
        for p in game.planets:
            for f in game.fleets:
                if(p.owner == PlanetWars.ME) and (f.destination_planet_id == p.planet_id) and (f.owner != 1):
                    list_planet.append({"Planet":p,"Fleet":f})
        return list_planet

    def defence_stars(self,game:PlanetWars):
        #if defence is possible:
        for p in self.owned_attacked_planets(PlanetWars):
            total_defence = p["Planet"].num_ships + (p["Planet"].growth_rate * p["Fleet"].turns_remaining)
            if (total_defence > p["Fleet"].num_ships):
                pass
        #if can't survived the attack then attack another planet

        

    def play_turn(self, game: PlanetWars) -> Iterable[Order]:
        """
        See player.play_turn documentation.
        :param game: PlanetWars object representing the map - use it to fetch all the planets and flees in the map.
        :return: List of orders to execute, each order sends ship from a planet I own to other planet.
        """
        pot_attack = self.five_not_owned_closest_stars(game)
        attack_list =[]
        for p in pot_attack:
            check = int(math.ceil((p["Distance"])*p["Planet"].growth_rate)+p["Planet"].num_ships)
            if self.Biggest_owned_star(game).num_ships > p["Planet"].num_ships:
                if p["Planet"].owner == 0:
                    attack_list.append(Order(self.Biggest_owned_star(game),p["Planet"],p["Planet"].num_ships+1))
                elif check < self.Biggest_owned_star(game).num_ships:
                    attack_list.append(Order(self.Biggest_owned_star(game),p["Planet"],check+2))
        return attack_list




            
def view_bots_battle():
    """
    Runs a battle and show the results in the Java viewer

    Note: The viewer can only open one battle at a time - so before viewing new battle close the window of the
    previous one.
    Requirements: Java should be installed on your device.
    """
    map_str = get_random_map()
    run_and_view_battle(The_average_group(), AttackWeakestPlanetFromStrongestSmarterNumOfShipsBot(), map_str)


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
