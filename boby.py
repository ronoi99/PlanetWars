from typing import Iterable, List

import pandas as pd

from baseline_bot import AttackWeakestPlanetFromStrongestBot, AttackEnemyWeakestPlanetFromStrongestBot, \
    AttackWeakestPlanetFromStrongestSmarterNumOfShipsBot, get_random_map
from planet_wars.battles.tournament import run_and_view_battle, TestBot
from planet_wars.planet_wars import Player, PlanetWars, Order, Planet


class boby(Player):
    def get_planets_to_attack(self, game: PlanetWars) -> List[Planet]:
        """
        :param game: PlanetWars object representing the map
        :return: The planets we need to attack
        """
        # 
        x= [p for p in game.planets if p.owner != PlanetWars.ME and not any(
            f.destination_planet_id==p.planet_id for f in game.get_fleets_by_owner(1)
            ) ]
        if len(x)>0:
            return x  
        else:
            return [p for p in game.planets if p.owner != PlanetWars.ME and p.growth_rate >0
           ]
        
      
    def ships_to_send_in_a_flee(self, source_planet: Planet, dest_planet: Planet) -> int:
        return dest_planet.num_ships+1

    def play_turn(self, game: PlanetWars) -> Iterable[Order]:
        """
        See player.play_turn documentation.
        :param game: PlanetWars object representing the map - use it to fetch all the planets and flees in the map.
        :return: List of orders to execute, each order sends ship from a planet I own to other planet.
        """
        # (1) If we currently have a fleet in flight, just do nothing.
        if len(game.get_fleets_by_owner(owner=PlanetWars.ME)) >= 100:
            return []

        # (2) Find my strongest planet.
        my_planets = game.get_planets_by_owner(owner=PlanetWars.ME)
        if len(my_planets) == 0:
            return []
        my_strongest_planet = max(my_planets, key=lambda planet: planet.num_ships)
        
        y= (my_planets[0])
        # (3) Find the weakest enemy or neutral planet.
        planets_to_attack = self.get_planets_to_attack(game)
        if len(planets_to_attack) == 0:
            return []
        enemy_or_neutral_weakest_planet = min(planets_to_attack, key=lambda planet: planet.num_ships)
        
        #closest planet (4)
        planets_to_attack = self.get_planets_to_attack(game)
        if len(planets_to_attack) == 0:
            return []
        closest_enemy = min(planets_to_attack, key=lambda planet:
         abs(planet.x-my_strongest_planet.x)+ abs(planet.y-my_strongest_planet.y))
      
        
        # (5) Send half the ships from my strongest planet to the weakest planet that I do not own.
        listt=[]
            
        for i in my_planets:
            listt.append(Order(
                    i,
                    min(planets_to_attack, key=lambda planet: abs(planet.x-i.x)+ abs(planet.y-i.y)),
                    self.ships_to_send_in_a_flee(i, min(planets_to_attack, key=lambda planet: abs(planet.x-i.x)+ abs(planet.y-i.y)))))
            
                   

        return  listt
                    
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

class SOYsauce(Player):
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
        #self.choose_planet(planets_to_attack)
        
        chosen = planets_to_attack[0]
        chosen.score = (chosen.num_ships/(chosen.growth_rate+0.1)) + chosen.distance_between_planets(my_strongest_planet, chosen)
        #chosen.num_ships / (chosen.growth_rate + .5)+ (chosen.distance_between_planets(my_strongest_planet, chosen)/.5)
        for p in planets_to_attack:
            p.score = (p.num_ships/(p.growth_rate+0.1)) + p.distance_between_planets(my_strongest_planet, p)
            if p.score < chosen.score:
                for y in game.get_fleets_by_owner(owner=PlanetWars.ME):
                 if y.destination_planet_id != p.planet_id:
                     chosen=p

        
        # enemy_or_neutral_weakest_planet = min(planets_to_attack, key=lambda planet: planet.num_ships)

        # (4) Send half the ships from my strongest planet to the weakest planet that I do not own.
        return [Order(
            my_strongest_planet,
            chosen,
            self.ships_to_send_in_a_flee(my_strongest_planet, chosen)
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

    """
    Implement here your smart logic.
    Rename the class and the module to your team name
    """

    def play_turn(self, game: PlanetWars) -> Iterable[Order]:
        """
        See player.play_turn documentation.
        :param game: PlanetWars object representing the map - use it to fetch all the planets and flees in the map.
        :return: List of orders to execute, each order sends ship from a planet I own to other planet.
        """
        # TODO IMPLEMENT HERE YOUR SMART LOGIC
        pass


def view_bots_battle():
    """
    Runs a battle and show the results in the Java viewer

    Note: The viewer can only open one battle at a time - so before viewing new battle close the window of the
    previous one.
    Requirements: Java should be installed on your device.
    """
    map_str = get_random_map()
    run_and_view_battle(boby(), SOYsauce(), map_str)


def check_bot():
    """
    Test AttackWeakestPlanetFromStrongestBot against the 2 other bots.
    Print the battle results data frame and the PlayerScore object of the tested bot.
    So is AttackWeakestPlanetFromStrongestBot worse than the 2 other bots? The answer might surprise you.
    """
    maps = [get_random_map(), get_random_map()]
    player_bot_to_test = SOYsauce()
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
