from typing import Iterable, List
import statistics
import pandas as pd

from baseline_bot import AttackWeakestPlanetFromStrongestBot, AttackEnemyWeakestPlanetFromStrongestBot, \
 AttackWeakestPlanetFromStrongestSmarterNumOfShipsBot, get_random_map
from planet_wars.battles.tournament import run_and_view_battle, TestBot
from planet_wars.planet_wars import Player, PlanetWars, Order, Planet


class Genghis_Khan(Player):
    def get_planets_to_attack_enemy(self, game: PlanetWars) -> List[Planet]:
        """
        :param game: PlanetWars object representing the map
        :return: The planets we need to attack
        """
        lst = [p.growth_rate for p in game.planets if p.owner ==PlanetWars.ENEMY]
        if (lst!=[]):
            medi = statistics.median(lst)
        return [p for p in game.planets if p.owner == PlanetWars.ENEMY and p.growth_rate>=medi]
    #def get_next_planet_to_attack(self,planetlist):
       # days = 20
        #myplanets=
    def get_planets_to_attack_neutral(self, game: PlanetWars) -> List[Planet]:
        """
        :param game: PlanetWars object representing the map
        :return: The planets we need to attack
        """
        lst=[p.growth_rate for p in game.planets if p.owner == PlanetWars.NEUTRAL]
        if lst!= []:
            medi=statistics.median(lst)
        return [p for p in game.planets if p.owner == PlanetWars.NEUTRAL and p.growth_rate>=medi]

    def ships_to_send_in_a_flee(self, source_planet: Planet, dest_planet: Planet) -> int:

        if dest_planet.owner == PlanetWars.ENEMY:
            return (dest_planet.num_ships+ dest_planet.distance_between_planets(source_planet,dest_planet)+ dest_planet.growth_rate*dest_planet.distance_between_planets(source_planet,dest_planet)+20)
        else:
            return (dest_planet.num_ships+20)

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

        if(len(my_planets)>=4):
            planets_to_attack = self.get_planets_to_attack_enemy(game)
            if len(planets_to_attack) == 0:
                planets_to_attack = self.get_planets_to_attack_neutral(game)
                if len(planets_to_attack) == 0:
                    return []
        else:
            planets_to_attack = self.get_planets_to_attack_neutral(game)
            if len(planets_to_attack) == 0:
                return []
        planets_by_growth = planets_to_attack
        planets_by_growth.sort(key=lambda planet : planet.growth_rate,reverse=True)
        top_5_by_growth=planets_by_growth[0:4]
        top_5_by_growth.sort(key=lambda planet : planet.distance_between_planets(planet, my_strongest_planet))
        planet_attack=top_5_by_growth[0]
        enemy_weakest_planet = min(planets_to_attack, key=lambda planet: planet.num_ships)
        if(planet_attack.growth_rate*17<=enemy_weakest_planet.growth_rate*10):
            planet_attack=enemy_weakest_planet
        # (4) Find the closest planet to target.
        maxi=5000
        for p in my_planets:
            if(p.distance_between_planets(p,planet_attack)<maxi and p.num_ships>planet_attack.num_ships):
                my_strongest_planet = p
        return [Order(
            my_strongest_planet,
            planet_attack,
            self.ships_to_send_in_a_flee(my_strongest_planet, planet_attack)
        )]

def view_bots_battle():
    """
    Runs a battle and show the results in the Java viewer

    Note: The viewer can only open one battle at a time - so before viewing new battle close the window of the
    previous one.
    Requirements: Java should be installed on your device.
    """
    map_str = get_random_map()
    run_and_view_battle(AttackWeakestPlanetFromStrongestBot(), AttackEnemyWeakestPlanetFromStrongestBot(), map_str)


def check_bot():
    """
    Test AttackWeakestPlanetFromStrongestBot against the 2 other bots.
    Print the battle results data frame and the PlayerScore object of the tested bot.
    So is AttackWeakestPlanetFromStrongestBot worse than the 2 other bots? The answer might surprise you.
    """
    maps = [get_random_map(), get_random_map()]
    player_bot_to_test = Genghis_Khan()
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
    tester.view_battle(4)


if __name__ == "__main__":
    check_bot()
    #view_bots_battle()
