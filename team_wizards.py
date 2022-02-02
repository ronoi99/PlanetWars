import random
from typing import Iterable, List
from planet_wars.player_bots.baseline_code.baseline_bot import AttackWeakestPlanetFromStrongestBot
from numpy import choose
from runtime_Terror import ETerror
from planet_wars.planet_wars import Player, PlanetWars, Order, Planet
from planet_wars.battles.tournament import get_map_by_id, run_and_view_battle, TestBot

import pandas as pd


class WizardsBot(Player):
    """
    Example of very simple bot - it send flee from its strongest planet to the weakest enemy/neutral planet
    """

    def get_planets_to_attack(self, game: PlanetWars) -> List[Planet]:
        """
        :param game: PlanetWars object representing the map
        :return: The planets we need to attack
        """
        return [p for p in game.planets if (p.owner != PlanetWars.ME) and (p.owner == PlanetWars.NEUTRAL or p.owner == PlanetWars.ENEMY)]

    def ships_to_send_in_a_flee(self, source_planet: Planet, dest_planet: Planet, game) -> int:
        
        
        ships_to_planet = 0
        for f in game.get_fleets_by_owner(owner=PlanetWars.ENEMY):
            if dest_planet.planet_id == f.destination_planet_id:
                ships_to_planet += f.num_ships

        growth = dest_planet.growth_rate
        distance = dest_planet.distance_between_planets(source_planet, dest_planet)
        
        # print(growth, distance)
        if dest_planet.owner == PlanetWars.NEUTRAL:
            return (dest_planet.num_ships + 1 + ships_to_planet)
        else:
            return ((dest_planet.num_ships + growth * distance) + 1 + ships_to_planet)
    # def choose_planet(planets_to_attack: List[Planet]) -> Planet:
    #     """
    #     :param planets_to_attack: List of planets to attack
    #     :return: The planet to attack
    #     """
    #     print(planets_to_attack)
    #     return random.choice(planets_to_attack)


    def play_turn(self, game: PlanetWars) -> Iterable[Order]:
        """
        See player.play_turn documentation.
        :param game: PlanetWars object representing the map - use it to fetch all the planets and flees in the map.
        :return: List of orders to execute, each order sends ship from a planet I own to other planet.
        """
        # # (1) If we currently have a fleet in flight, just do nothing.
        # if len(game.get_fleets_by_owner(owner=PlanetWars.ME)) >= 1:
        #     return []

        # (2) Find my strongest planet.
       
        my_planets = game.get_planets_by_owner(owner=PlanetWars.ME)
        if len(my_planets) == 0:
            return []
        my_strongest_planet = max(my_planets, key=lambda planet: planet.num_ships)

        # (3) Find the weakest enemy or neutral planet.
        planets_to_attack = self.get_planets_to_attack(game)
        if len(planets_to_attack) == 0:
            return []
        # self.choose_planet(planets_to_attack)
        arrayOfPlanetId=[]
        for planetId in game.get_fleets_by_owner(owner=PlanetWars.ME):
            arrayOfPlanetId.append(planetId.destination_planet_id)

        chosen = planets_to_attack[0]
        chosen.score = chosen.num_ships / (chosen.growth_rate + .5)+ (chosen.distance_between_planets(my_strongest_planet, chosen) / .5)
        for p in planets_to_attack:
            if p.planet_id in arrayOfPlanetId:
                continue
                # # if p.planet_id == game.get_fleets_by_owner(owner=PlanetWars.ME)[0].destination_planet_id:
                # print(game.get_fleets_by_owner(owner=PlanetWars.ME)[0].destination_planet_id)
            p.score = p.num_ships / (p.growth_rate + .5)+ p.distance_between_planets(my_strongest_planet, p) / .5

            if p.score < chosen.score:
                chosen = p
        
        # enemy_or_neutral_weakest_planet = min(planets_to_attack, key=lambda planet: planet.num_ships)
