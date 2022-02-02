from ast import Or
from operator import le
import random
from typing import Iterable, List
from planet_wars.planet_wars import Player, PlanetWars, Order, Planet
from planet_wars.battles.tournament import get_map_by_id, run_and_view_battle, TestBot
import pandas as pd
# from run_time_terror import ETerror


class SquanchyArn(Player):
    """
    Example of very simple bot - it send flee from its strongest planet to the weakest enemy/neutral planet
    """

    def get_planets_to_attack(self, game: PlanetWars) -> List[Planet]:
        """
        :param game: PlanetWars object representing the map
        :return: The planets we need to attack
        """
        return [p for p in game.planets if p.owner != PlanetWars.ME]

    def get_my_planets(self, game: PlanetWars):
        return [p for p in game.planets if p.owner == PlanetWars.ME]

    def filter_planets(self, home_planet, enemy_planet):
        return home_planet.num_ships > enemy_planet.num_ships // 2 if enemy_planet.owner == 0 else home_planet.num_ships // 1.5 > enemy_planet.growth_rate * enemy_planet.num_ships

    def calc_score(self, game: PlanetWars):
        scores_dict = {}
        avrage_turn_until_takedown = 30
        if len(game.get_planets_by_owner(2)) > 5:
            avrage_turn_until_takedown = 5
        my_planets = self.get_my_planets(game)
        enemy_planets = self.get_planets_to_attack(game)
        for planet in my_planets:
            for enemy_planet in enemy_planets:
                if (self.filter_planets(planet, enemy_planet)):
                    turns_until_arrival = planet.distance_between_planets(
                        planet, enemy_planet)
                    enemy_growth = 1 if enemy_planet.owner == 0 else 4 * \
                                                                     enemy_planet.growth_rate
                    ships_lost = enemy_planet.num_ships if enemy_planet.owner == 0 else \
                        (turns_until_arrival *
                         (enemy_planet.growth_rate) + enemy_planet.num_ships)
                    turn_to_gain = avrage_turn_until_takedown - turns_until_arrival
                    profit_ships = turn_to_gain * enemy_growth - ships_lost
                    if not (planet.planet_id in scores_dict):
                        if not (enemy_planet.planet_id in [fleet.destination_planet_id for fleet in
                                                           game.get_fleets_by_owner(1)]):
                            scores_dict[planet.planet_id] = {
                                "profit": profit_ships, "enemey_id": enemy_planet.planet_id}
                    else:
                        if scores_dict[planet.planet_id]["profit"] > profit_ships:
                            pass
                        elif not (enemy_planet.planet_id in [fleet.destination_planet_id for fleet in
                                                             game.get_fleets_by_owner(1)]):
                            scores_dict[planet.planet_id] = {
                                "profit": profit_ships, "enemey_id": enemy_planet.planet_id}
        if len(scores_dict.items()) == 0:
            return
        return scores_dict.items()
        # return max(scores_dict.items(), key=lambda x: x[1]["profit"])

    def ships_to_send_in_a_flee(self, source_planet: Planet, dest_planet: Planet) -> int:
        return dest_planet.num_ships + 10 if dest_planet.owner == 0 else dest_planet.num_ships + dest_planet.growth_rate * source_planet.distance_between_planets(
            source_planet, dest_planet) + 10

    def send_fleet_to_attacker(self, game: PlanetWars):
        enemy_planets_attacking_neutral_planet = [fleet.source_planet_id for fleet in game.get_fleets_by_owner(
            2) if fleet.destination_planet_id in [planet.planet_id for planet in game.get_planets_by_owner(1)]]
        distance_dict = {}
        if len(enemy_planets_attacking_neutral_planet) != 0:
            for planet in game.get_planets_by_owner(1):
                for enemy_planet in [game.get_planet_by_id(id) for id in enemy_planets_attacking_neutral_planet]:
                    distance_dict[planet.planet_id] = {"distance": planet.distance_between_planets(
                        planet, enemy_planet), "enemy_id": enemy_planet.planet_id}
            return min(distance_dict.items(), key=lambda x: x[1]["distance"])

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
        # calculating valid planets
        best_move = self.calc_score(game)
        print(best_move)
        if len(my_planets) == 0:
            return []
        my_strongest_planet = max(
            my_planets, key=lambda planet: planet.num_ships)
        # (3) Find the weakest enemy or neutral planet.
        planets_to_attack = self.get_planets_to_attack(game)
        if len(planets_to_attack) == 0:
            return []
        enemy_or_neutral_weakest_planet = min(
            planets_to_attack, key=lambda planet: planet.num_ships)
        # (4) Send half the ships from my strongest planet to the weakest planet that I do not own.
        if best_move and len(best_move) != 0:
            # return [Order(
            #     game.get_planet_by_id(planet_id=best_move[0]),
            #     game.get_planet_by_id(planet_id=best_move[1]['enemey_id']),
            #     self.ships_to_send_in_a_flee(
            #         game.get_planet_by_id(planet_id=best_move[0]), enemy_or_neutral_weakest_planet)
            # )]
            return [Order(game.get_planet_by_id(move[0]), game.get_planet_by_id(move[1]['enemey_id']),
                          self.ships_to_send_in_a_flee(game.get_planet_by_id(planet_id=move[0]),
                                                       game.get_planet_by_id(planet_id=move[1]["enemey_id"]))) for move
                    in best_move]
        else:
            attac_fleet_attacker = self.send_fleet_to_attacker(game)
            if attac_fleet_attacker:
                return [Order(game.get_planet_by_id(attac_fleet_attacker[0]),
                              game.get_planet_by_id(attac_fleet_attacker[1]['enemy_id']),
                              self.ships_to_send_in_a_flee(game.get_planet_by_id(planet_id=attac_fleet_attacker[0]),
                                                           game.get_planet_by_id(
                                                               planet_id=attac_fleet_attacker[1]["enemy_id"])))]
            else:
                return []


