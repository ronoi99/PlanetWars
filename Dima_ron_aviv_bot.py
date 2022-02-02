import random
from typing import Iterable, List

from planet_wars.planet_wars import Player, PlanetWars, Order, Planet, Fleet
from planet_wars.battles.tournament import get_map_by_id, run_and_view_battle, TestBot
from team_wizards import WizardsBot

import pandas as pd


class AttackWeakestPlanetFromStrongestBot(Player):
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
        return source_planet.num_ships // 2

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

        # (3) Find the weakest enemy or neutral planet.
        planets_to_attack = self.get_planets_to_attack(game)
        if len(planets_to_attack) == 0:
            return []
        enemy_or_neutral_weakest_planet = min(planets_to_attack, key=lambda planet: planet.num_ships)

        # (4) Send half the ships from my strongest planet to the weakest planet that I do not own.
        return [Order(
            my_strongest_planet,
            enemy_or_neutral_weakest_planet,
            self.ships_to_send_in_a_flee(my_strongest_planet, enemy_or_neutral_weakest_planet)
        )]

class WizardsBot(Player):
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
        growth = dest_planet.growth_rate
        distance = dest_planet.distance_between_planets(source_planet, dest_planet)
        # print(growth, distance)
        if dest_planet.owner == PlanetWars.NEUTRAL:
            return (dest_planet.num_ships + 6)
        else:
            return (dest_planet.num_ships + growth * distance + 5)
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
        
        chosen = planets_to_attack[0]
        chosen.score = chosen.num_ships / (chosen.growth_rate + .5)+ (chosen.distance_between_planets(my_strongest_planet, chosen) / .5)
        for p in planets_to_attack:
            p.score = p.num_ships / (p.growth_rate + .5)+ p.distance_between_planets(my_strongest_planet, p) / .5

            if p.score < chosen.score:
                chosen = p
        
        # enemy_or_neutral_weakest_planet = min(planets_to_attack, key=lambda planet: planet.num_ships)

        # (4) Send half the ships from my strongest planet to the weakest planet that I do not own.
        return [Order(
            my_strongest_planet,
            chosen,
            self.ships_to_send_in_a_flee(my_strongest_planet, chosen)
        )]        

class dima(Player):
    """
    Example of very simple bot - it send flee from its strongest planet to the weakest enemy/neutral planet
    """
    #calculating distance between two planets
    def distance(self, source, destination):
        if source==destination:
            return 0.00000000001
        return Planet.distance_between_planets(source, destination)

    #calculating the number of ships that can be sent to a planet
    def ships_to_send(self, source_planet: Planet, dest_planet: Planet) -> int:
        return source_planet.num_ships - 1
    
    #get number of ships on a planet
    def get_num_ships(self, planet):
        if planet.num_ships==0:
            return 0.00000000001
        return planet.num_ships
    
    #get growth rate of a planet
    def get_growth_rate(self, planet):
        return planet.growth_rate

    # #calculating enamy planet shipes in the future
    # def enemy_ships_in_future(self, source_planet: Planet, dest_planet: Planet, num_turns: int) -> int:
    #     return dest_planet.num_ships + (dest_planet.growth_rate * num_turns)

    
    def planet_ships_in_future(self, game ,planet: Planet, num_turns: int) -> int:
        backup = 0
        for fleet in game.get_fleets_by_owner(owner=PlanetWars.ENEMY):
            if fleet.destination_planet_id == planet.planet_id:
                backup+=fleet.num_ships
        if planet.owner == PlanetWars.NEUTRAL:
            return planet.num_ships+backup 
        else:     
            return planet.num_ships + (planet.growth_rate * num_turns) +backup
    


    #rating a planet by distance, growth rate and number of ships
    def rate_planet(self, game,source,destination ):
        
        #weights :
        distance_weight=1.3
        growth_rate_weight=1.2
        num_ships_weight=1
        enemy_weight=1

        if self.game_rate(game)>0.5:
            enemy_weight=1.2
        if self.game_rate(game)>0.6:
            enemy_weight=1.4    
        if self.distance(source,destination)>=15:
            return 0
        if destination.growth_rate==0:
            return 0
        if(destination.owner==PlanetWars.ENEMY and source.num_ships>destination.num_ships):
            enemy_weight=1.5

        for fleet in game.get_fleets_by_owner(owner=PlanetWars.ME):
            if fleet.destination_planet_id == destination.planet_id and destination.owner == PlanetWars.NEUTRAL:
                return 0
            
        return enemy_weight*growth_rate_weight*self.get_growth_rate(destination) / (distance_weight*self.distance(source,destination) * num_ships_weight*self.get_num_ships(destination))
    #calculate total growth rate of all my planets
    def total_growth_rate(self, game):
        #total game growth rate
        total_growth_rate=0
        for planet in game.planets:
            total_growth_rate+=planet.growth_rate
        return total_growth_rate

    #calculate total growth rate of all my planets
    def my_growth_rate(self, game):
        total=0
        for planet in game.get_planets_by_owner(owner=PlanetWars.ME):
            total+=planet.growth_rate
        return total

    #calculate game rate
    def game_rate(self, game):
        return self.my_growth_rate(game)/self.total_growth_rate(game)

        

    
    
    def get_planets_to_attack(self, game: PlanetWars) -> List[Planet]:
        """
        :param game: PlanetWars object representing the map
        :return: The planets we need to attack
        """
        return [p for p in game.planets if p.owner != PlanetWars.ME]

    def ships_to_send_in_a_flee(self, game ,source_planet: Planet, dest_planet: Planet) -> int:
        # if source_planet.num_ships <=30:
        #     return 0
        # if source_planet.num_ships <=40 and source_planet.growth_rate <=2  :
        #     return 0 
        return self.planet_ships_in_future(game,dest_planet,self.distance(source_planet,dest_planet))+2
        
    

    def play_turn(self, game: PlanetWars) -> Iterable[Order]:
        """
        See player.play_turn documentation.
        :param game: PlanetWars object representing the map - use it to fetch all the planets and flees in the map.
        :return: List of orders to execute, each order sends ship from a planet I own to other planet.
        """
        # (1) If we currently have a fleet in flight, just do nothing.
        # if len(game.get_fleets_by_owner(owner=PlanetWars.ME)) >= 1:
        #     return []

        # (2) Find my strongest planet.
        my_planets = game.get_planets_by_owner(owner=PlanetWars.ME)
        if len(my_planets) == 0:
            return []
        my_strongest_planet = max(my_planets, key=lambda planet: planet.num_ships)

        ## (3) Find the highest rate enemy or neutral planet.
        planets_to_attack = self.get_planets_to_attack(game)
        if len(planets_to_attack) == 0:
            return []
        enemy_or_neutral_weakest_planet = max(planets_to_attack, key=lambda planet: self.rate_planet(game,my_strongest_planet,planet))

        # # (3) Find the weakest enemy or neutral planet.
        # planets_to_attack = self.get_planets_to_attack(game)
        # if len(planets_to_attack) == 0:
        #     return []
        # enemy_or_neutral_weakest_planet = min(planets_to_attack, key=lambda planet: planet.num_ships)

        # (4) Send half the ships from my strongest planet to the weakest planet that I do not own.
        arr =[]
        for planet in my_planets:
            arr.append(Order(
            planet,
            enemy_or_neutral_weakest_planet,
            self.ships_to_send_in_a_flee(game,planet, enemy_or_neutral_weakest_planet)
        ))
        return arr
        



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
        return game.get_planets_by_owner(owner=PlanetWars.ENEMY)


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