#############################################################################################################################
#############################################################################################################################
#############################################################################################################################
#############################################################################################################################
        # (4) Send half the ships from my strongest planet to the weakest planet that I do not own.
        # if game.get_fleets_by_owner(owner=PlanetWars.ME):
        #     print(game.get_fleets_by_owner(owner=PlanetWars.ME)[0].destination_planet_id)
        
        return [Order(
            my_strongest_planet,
            chosen,
            self.ships_to_send_in_a_flee(my_strongest_planet, chosen, game)
        )]


class AttackEnemyWeakestPlanetFromStrongestBot(AttackWeakestPlanetFromStrongestBot):
    """
    Same like AttackWeakestPlanetFromStrongestBot but attacks only enemy planet - not neutral planet.
    The idea is not to "waste" ships on fighting with neutral planets.

    See which bot is better using the function view_bots_battle
    """

    def get_planets_to_attack(self, game: PlanetWars):
        """
        :param game: PlanetWars object representing the map
        :return: The planets we need to attack - attack only enemy's planets
        """
        
        return game.get_planets_by_owner(owner=PlanetWars.NEUTRAL or PlanetWars.ENEMY and not PlanetWars.ME)


class AttackWeakestPlanetFromStrongestSmarterNumOfShipsBot(AttackWeakestPlanetFromStrongestBot):
    """
    Same like AttackWeakestPlanetFromStrongestBot but with smarter flee size.
    If planet is neutral send up to its population + 5
    If it is enemy send most of your ships to fight!

    Will it out preform AttackWeakestPlanetFromStrongestBot? see test_bot function.
    """

    def ships_to_send_in_a_flee(self, source_planet: Planet, dest_planet: Planet) -> int:
        original_num_of_ships = source_planet.num_ships // 2
        if dest_planet.owner == PlanetWars.NEUTRAL:
            if dest_planet.num_ships < original_num_of_ships:
                return dest_planet.num_ships + 5
        if dest_planet.owner == PlanetWars.ENEMY:
            return int(source_planet.num_ships * 0.75)
        return original_num_of_ships


def get_random_map():
    """
    :return: A string of a random map in the maps directory
    """
    random_map_id = random.randrange(1, 100)
    return get_map_by_id(random_map_id)


def view_bots_battle():
    """
    Runs a battle and show the results in the Java viewer

    Note: The viewer can only open one battle at a time - so before viewing new battle close the window of the
    previous one.
    Requirements: Java should be installed on your device.
    """
    map_str = get_random_map()
    run_and_view_battle(WizardsBot(), ETerror(), map_str)


def check_bot():
    """
    Test AttackWeakestPlanetFromStrongestBot against the 2 other bots.
    Print the battle results data frame and the PlayerScore object of the tested bot.
    So is AttackWeakestPlanetFromStrongestBot worse than the 2 other bots? The answer might surprise you.
    
    """
    # maps = [get_random_map(), get_random_map()]
    # player_bot_to_test = AttackWeakestPlanetFromStrongestBot()
    # tester = TestBot(
    #     player=player_bot_to_test,
    #     competitors=[
    #         AttackEnemyWeakestPlanetFromStrongestBot(), AttackWeakestPlanetFromStrongestSmarterNumOfShipsBot()
    #     ],
    #     maps=maps
    # )
    # tester.run_tournament()

    # # for a nicer df printing
    # pd.set_option('display.max_columns', 30)
    # pd.set_option('expand_frame_repr', False)

    # print(tester.get_testing_results_data_frame())
    # print("\n\n")
    # print(tester.get_score_object())
    # To view battle number 4 uncomment the line below
    # tester.view_battle(4)



    # count = 0
    # for num in range(1,100):
    maps = [get_random_map(), get_random_map()]
    player_bot_to_test = WizardsBot()
    tester = TestBot(
        player=player_bot_to_test,
        competitors=[
            AttackEnemyWeakestPlanetFromStrongestBot(),ETerror(), AttackWeakestPlanetFromStrongestSmarterNumOfShipsBot(), AttackWeakestPlanetFromStrongestBot()
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
        #count += tester.get_score_object().total_score

    # print(count/100)
    # To view battle number 4 uncomment the line below
    # tester.view_battle(4)


if __name__ == "__main__":
    check_bot()
    view_bots_battle()