from typing import ByteString, Iterable, List
import math
import pandas as pd
from planet_wars.battles.tournament import run_and_view_battle, TestBot
from planet_wars.planet_wars import Player, PlanetWars, Order, Planet


class teamRocket(Player):
    def get_planets_to_attack(self, game: PlanetWars) -> List[Planet]:
        """
        :param game: PlanetWars object representing the map
        :return: The planets we need to attack
        """
        return [p for p in game.planets if p.owner != PlanetWars.ME]

    def ships_to_send_in_a_flee(self, my_planet: Planet, dest_planet: Planet) -> int:
        
        return (my_planet.num_ships-(0.25*(my_planet.num_ships)))

    def idial_planet(self, game: PlanetWars, my_planet: Planet) -> Planet:
        planets_to_attack = self.get_planets_to_attack(game)
        
         
        list2 = []
        
        for planet in planets_to_attack :
           list2.append((planet, planet.growth_rate, Planet.distance_between_planets(my_planet,planet)))
           

                #min_ship_score = min(ship_score)
            #if (planet.growth_rate) :
           
        list2.sort(key= lambda p: p[1]*1000 - p[2], reverse=True)
        idial_planet_= list2[0][0]
            
            
            
        return idial_planet_

    def ships_on_arrival(self, game: PlanetWars, my_planet: Planet, planet: Planet) -> int :
        if planet.owner == 0 : return planet.num_ships
        return planet.num_ships + planet.growth_rate * Planet.distance_between_planets(my_planet, planet)


    def idial_planet2(self, game: PlanetWars, my_planet: Planet) -> Planet:
        planets_to_attack = self.get_planets_to_attack(game)
        highscore = 0
        ideal_planet = 0
        for planet in planets_to_attack :
            if planet.growth_rate > 4 and Planet.distance_between_planets(my_planet, planet) < 6 :
                return planet
            if my_planet.num_ships <= 4 * self.ships_on_arrival(game, my_planet, planet) :
                continue
            
            score = 1
            score = score * planet.growth_rate**2
            score = score / Planet.distance_between_planets(my_planet, planet)
            if planet.owner == 2 :
                score = score / (planet.num_ships + planet.growth_rate * Planet.distance_between_planets(my_planet, planet))
            elif planet.owner == 0 and planet.num_ships == 0 : 
                return planet
            else : 
                score = score / planet.num_ships
            if score > highscore :
                highscore = score
                ideal_planet = planet
        return ideal_planet

    def play_turn(self, game: PlanetWars) -> Iterable[Order]:
        """
        See player.play_turn documentation.
        :param game: PlanetWars object representing the map - use it to fetch all the planets and flees in the map.
        :return: List of orders to execute, each order sends ship from a planet I own to other planet.
        """
         #(1) If we currently have a fleet in flight, just do nothing.
        #if len(game.get_fleets_by_owner(owner=PlanetWars.ME)) >=  1:
          #return []

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
        closest_planet = min(planets_to_attack, key=lambda planet: math.sqrt((planet.x - my_strongest_planet.x) **2 + (planet.y - my_strongest_planet.y) **2))
        my_planet = my_strongest_planet
        ideal_planet_to_attack = self.idial_planet2(game, my_planet)
        # (4) Send half the ships from my strongest planet to the weakest planet that I do not own.
        return [Order(
            my_strongest_planet,
            ideal_planet_to_attack,
            self.ships_to_send_in_a_flee(my_strongest_planet, ideal_planet_to_attack)
        )]


def view_bots_battle():
    """
    Runs a battle and show the results in the Java viewer

    Note: The viewer can only open one battle at a time - so before viewing new battle close the window of the
    previous one.
    Requirements: Java should be installed on your device.
    """
    map_str = get_random_map()
    run_and_view_battle(teamRocket(), SOYsauce(), map_str)


def check_bot():
    """
    Test bot2 against the 2 other bots.
    Print the battle results data frame and the PlayerScore object of the tested bot.
    So is bot2 worse than the 2 other bots? The answer might surprise you.
    """
    maps = [get_random_map(), get_random_map()]
    player_bot_to_test = teamRocket()
    tester = TestBot(
        player=player_bot_to_test,
        competitors=[
            SOYsauce()
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