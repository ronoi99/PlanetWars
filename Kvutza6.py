from turtle import distance
from typing import Dict, Iterable, List
from numpy import Infinity

import pandas as pd

from baseline_bot import AttackWeakestPlanetFromStrongestBot, AttackEnemyWeakestPlanetFromStrongestBot, \
    AttackWeakestPlanetFromStrongestSmarterNumOfShipsBot, get_random_map
from planet_wars.battles.tournament import run_and_view_battle, TestBot
from planet_wars.planet_wars import Player, PlanetWars, Order, Planet


class Kvutza6(Player):
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
        
        self.game = game
        self.phase = 0
        # print(self.distance_from_closest_planet(game.get_planets_by_owner(game.ME)[0])[0])

        if(len(self.game.get_planets_by_owner(PlanetWars.ME))>0):
            output = Order(
            self.game.get_planets_by_owner(PlanetWars.ME)[0].planet_id,
            self.get_MVP(),
            self.game.get_planets_by_owner(PlanetWars.ME)[0].num_ships//2
            )
            print(output)
            return [output]
        else:
             return []

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

    def distance_from_natural_planets(self) -> List[Dict[int, int]]:
        base_planet = self.game.get_planets_by_owner(PlanetWars.ENEMY)[0]
        planets_distance = []
        for netrual_planet in self.game.get_planets_by_owner(PlanetWars.NEUTRAL):
            planets_distance.append({'id': netrual_planet.planet_id, 'distance': Planet.distance_between_planets(netrual_planet, base_planet)})
        return sorted(planets_distance, key=lambda planet: planet['distance'])

    def get_closest_battle_ships(self) -> List[Planet]:
        pass

    def get_MVP(self):
        avaliable_planets = [p for p in self.game.planets if p.owner != PlanetWars.ME]
        home_planet = [p for p in self.game.planets if p.owner == PlanetWars.ME][0]
        highest_score_planet = 0
        highest_score = -Infinity
        for planet in avaliable_planets:
            # score = self.get_score(planet)
            enemy_dist =self.distance_from_closest_planet(planet)[1][0]['distance'] 
            score = self.distance_from_closest_planet(planet)[1][0]['distance'] + Planet.distance_between_planets(planet , home_planet) +10* planet.growth_rate - self.get_defense_score(planet, home_planet)
            if score > highest_score:
                highest_score = score
                highest_score_planet = planet.planet_id
                
        return highest_score_planet

    def get_defense_score(self , planet: Planet, home_planet: Planet):
        """shows enemy hp when we get there"""
        enemy = 1
        if(planet.owner == self.game.NEUTRAL):
            enemy = 0
        return planet.num_ships + enemy * planet.growth_rate * Planet.distance_between_planets(planet , home_planet) 
        

    def get_phase(self) -> None:
        ''''''
        self.phase

    def evolve_phase(self):
        self.phase += 1

    def planet_under_attack(self , planet) -> bool:
        """Returns True if the planet is under attack"""
        enemy_fleets = self.game.get_fleets_by_owner(owner=PlanetWars.ENEMY)
        for fleet in enemy_fleets:
            if fleet.destination_planet_id == planet.id:
                return True

        return False


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
    player_bot_to_test = AttackWeakestPlanetFromStrongestBot()
    tester = TestBot(
        player=player_bot_to_test,
        competitors=[
            Kvutza6(), AttackWeakestPlanetFromStrongestSmarterNumOfShipsBot()
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
