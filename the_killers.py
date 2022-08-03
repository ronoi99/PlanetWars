from operator import index
from typing import Iterable
from typing import Iterable, List
import pandas as pd

from baseline_bot import AttackWeakestPlanetFromStrongestBot, AttackEnemyWeakestPlanetFromStrongestBot, \
    AttackWeakestPlanetFromStrongestSmarterNumOfShipsBot, get_random_map
from planet_wars.battles.tournament import run_and_view_battle, TestBot
from planet_wars.planet_wars import Player, PlanetWars, Order, Planet


class the_killers(Player):
    """
    Implement here your smart logic.
    Rename the class and the module to your team name
    """
    index = 1 

    def play_turn(self, game: PlanetWars) -> Iterable[Order]:
        if self.index % 2 == 0:
            self.index+=1
            return self.weakest_enemy_move(game)
        else:
            self.index+=1
            return self.neutral_move(game)

        

    def neutral_move(self, game: PlanetWars) -> Iterable[Order]:
        """
        See player.play_turn documentation.
        :param game: PlanetWars object representing the map - use it to fetch all the planets and flees in the map.
        :return: List of orders to execute, each order sends ship from a planet I own to other planet.
        """
        how_much_to_attack = 0
        my_planets = game.get_planets_by_owner(owner=PlanetWars.ME)
        weakes_neutral = self.get_weakest_plant(game.get_planets_by_owner(owner=PlanetWars.NEUTRAL))
        if len(my_planets) == 0:
            return []
        elif len(my_planets) == 1:
            how_much_to_attack =  self.ships_to_send_in_a_flee_to_netural(my_planets[0],weakes_neutral)
            return [Order(
            my_planets[0],
            weakes_neutral,
            how_much_to_attack
        )]
        else: 
            my_planets.sort(key=lambda planet: planet.num_ships)   
            how_much_to_attack =  self.ships_to_send_in_a_flee_to_netural(my_planets[-2],weakes_neutral)
        
        return [Order(
            my_planets[-2],
            weakes_neutral,
            how_much_to_attack
        )]

    def weakest_enemy_move(self, game: PlanetWars) -> Iterable[Order]:
        """
        See player.play_turn documentation.
        :param game: PlanetWars object representing the map - use it to fetch all the planets and flees in the map.
        :return: List of orders to execute, each order sends ship from a planet I own to other planet.
        """
        how_much_to_attack = 0
        my_planets = game.get_planets_by_owner(owner=PlanetWars.ME)
        weakes_enemy = self.get_weakest_plant(game.get_planets_by_owner(owner=PlanetWars.ENEMY))
        
        if len(my_planets) == 0:
            return []
        #elif len(my_planets) == 1:
            #defense
        else: 
            how_much_to_attack =  self.ships_to_send_in_a_flee_to_enemy(my_planets[0],weakes_enemy)
        
        return [Order(
            my_planets[0],
            weakes_enemy,
            how_much_to_attack
        )]        

    def ships_to_send_in_a_flee_to_netural(self, source_planet: Planet, dest_planet: Planet) -> int:
            original_num_of_ships = int(source_planet.num_ships * 0.6)
            if dest_planet.num_ships < original_num_of_ships:
                return dest_planet.num_ships + 5
            return 0
            # if dest_planet.owner == PlanetWars.ENEMY:
            #     return int(source_planet.num_ships * 0.75)
            # return original_num_of_ships

    def ships_to_send_in_a_flee_to_enemy(self, source_planet: Planet, dest_planet: Planet) -> int:
            # original_num_of_ships = int(source_planet.num_ships * 0.6)
            # if dest_planet.num_ships < original_num_of_ships:
                return int(source_planet.num_ships * 0.5) 

#Planet.distance_between_planets()
    
    def get_netural_plants(self, game: PlanetWars):
        """
        :param game: PlanetWars object representing the map
        :return: The planets we need to attack - attack only enemy's planets
        """
        return game.get_planets_by_owner(owner=PlanetWars.NEUTRAL)

    def get_enemy_plants(self, game: PlanetWars):
        """
        :param game: PlanetWars object representing the map
        :return: The planets we need to attack - attack only enemy's planets
        """
        return game.get_planets_by_owner(owner=PlanetWars.ENEMY)

    def get_weakest_plant(self, plants: List[Planet]):
            """
            :param game: PlanetWars object representing the map
            :return: The planets we need to attack - attack only enemy's planets
            """

            return min(plants, key=lambda planet: planet.num_ships)

def view_bots_battle():
    """
    Runs a battle and show the results in the Java viewer

    Note: The viewer can only open one battle at a time - so before viewing new battle close the window of the
    previous one.
    Requirements: Java should be installed on your device.
    """
    map_str = get_random_map()
    run_and_view_battle(the_killers(), AttackEnemyWeakestPlanetFromStrongestBot(), map_str)


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
