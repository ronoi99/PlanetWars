from multiprocessing.dummy import Array
from turtle import distance
from typing import Dict, Iterable, List
from numpy import Infinity
# from shmerlingBot import shmerlingBot
import pandas as pd
# from  awasomeBot import awasomeBot
from baseline_bot import AttackWeakestPlanetFromStrongestBot, AttackEnemyWeakestPlanetFromStrongestBot, \
    AttackWeakestPlanetFromStrongestSmarterNumOfShipsBot, get_random_map
from planet_wars.battles.tournament import run_and_view_battle, TestBot
from planet_wars.planet_wars import Player, PlanetWars, Order, Planet , Fleet


class Kvutza6(Player):
    """
    Implement here your smart logic.
    Rename the class and the module to your team name
    """
    counter = 0
    def play_turn(self, game: PlanetWars) -> Iterable[Order]:
        """
        See player.play_turn documentation.
        :param game: PlanetWars object representing the map - use it to fetch all the planets and flees in the map.
        :return: List of orders to execute, each order sends ship from a planet I own to other planet.
        """
        self.orders = []
        self.game = game
        self.phase = 0
        self.attacks_to_planet = []
        self.counter += 1 
        for i in range(len(self.game.planets)):
            self.attacks_to_planet.append(0)
            
        planet_that_can_attack = game.get_planets_by_owner(game.ME)
        for fleet in game.fleets:
            self.attacks_to_planet[fleet.destination_planet_id] += fleet.num_ships
        # print(planet_that_can_attack)
        for planet in game.get_planets_by_owner(game.ME):
            enemy_fleets = self.planet_under_attack(planet)
            if  enemy_fleets != []:
                order = self.ask_for_reinforsments(planet , enemy_fleets)
                if order != False:
                    self.orders.append(order) 
            if self.get_strongest_planet() != False:            
                output = Order(
                self.get_strongest_planet().planet_id,
                self.get_MVP_passive(self.get_strongest_planet()).planet_id,
                self.get_defense_score(self.get_MVP_passive(self.get_strongest_planet()), self.game.get_planets_by_owner(PlanetWars.ME)[0]) + 10
                )
                self.orders.append(output)

        # print(self.orders)
        if self.counter%5 ==0 and self.counter >20:
            for planet in  game.get_planets_by_owner(game.ME):
                if(self.attacks_to_planet[planet.planet_id] <= planet.num_ships and planet.num_ships>=50 and self.distance_from_closest_planet(planet)[1][0]['distance'] > 10):
                    #order send forwards \
                    closest = Infinity
                    arr = self.distance_from_closest_planet(planet)[2]
                    for ally in arr:
                        if(self.distance_from_closest_planet(self.game.get_planet_by_id(ally['id']))[1][0]['distance'] < closest and  4 < self.distance_from_closest_planet(self.game.get_planet_by_id(ally['id']))[1][0]['distance']) <15:
                            closest = self.distance_from_closest_planet(self.game.get_planet_by_id(ally['id']))[1][0]['distance'] 
                            target_id = self.distance_from_closest_planet(self.game.get_planet_by_id(ally['id']))[1][0]['id'] 
                            oreder =  Order(
                            planet.planet_id,
                            ally['id'],
                            planet.num_ships//3
                                    )
                            self.orders.append(oreder)
                            break
        return self.orders

    def ask_for_reinforsments(self , defending_planet , enemy_fleets: List[Fleet]):
        """""Returns an order with reinforsment if available and False otherwise"""
        enemy_attacking_ships = 1
        for fleet in enemy_fleets:
            enemy_attacking_ships += fleet.num_ships

        enemy_fleets.sort( key= lambda fleet: fleet.turns_remaining)

        amount_needed_to_def = enemy_attacking_ships - defending_planet.num_ships - defending_planet.growth_rate * (enemy_fleets[0].turns_remaining) - self.reinforsments_on_the_way(defending_planet)
        # print('i need ' ,amount_needed_to_def, '    recieving ',self.reinforsments_on_the_way(defending_planet))
        if amount_needed_to_def > 0:
            print("i need reinforsments")
            for planet in self.game.get_planets_by_owner(self.game.ME):
                if Planet.distance_between_planets(planet , defending_planet) < enemy_fleets[0].turns_remaining and \
                self.planet_under_attack(planet) == []:
                    if planet.num_ships > amount_needed_to_def:
                        return Order(
                            planet,
                            defending_planet,
                            amount_needed_to_def
                        )
        return False

    def reinforsments_on_the_way(self , defending_planet):
        """Returns True if the planet has reinforcments incoming"""
        amount = 0
        my_fleets = self.game.get_fleets_by_owner(owner=PlanetWars.ME)
        for fleet in my_fleets:
            if fleet.destination_planet_id == defending_planet.planet_id:
                amount += fleet.num_ships
        return amount

    def planet_under_attack(self , planet) :
        """Returns True if the planet is under attack"""
        enemy_fleets = self.game.get_fleets_by_owner(owner=PlanetWars.ENEMY)
        fleets = []
        for fleet in enemy_fleets:
            if fleet.destination_planet_id == planet.planet_id:
                fleets.append(fleet)

        return fleets


    def distance_from_closest_planet(self, src_planet: Planet) -> List[List[Dict[int, int]]]:
        '''
        Return a lists of dicts for all the planets sorted by distance.
        Array[0] = neutral planets
        Array[1] = enemy planets
        Array[2] = ME
        '''
        base_planet = src_planet
        planets_distance = []
        planets_distance.append([])
        for netrual_planet in self.game.get_planets_by_owner(PlanetWars.NEUTRAL):
            planets_distance[0].append({'id': netrual_planet.planet_id, 'distance': Planet.distance_between_planets(netrual_planet, base_planet)})
        planets_distance[0] = sorted(planets_distance[0], key=lambda planet: planet['distance'])
        planets_distance.append([])
        for enemy_planet in self.game.get_planets_by_owner(PlanetWars.ENEMY):
            planets_distance[1].append({'id': enemy_planet.planet_id, 'distance': Planet.distance_between_planets(enemy_planet, base_planet)})
        planets_distance[1] = sorted(planets_distance[1], key=lambda planet: planet['distance'])
        planets_distance.append([])
        for ally_planet in self.game.get_planets_by_owner(PlanetWars.ME):
            planets_distance[2].append({'id': ally_planet.planet_id, 'distance': Planet.distance_between_planets(ally_planet, base_planet)})
        planets_distance[2] = sorted(planets_distance[2], key=lambda planet: planet['distance'])
        return planets_distance

    def get_strongest_planet(self) -> Planet:
        output = False
        
        arr = sorted(self.game.get_planets_by_owner(PlanetWars.ME), key= lambda planet: planet.num_ships - self.distance_from_closest_planet(planet)[1][0]['distance'] *0.4)
            # if(len(self.distance_from_closest_planet(self.game.get_planets_by_owner(self.game.ENEMY)[0])[1][0]['distance'])[0])    
        for i in range(len(self.game.get_planets_by_owner(PlanetWars.ME) ) ):
            output = arr[i]
            # print(self.attacks_to_planet[output.planet_id])
            if(self.attacks_to_planet[output.planet_id] >= output.num_ships):
                continue
            return output
                

        
        return False

    def distance_from_natural_planets(self) -> List[Dict[int, int]]:
        base_planet = self.game.get_planets_by_owner(PlanetWars.ENEMY)[0]
        planets_distance = []
        for netrual_planet in self.game.get_planets_by_owner(PlanetWars.NEUTRAL):
            planets_distance.append({'id': netrual_planet.planet_id, 'distance': Planet.distance_between_planets(netrual_planet, base_planet)})
        return sorted(planets_distance, key=lambda planet: planet['distance'])

    def get_closest_battle_ships(self) -> List[Planet]:
        pass

    def get_MVP_passive(self, base_planet) -> Planet:
        avaliable_planets = [p for p in self.game.planets if p.owner != PlanetWars.ME]
        home_planet = base_planet
        # home_planet = [p for p in self.game.planets if p.owner == PlanetWars.ME][0]
        highest_score_planet = 0
        highest_score = -Infinity
        for planet in avaliable_planets:
            if self.get_how_many_fleets_attack_planet(planet) > 1:
                continue
            # score = self.get_score(planet)
            #             score =  self.distance_from_closest_planet(planet)[1][0]['distance'] - 1.5*Planet.distance_between_planets(planet , home_planet) 
            # +20* planet.growth_rate - 0.5* self.get_defense_score(planet, home_planet)
            multiplayer = 1
            if planet.owner == self.game.ENEMY:
                multiplayer = 2
            
            score =   - 4*Planet.distance_between_planets(planet , home_planet) +15*multiplayer* planet.growth_rate - 0.5* self.get_defense_score(planet, home_planet)
            if score > highest_score:
                    highest_score = score
                    highest_score_planet = planet
                
        return highest_score_planet
    
    
    def get_defense_score(self , planet: Planet, home_planet: Planet) -> int:
        """shows enemy hp when we get there"""
        enemy = 1
        if(planet.owner == self.game.NEUTRAL):
            enemy = 0
        return planet.num_ships + enemy * planet.growth_rate * Planet.distance_between_planets(planet , home_planet) 

    def get_how_many_fleets_attack_planet(self , planet: Planet) -> int:
        counter = 0
        for fleet in self.game.get_fleets_by_owner(owner=PlanetWars.ME):
            if fleet.destination_planet_id == planet.planet_id:
                counter += 1
        return counter


def view_bots_battle():
    """
    Runs a battle and show the results in the Java viewer

    Note: The viewer can only open one battle at a time - so before viewing new battle close the window of the
    previous one.
    Requirements: Java should be installed on your device.
    """
    map_str = get_random_map()
    run_and_view_battle(Kvutza6(), AttackEnemyWeakestPlanetFromStrongestBot(), map_str)


def check_bot():
    """
    Test AttackWeakestPlanetFromStrongestBot against the 2 other bots.
    Print the battle results data frame and the PlayerScore object of the tested bot.
    So is AttackWeakestPlanetFromStrongestBot worse than the 2 other bots? The answer might surprise you.
    """
    maps = [get_random_map(), get_random_map()]
    player_bot_to_test = AttackEnemyWeakestPlanetFromStrongestBot()
    tester = TestBot(
        player=player_bot_to_test,
        competitors=[
            Kvutza6(), AttackEnemyWeakestPlanetFromStrongestBot()
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
