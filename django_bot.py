from typing import Iterable, List

import pandas as pd

from baseline_bot import AttackWeakestPlanetFromStrongestBot, AttackEnemyWeakestPlanetFromStrongestBot, AttackWeakestPlanetFromStrongestSmarterNumOfShipsBot, get_random_map
from planet_wars.battles.tournament import run_and_view_battle, TestBot
from planet_wars.planet_wars import Player, PlanetWars, Order, Planet, Fleet
#from planet_wars.player_bots.alex_david_bot import AlexDavidBot

class DjangoBot(Player):
    """
    Implement here your smart logic.
    Rename the class and the module to your team name
    """

    def __init__(self):
        super()
        self.home_planet = None

    def max_available_ships_for_attack(self, fleets: List[Fleet], planet):
        enemy_fleets = list(filter(lambda f: f.owner == PlanetWars.ENEMY, fleets))
        attackers = list(filter(lambda f: f.destination_planet_id == planet.planet_id, enemy_fleets))

        if len(attackers) == 0:
            return planet.num_ships

        total = sum(a.num_ships for a in attackers)
        min_turns_remaining = min(a.turns_remaining for a in attackers)
        available = planet.num_ships - total + planet.growth_rate * min_turns_remaining

        result = min(planet.num_ships, available)
        # print(f"home_planet.num_ships: {planet.num_ships}, available: {available}, max_available_ships_for_attack: {result}")
        return result

    def score_planet(self, planet: Planet, source: Planet):
        # if we are under attack - this is top priority to defend
        inbound = self.num_of_ships_for_attack(source, planet)

        if planet.owner == PlanetWars.ME and inbound > 0:
            return 1000000 + planet.growth_rate * 3 - inbound

        # print(f"*** Top Priority {inbound} ***")

        if planet.owner == PlanetWars.NEUTRAL:
            return planet.growth_rate * 2 - 40 * planet.distance_between_planets(source, planet) - 4 * planet.num_ships
        if planet.owner == PlanetWars.ENEMY:
            return (planet.growth_rate * 2 - 40 * planet.distance_between_planets(source, planet)) + 10
        else: # our Planet
            # print(f"*** ERROR ***")
            return -10000

    def find_candidates(self, planets: List[Planet], fleets: List[Fleet], available_ships: int, game:PlanetWars, source):
        not_in_attack = [game.get_planet_by_id(f.destination_planet_id) for f in fleets if f.owner == PlanetWars.ME]
        if not_in_attack is None:
            not_in_attack = {}
        if planets is None:
            return None
            # print("No planets")
        raw_candidates = list(filter(lambda p: (p.growth_rate > 0 and self.num_of_ships_for_attack(source,p) < available_ships), planets))
        raw_candidates_not_in_attack = list(set(raw_candidates).difference(set(not_in_attack)))
        candidates = sorted(raw_candidates_not_in_attack, key=lambda p: self.score_planet(p, source), reverse=True)
        # print(f"candidates: {candidates}")
        if len(candidates) == 0:
            return None
        best_candidate = candidates[0]
        # print(f"best_candidate: {best_candidate}")
        res = {}
        for p in planets:
            rate = p.growth_rate * 3
            dist = p.distance_between_planets(source, p)
            ships = p.num_ships
            score = rate - dist - ships
            res[p.planet_id] = {'score': score, 'dist': dist, 'ships': ships, 'rate': p.growth_rate, 'p_id': p.planet_id}

        return best_candidate

    def my_planet(self, planet):
        planet.owner == PlanetWars.ME

    def enemy_planet(self, planet):
        planet.owner == PlanetWars.ENEMY

    def inbound_attack_ships(self, target: Planet):
        fleets: List[Fleet] = self.game.fleets
        attacking_fleets = filter(lambda f: f.destination_planet_id == target.planet_id and f.owner == PlanetWars.ENEMY, fleets)
        total_ships_inbound = sum([f.num_ships for f in attacking_fleets])
        return total_ships_inbound

    def num_of_ships_for_attack(self, source, target):
        ships = 0

        if target.owner == PlanetWars.NEUTRAL:
            return target.num_ships
        if target.owner == PlanetWars.ENEMY:
            return target.num_ships + target.growth_rate * target.distance_between_planets(source, target)
        else:
            # todo: check
            inbound = self.inbound_attack_ships(target)
            return inbound


        # ships = target.num_ships
        # if self.enemy_planet(target):
        #     ships += target.growth_rate * target.distance_between_planets(source, target)
        # ships += 1

        return ships

    def create_order(self, candidate, source):
        if candidate is None:
            return []

        ships = self.num_of_ships_for_attack(source, candidate)

        # crazy 1 method - if not work - remove it
        if ships > 0:
            ships += 1

        orders = [
            Order(
                source,
                candidate,
                ships
            )
        ]
        return orders

    def play_turn(self, game: PlanetWars) -> Iterable[Order]:

        # graph = self.create_game_graph(game)


        my_planets = game.get_planets_by_owner(owner=PlanetWars.ME)
        enemy_planets = game.get_planets_by_owner(owner=PlanetWars.ENEMY)
        neutral_planets = game.get_planets_by_owner(owner=PlanetWars.NEUTRAL)


        self.game = game

        orders = []

        for planet in my_planets:
            available_ships = self.max_available_ships_for_attack(game.fleets, planet)
            candidate = self.find_candidates(neutral_planets+enemy_planets+my_planets, game.fleets, available_ships, game, planet)
            planet_orders = self.create_order(candidate, planet)
            orders.extend(planet_orders)
        return orders

    def get_densiest_planet(self, game):
        densities = {}
        for planet in game.planets:
            curr_neis = 0
            for target in game.planets:
                if (planet.distance_between_planets(planet, target) < 6):
                    curr_neis += target.growth_rate
            densities[planet.planet_id] = (planet.planet_id, curr_neis, planet.x, planet.y)
        # print(f"planet.planet_id: {planet.planet_id}, x: {planet.x}, y: {planet.y}")
        if game.turns == 0:
            for i in densities.items():
                print(i)
            # print(f"densities: {densities.items()}")

        densiest = max(densities.values(), key=lambda x: x[1])
        return densiest[1]


def view_bots_battle():
    """
    Runs a battle and show the results in the Java viewer

    Note: The viewer can only open one battle at a time - so before viewing new battle close the window of the
    previous one.
    Requirements: Java should be installed on your device.
    """
    map_str = get_random_map()
    # todo: change one of them to our bot
    # run_and_view_battle(YourCoolBot(), AttackEnemyWeakestPlanetFromStrongestBot(), map_str)
    # run_and_view_battle(DjangoBot(), AttackWeakestPlanetFromStrongestSmarterNumOfShipsBot(), map_str)
    run_and_view_battle(DjangoBot(), AlexDavidBot(), map_str)
    # run_and_view_battle(DjangoBot(), RonenYuvalBot(), map_str)
    # run_and_view_battle(DjangoBot(), TheKinders(), map_str)


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


if __name__ == "__main__":
    # check_bot()
    view_bots_battle()