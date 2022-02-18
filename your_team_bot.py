from typing import Iterable

import pandas as pd

from baseline_bot import AttackWeakestPlanetFromStrongestBot, get_random_map
from planet_wars.battles.tournament import run_and_view_battle, TestBot
from planet_wars.planet_wars import Player, PlanetWars, Order, Planet, Fleet


class PlanetToAttack:
    def __init__(self, planet: Planet, needed_ships: int, score: float):
        self.planet = planet
        self.needed_ships = needed_ships
        self.score = score


class RonCoolBot(Player):
    """
    Implement here your smart logic.
    Rename the class and the module to your team name
    """
    @staticmethod
    def fight(neutral, enemy, me):
        if neutral >= enemy and neutral >= me:
            return PlanetWars.NEUTRAL, neutral - max(enemy, me)
        if enemy >= neutral and enemy >= me:
            return PlanetWars.ENEMY, enemy - max(neutral, me)
        if me >= enemy and me >= neutral:
            return PlanetWars.ME, me - max(enemy, neutral)

    @classmethod
    def ships_in_turn(cls, planet: Planet, turn: int, game: PlanetWars):
        """
        :return: The amount of ships on the given planet in 'turn' turns
        """
        fleets = [f for f in game.fleets if f.destination_planet_id == planet.planet_id]
        if len(fleets) == 0:
            growth_rate = planet.growth_rate if planet.owner == PlanetWars.ENEMY else 0
            return planet.owner, planet.num_ships + growth_rate * turn

        # simulate the fleets
        number_of_ships = planet.num_ships
        current_owner = planet.owner
        for time in range(1, turn+1):
            growth_rate = planet.growth_rate if current_owner != PlanetWars.NEUTRAL else 0
            number_of_ships += growth_rate
            arriving_fleets = [f for f in fleets if f.turns_remaining == time]
            if len(arriving_fleets) == 0:
                continue
            enemy_ships = sum([f.num_ships for f in arriving_fleets if f.owner == PlanetWars.ENEMY] or [0])
            my_ships = sum([f.num_ships for f in arriving_fleets if f.owner == PlanetWars.ME] or [0])
            neutral_ships = 0
            if current_owner == PlanetWars.NEUTRAL:
                neutral_ships += number_of_ships
            elif current_owner == PlanetWars.ENEMY:
                enemy_ships += number_of_ships
            elif current_owner == PlanetWars.ME:
                my_ships += number_of_ships

            current_owner, number_of_ships = cls.fight(neutral_ships, enemy_ships, my_ships)

        return current_owner, number_of_ships

    @classmethod
    def create_planet_to_attack(cls, source_planet: Planet, dest_planet: Planet, game: PlanetWars):
        distance = Planet.distance_between_planets(source_planet, dest_planet)
        current_owner, number_of_ships = cls.ships_in_turn(dest_planet, turn=distance+1, game=game)
        factor = 0
        if current_owner == PlanetWars.ENEMY:
            factor = 2
        elif current_owner == PlanetWars.NEUTRAL:
            factor = 1
        ships = number_of_ships
        if distance < 10:
            ships -= (10 - distance) * dest_planet.growth_rate
        ships = ships if ships > 0 else 1
        score = (dest_planet.growth_rate * factor) / ships
        return PlanetToAttack(dest_planet, number_of_ships, score)

    def planet_we_can_attack_from(self, planet: Planet, game: PlanetWars):
        if planet.num_ships < 10:
            return False
        owner, num_of_ships = self.ships_in_turn(planet, turn=20, game=game)
        if owner != PlanetWars.ME or num_of_ships < 10:
            return False
        return True

    def play_turn(self, game: PlanetWars) -> Iterable[Order]:
        """
        See player.play_turn documentation.
        :param game: PlanetWars object representing the map - use it to fetch all the planets and flees in the map.
        :return: List of orders to execute, each order sends ship from a planet I own to other planet.
        """
        orders = []
        for source_planet in game.get_planets_by_owner(PlanetWars.ME):
            if not self.planet_we_can_attack_from(source_planet, game):
                continue

            planets_to_attack = [self.create_planet_to_attack(source_planet, p, game) for p in game.planets]
            planets_to_attack = sorted(planets_to_attack, key=lambda p: p.score, reverse=True)
            source_planet_ships = source_planet.num_ships
            for planet_to_attack in planets_to_attack:
                needed_ships = planet_to_attack.needed_ships+5
                source_planet.num_ships -= needed_ships
                if not self.planet_we_can_attack_from(source_planet, game):
                    break
                orders.append(Order(source_planet, planet_to_attack.planet, needed_ships))

                distance = Planet.distance_between_planets(source_planet, planet_to_attack.planet)
                game.fleets.append(
                    Fleet(
                        owner=PlanetWars.ME, num_ships=needed_ships, source_planet_id=source_planet.planet_id,
                        destination_planet_id=planet_to_attack.planet.planet_id,
                        total_trip_length=distance, turns_remaining=distance
                    )
                )
            source_planet.num_ships = source_planet_ships

        return orders


def view_bots_battle():
    """
    Runs a battle and show the results in the Java viewer

    Note: The viewer can only open one battle at a time - so before viewing new battle close the window of the
    previous one.
    Requirements: Java should be installed on your device.
    """
    map_str = get_random_map()
    run_and_view_battle(AttackWeakestPlanetFromStrongestBot(), RonCoolBot(), map_str)


def check_bot():
    """
    Test AttackWeakestPlanetFromStrongestBot against the 2 other bots.
    Print the battle results data frame and the PlayerScore object of the tested bot.
    So is AttackWeakestPlanetFromStrongestBot worse than the 2 other bots? The answer might surprise you.
    """
    maps = [get_random_map() for i in range(20)]
    player_bot_to_test = RonCoolBot()
    tester = TestBot(
        player=player_bot_to_test,
        competitors=[
            AttackWeakestPlanetFromStrongestBot()
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
    # view_bots_battle()
