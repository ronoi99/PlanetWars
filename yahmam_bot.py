from typing import Iterable, List

import pandas as pd

from baseline_bot import AttackWeakestPlanetFromStrongestBot, AttackEnemyWeakestPlanetFromStrongestBot, \
    AttackWeakestPlanetFromStrongestSmarterNumOfShipsBot, get_random_map
from planet_wars.battles.tournament import run_and_view_battle, TestBot
from planet_wars.planet_wars import Player, PlanetWars, Order, Planet

class YahmamBot(Player):
    """
    Implement here your smart logic.
    Rename the class and the module to your team name
    """
    
    def calculate_planet(self, game: PlanetWars, planet: Planet, my_strongest_planet: Planet) -> float:
        distance = my_strongest_planet.distance_between_planets(my_strongest_planet, planet)
        return (((100 - distance) + planet.growth_rate) / 2)


    def get_planets_to_attack(self, game: PlanetWars) -> List[Planet]:
        """
        :param game: PlanetWars object representing the map
        :return: The planets we need to attack
        """
        return [p for p in game.planets if p.owner != PlanetWars.ME]

    def ships_to_send_in_a_flee(self, source_planet: Planet) -> int:
        return source_planet.num_ships // 2    

    def play_turn(self, game: PlanetWars) -> Iterable[Order]:
        """
        See player.play_turn documentation.
        :param game: PlanetWars object representing the map - use it to fetch all the planets and flees in the map.
        :return: List of orders to execute, each order sends ship from a planet I own to other planet.
        """
        planet_scores = {}
        planet_list = []
       
        if game.turns < 20:
            # (1) If we currently have a fleet in flight, just do nothing.
            if len(game.get_fleets_by_owner(owner=PlanetWars.ME)) >= 1:
                return []
        else:
            if len(game.get_fleets_by_owner(owner=PlanetWars.ME)) >= 2:
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

        for planet in planets_to_attack:
            if planet.num_ships < my_strongest_planet.num_ships / 2:
                score = self.calculate_planet(planet=planet, my_strongest_planet=my_strongest_planet, game=game)
                planet_scores[str(score)] = planet
                planet_list.append(score)

        if len(planet_list) != 0:
            highest_score_planet = planet_scores[str(max(planet_list))] 
        else:
            highest_score_planet = my_strongest_planet     

        enemy_planets = game.get_planets_by_owner(owner=PlanetWars.ENEMY)
        for planet in my_planets:
            for enemy_planet in enemy_planets:
                if planet.num_ships / 2 > enemy_planet.num_ships + planet.distance_between_planets(planet, enemy_planet) * enemy_planet.growth_rate:
                    highest_score_planet = enemy_planet  
  
        # (4) Send half the ships from my strongest planet to the weakest planet that I do not own.
        return [Order(
            my_strongest_planet,
            highest_score_planet,
            my_strongest_planet.num_ships /2
        )]

def view_bots_battle():
    """
    Runs a battle and show the results in the Java viewer

    Note: The viewer can only open one battle at a time - so before viewing new battle close the window of the
    previous one.
    Requirements: Java should be installed on your device.
    """
    map_str = get_random_map()
    run_and_view_battle(YahmamBot(), AttackEnemyWeakestPlanetFromStrongestBot(), map_str)


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