class AttackEnemyWeakestPlanetFromStrongestBot(SquanchyArn):
    """
    Same like Squanchy but attacks only enemy planet - not neutral planet.
    The idea is not to "waste" ships on fighting with neutral planets.
    See which bot is better using the function view_bots_battle
    """

    def get_planets_to_attack(self, game: PlanetWars):
        """
        :param game: PlanetWars object representing the map
        :return: The planets we need to attack - attack only enemy's planets
        """
        return game.get_planets_by_owner(owner=PlanetWars.ENEMY)


class AttackWeakestPlanetFromStrongestSmarterNumOfShipsBot(SquanchyArn):
    """
    Same like Squanchy but with smarter flee size.
    If planet is neutral send up to its population + 5
    If it is enemy send most of your ships to fight!
    Will it out preform Squanchy? see test_bot function.
    """

    def ships_to_send_in_a_flee(self, source_planet: Planet, dest_planet: Planet) -> int:
        original_num_of_ships = source_planet.num_ships // 2
        if dest_planet.owner == PlanetWars.NEUTRAL:
            if dest_planet.num_ships < original_num_of_ships:
                return dest_planet.num_ships + 5
        if dest_planet.owner == PlanetWars.ENEMY:
            return int(source_planet.num_ships * 0.75)
        return original_num_of_ships


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
    run_and_view_battle(SquanchyArn(
    ), SquanchyArn(), map_str)


def check_bot():
    """
    Test Squanchy against the 2 other bots.
    Print the battle results data frame and the PlayerScore object of the tested bot.
    So is Squanchy worse than the 2 other bots? The answer might surprise you.
    """
    maps = [get_random_map(), get_random_map()]
    player_bot_to_test = SquanchyArn()
    tester = TestBot(
        player=player_bot_to_test,
        competitors=[
            SquanchyArn(
            ), AttackWeakestPlanetFromStrongestSmarterNumOfShipsBot()
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