class ETerror(Player):
    """
    Eterro
    """
    def get_planets_to_attack(self, game: PlanetWars) -> List[Planet]:
        """
        :param game: PlanetWars object representing the map
        :return: The planets we need to attack
        """

        return [p for p in game.planets if p.owner != PlanetWars.ME]
    
    def get_my_planets(self, game: PlanetWars) -> List[Planet]:
        """
        :param game: PlanetWars object representing the map
        :return: The planets we need to attack
        """

        return [p for p in game.planets if p.owner == PlanetWars.ME]

    def calc_fleet(source_planet: Planet, dest_planet: Planet):
        dis = Planet.distance_between_planets(source_planet, dest_planet)
        if dest_planet.owner == 2:
            return dest_planet.num_ships + (dest_planet.growth_rate * dis)
        return dest_planet.num_ships

    def get_all_planets_list (self, game:PlanetWars):
        return [p for p in game.planets if p.owner != PlanetWars.ME]
        
    def farest_planet_rate(self, game: PlanetWars, source_planet: Planet):
        distance_key = lambda a: Planet.distance_between_planets(source_planet, a)
        return sorted(self.get_all_planets_list(game),key=distance_key)


    def biggest_growth_rate(self, game: PlanetWars):
        keyGrowthRate = lambda a:a.growth_rate
        return sorted(self.get_all_planets_list(game),key=keyGrowthRate)
        
    def smallest_planet_fleet(self, game: PlanetWars):
        key_num_ships = lambda a:a.num_ships
        return sorted(self.get_all_planets_list(game),key=key_num_ships)
        
        
    def best_option(self, game: PlanetWars, source_planet: Planet)->Planet:
        distanceList = self.farest_planet_rate(game, source_planet)[::-1]
        growthList = self.biggest_growth_rate(game)
        armiesList = self.smallest_planet_fleet(game)[::-1]
        bestOption = {p: 0 for p in self.get_all_planets_list(game)}

        for index, planet in enumerate(distanceList):
            bestOption[planet] +=  index
        for index, planet in enumerate(growthList):
            bestOption[planet] +=  index    
        for index, planet in enumerate(armiesList):
            bestOption[planet] +=  index
        if bestOption:
            target = max(bestOption.items(),key= lambda a:a[1])[0]
            return target
        return None
   

    def ships_to_send_in_a_flee(self, source_planet: Planet, dest_planet: Planet) -> int:
        if dest_planet.owner == 2:
            dest_ships_num = dest_planet.num_ships + (dest_planet.growth_rate * Planet.distance_between_planets(source_planet, dest_planet)) + 1
        elif dest_planet.owner == 0:
            dest_ships_num = dest_planet.num_ships + 1
        if source_planet.num_ships > dest_ships_num:
            return dest_ships_num
        return 0

    def play_turn(self, game: PlanetWars) -> Iterable[Order]:
        """
        See player.play_turn documentation.
        :param game: PlanetWars object representing the map - use it to fetch all the planets and flees in the map.
        :return: List of orders to execute, each order sends ship from a planet I own to other planet.
        """
        orders = []
        for planet in self.get_my_planets(game):
            attack_planet = self.best_option(game,planet)
            if not attack_planet:
                return []
            troops = self.ships_to_send_in_a_flee(planet,attack_planet)
            if troops > 0:
                orders.append(Order(planet,attack_planet,troops))
        return orders

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
    run_and_view_battle(ETerror(), dima(), map_str)


def check_bot():
    """
    Test AttackWeakestPlanetFromStrongestBot against the 2 other bots.
    Print the battle results data frame and the PlayerScore object of the tested bot.
    So is AttackWeakestPlanetFromStrongestBot worse than the 2 other bots? The answer might surprise you.
    """
    maps = [get_random_map(), get_random_map()]
    player_bot_to_test = WizardsBot()
    tester = TestBot(
        player=player_bot_to_test,
        competitors=[
            WizardsBot(), dima()
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
    view_bots_battle()
