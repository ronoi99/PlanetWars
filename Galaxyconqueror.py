from typing import Iterable
from typing import Iterable, List

import pandas as pd

from baseline_bot import AttackWeakestPlanetFromStrongestBot, AttackEnemyWeakestPlanetFromStrongestBot, \
    AttackWeakestPlanetFromStrongestSmarterNumOfShipsBot, get_random_map
from planet_wars.battles.tournament import run_and_view_battle, TestBot
from planet_wars.planet_wars import Player, PlanetWars, Order, Planet
from SOYsauce import SOYsauce


class Galaxyconqueror(Player):
    """
    Implement here your smart logic.
    Rename the class and the module to your team name
    """
    game_mode = 'deff'

    def attack_mode (self, game: PlanetWars):
        my_planets = game.get_planets_by_owner(owner=PlanetWars.ME)
        enemy_planets = game.get_planets_by_owner(owner=PlanetWars.ENEMY)
        orders = []
        for i in my_planets:
            if i.growth_rate == 5:
                my_planets.remove(i)
        for j in enemy_planets:
            if j.growth_rate != 5:
                enemy_planets.remove(i)
        enemy_planets.sort(key = lambda planet: planet.num_ships)
        for i in my_planets:
            Order(i,enemy_planets[0],i.num_ships-1)
        return orders


    def secret_weapon(self, game: PlanetWars):
        my_planets = game.get_planets_by_owner(owner=PlanetWars.ME)
        enemy_fleets = game.get_fleets_by_owner(owner = PlanetWars.ENEMY)
        orders = []
        for fleet in enemy_fleets:
            for myplanet in my_planets:
                 if Planet.distance_between_planets(myplanet, game.get_planet_by_id(fleet.destination_planet_id)) == (fleet.turns_remaining + 1) and game.get_planet_by_id(fleet.destination_planet_id).owner == 0 :
                    orders.append (Order(
                    myplanet.planet_id, 
                    fleet.destination_planet_id, 
                    fleet.num_ships - game.get_planet_by_id(fleet.destination_planet_id).num_ships + game.get_planet_by_id(fleet.destination_planet_id).growth_rate + 1))
        return orders

    def get_planets_to_attack(self, game: PlanetWars) -> List[Planet]:
        """
        :param game: PlanetWars object representing the map
        :return: The planets we need to attack
        """
        return [p for p in game.planets if p.owner != PlanetWars.ME]
    
    def attack_closest_planet(self, game: PlanetWars):
        my_planets = game.get_planets_by_owner(owner=PlanetWars.ME)
        my_planets.sort(key = lambda planet: planet.num_ships)
        planets_to_attack = self.get_planets_to_attack(game)
        orders = []
        for planet in my_planets:
            planets_to_attack.sort(key =lambda planet_to_attack: (planet.distance_between_planets(planet,planet_to_attack),(planet.growth_rate*-1))) 
                       
            if len(planets_to_attack) > 0:
                dest = planets_to_attack[0]
            else:
                dest = my_planets[-1]
            if dest.owner == 0:
                num_ships = dest.num_ships + 1
            else:
                num_ships = dest.num_ships + dest.growth_rate * planet.distance_between_planets(planet, dest) + 1

            orders.append(Order(planet,dest,num_ships))
        return orders


    def play_turn(self, game: PlanetWars) -> Iterable[Order]:
        """
        See player.play_turn documentation.
        :param game: PlanetWars object representing the map - use it to fetch all the planets and flees in the map.
        :return: List of orders to execute, each order sends ship from a planet I own to other planet.
        """
        # TODO IMPLEMENT HERE YOUR SMART LOGIC
        #pass
        my_planets = game.get_planets_by_owner(owner=PlanetWars.ME)
        cnt = 0
        for planet in my_planets:
            if planet.growth_rate == 5:
                cnt =+ 1
        if cnt >= 3:
            self.game_mode = 'attack'

        while self.game_mode == 'deff':
            sw = self.secret_weapon(game)
            acp = self.attack_closest_planet(game)
            return sw + acp
        while self.game_mode == 'attack':
            sw = self.secret_weapon(game)
            atk = self.attack_mode(game)
            acp = self.attack_closest_planet(game)
            return game+ sw + acp


def view_bots_battle():
    """
    Runs a battle and show the results in the Java viewer

    Note: The viewer can only open one battle at a time - so before viewing new battle close the window of the
    previous one.
    Requirements: Java should be installed on your device.
    """
    map_str = get_random_map()
    run_and_view_battle(SOYsauce(), Galaxyconqueror(), map_str)


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
