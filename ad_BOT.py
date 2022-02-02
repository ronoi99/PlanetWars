from math import dist
import random
from sre_parse import State
from typing import Iterable, List
from runtime_Terror import ETerror
from space_pirate_bot import SpacePirateBot
from dy_team import dyBot
from dream_team_bot import DreamTeamV1

from planet_wars.planet_wars import Player, PlanetWars, Order, Planet
from planet_wars.battles.tournament import get_map_by_id, run_and_view_battle, TestBot

import pandas as pd

from planet_wars.player_bots.baseline_code.baseline_bot import AttackWeakestPlanetFromStrongestBot


class AD_BOT(Player):
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
        return source_planet.num_ships // 2

    def plant_rating(self, game: PlanetWars, plant: Planet):
        plant_rating_arr = []
        planets_to_attack = self.get_planets_to_attack(game)
        if len(planets_to_attack) == 0:
            return
        farrest_planet = max([dist([E_plant.x, E_plant.y], [
            plant.x, plant.y]) for E_plant in planets_to_attack])
        netural_plants = game.get_planets_by_owner(owner=PlanetWars.NEUTRAL)
        for N_plant in netural_plants:
            distance = dist([N_plant.x, N_plant.y], [plant.x, plant.y])
            dist_rating = 1 - (distance / farrest_planet)
            base = 0.0000001 if N_plant.num_ships == 0 else N_plant.num_ships
            q_ships = N_plant.growth_rate
            profit = (q_ships * 10) / base
            grade = profit * dist_rating
            plant_rating_arr.append((grade, N_plant.planet_id))
        sortedArr = sorted(plant_rating_arr, key=lambda x: x[0])
        sortedArr.reverse()
        return sortedArr

    def plant_rating_enemy(self, game: PlanetWars, plant: Planet):
        plant_rating_arr = []
        planets_to_attack = self.get_planets_to_attack(game)
        if len(planets_to_attack) == 0:
            return
        farrest_planet = max([dist([E_plant.x, E_plant.y], [
            plant.x, plant.y]) for E_plant in planets_to_attack])
        netural_plants = game.get_planets_by_owner(owner=PlanetWars.ENEMY)
        for N_plant in netural_plants:
            distance = dist([N_plant.x, N_plant.y], [plant.x, plant.y])
            dist_rating = 1 - (distance / farrest_planet)
            base = 0.0000001 if N_plant.num_ships == 0 else N_plant.num_ships
            q_ships = N_plant.growth_rate
            profit = (q_ships * 10) / base
            grade = profit * dist_rating
            plant_rating_arr.append((grade, N_plant.planet_id))
        sortedArr = sorted(plant_rating_arr, key=lambda x: x[0])
        sortedArr.reverse()
        return sortedArr

    def state_of_game(self, game):
        enemy_ships = sum(
            [plant.num_ships for plant in game.get_planets_by_owner(owner=PlanetWars.ENEMY)])
        my_ships = sum(
            [plant.num_ships for plant in game.get_planets_by_owner(owner=PlanetWars.ME)])
        enemy_growth = sum(
            [plant.growth_rate for plant in game.get_planets_by_owner(owner=PlanetWars.ENEMY)])
        my_growth = sum(
            [plant.growth_rate for plant in game.get_planets_by_owner(owner=PlanetWars.ME)])
        if enemy_ships < my_ships and enemy_growth < my_growth:
            return "A"  # CASE A
        if enemy_ships > my_ships and enemy_growth > my_growth:
            return "B"  # CASE B
        if enemy_ships < my_ships and enemy_growth > my_growth:
            return "C"  # CASE C
        if enemy_ships > my_ships and enemy_growth < my_growth:
            return "D"  # CASE D

        return "E"  # DEFULT

    def fleets_diff(self, game, my_planet_id, destId):
        num_of_fleets_to_send = 0
        my_forces = 0
        for fleet in game.get_fleets_by_owner(1):
            if fleet.destination_planet_id == destId:
                my_forces += fleet.num_ships
        for fleet in game.get_fleets_by_owner(2):
            if fleet.destination_planet_id == destId:
                distance = Planet.distance_between_planets(game.get_planet_by_id(
                    my_planet_id), game.get_planet_by_id(destId))
                distance_by_enemy = []
                sum_forces = 0
                for fleet_1 in game.get_fleets_by_owner(2):
                    distance_by_enemy.append(fleet_1.turns_remaining)
                    sum_forces += fleet_1.num_ships
                min_distance_enemy = min(distance_by_enemy)
                growth = game.get_planet_by_id(destId).growth_rate
                if game.get_planet_by_id(destId).owner == 2:
                    num_of_fleets_to_send = (
                        distance-min_distance_enemy) * growth + sum_forces + game.get_planet_by_id(destId).num_ships + 1 - my_forces
                else:
                    num_of_fleets_to_send = (
                        distance-min_distance_enemy) * growth + sum_forces - game.get_planet_by_id(destId).num_ships + 1 - my_forces

        return num_of_fleets_to_send

    def clacMyFoyrse(self, game, destId):
        sum = 0
        for fleet in game.get_fleets_by_owner(1):
            if fleet.destination_planet_id == destId:
                sum += fleet.num_ships
        return sum

    def play_turn(self, game: PlanetWars) -> Iterable[Order]:
        """
        See player.play_turn documentation.
        :param game: PlanetWars object representing the map - use it to fetch all the planets and flees in the map.
        :return: List of orders to execute, each order sends ship from a planet I own to other planet.
        """
        # (1) If we currently have a fleet in flight, just do nothing.
        # if len(game.get_fleets_by_owner(owner=PlanetWars.ME)) >= 1:
        #     return []
        orders_to_send = []
        my_planets = game.get_planets_by_owner(owner=PlanetWars.ME)
        print(game.get_fleets_by_owner(1)[0].destination_planet_id if len(
            game.get_fleets_by_owner(1)) > 0 else 0)

        match self.state_of_game(game):
            case 'A':
                for plant in my_planets:
                    try:
                        my_ships = plant.num_ships
                        for i in range(len(self.plant_rating_enemy(game, plant))):
                            valuable_plant_enemy_id = self.plant_rating_enemy(game, plant)[
                                i][1]
                            # sum_of_ships_needed = (Planet.distance_between_planets(plant, valuable_planet_to_attack)
                            #                        * valuable_planet_to_attack.growth_rate) + 1 + valuable_planet_to_attack.num_ships
                            sum_of_ships_needed = self.fleets_diff(
                                game, plant.planet_id, valuable_plant_enemy_id)
                            if (sum_of_ships_needed < my_ships):
                                orders_to_send.append(
                                    Order(plant.planet_id, valuable_plant_enemy_id, sum_of_ships_needed + 1))
                                my_ships -= sum_of_ships_needed + 1

                        for i in range(len(self.plant_rating(game, plant))):
                            valuable_plant_id = self.plant_rating(game, plant)[
                                i][1]
                            if (game.get_planet_by_id(valuable_plant_id).num_ships < my_ships):
                                if (self.clacMyFoyrse(game, valuable_plant_id) < game.get_planet_by_id(valuable_plant_id).num_ships):
                                    orders_to_send.append(
                                        Order(plant.planet_id, valuable_plant_id, game.get_planet_by_id(valuable_plant_id).num_ships + 1))
                                    my_ships -= game.get_planet_by_id(
                                        valuable_plant_id).num_ships + 1
                    except:
                        return orders_to_send
            case 'B':
                for plant in my_planets:
                    try:
                        my_ships = plant.num_ships
                        for i in range(len(self.plant_rating(game, plant))):
                            valuable_plant_id = self.plant_rating(game, plant)[
                                i][1]
                            if (game.get_planet_by_id(valuable_plant_id).num_ships < my_ships):
                                orders_to_send.append(
                                    Order(plant.planet_id, valuable_plant_id, game.get_planet_by_id(valuable_plant_id).num_ships + 1))
                                my_ships -= game.get_planet_by_id(
                                    valuable_plant_id).num_ships + 1
                    except:
                        return orders_to_send
            case "C":
                for plant in my_planets:
                    try:
                        valuable_plant_enemy_id = self.plant_rating_enemy(game, plant)[
                            0][1]
                        valuable_plant_id = self.plant_rating(game, plant)[
                            0][1]
                    except:
                        return orders_to_send
                    sum_of_ships_needed = self.fleets_diff(
                        game, plant.planet_id, valuable_plant_enemy_id)
                    my_ships = plant.num_ships
                    if (sum_of_ships_needed < my_ships):
                        orders_to_send.append(
                            Order(plant.planet_id, valuable_plant_enemy_id, sum_of_ships_needed + 1))
                        my_ships -= sum_of_ships_needed + 1
                    if (game.get_planet_by_id(valuable_plant_id).num_ships < my_ships):
                        orders_to_send.append(
                            Order(plant.planet_id, valuable_plant_id, game.get_planet_by_id(valuable_plant_id).num_ships + 1))

            case "D":
                for plant in my_planets:
                    try:
                        my_ships = plant.num_ships
                        for i in range(len(self.plant_rating(game, plant))):
                            valuable_plant_id = self.plant_rating(game, plant)[
                                i][1]
                            if (game.get_planet_by_id(valuable_plant_id).num_ships < my_ships):
                                if (self.clacMyFoyrse(game, valuable_plant_id) < game.get_planet_by_id(valuable_plant_id).num_ships):
                                    orders_to_send.append(
                                        Order(plant.planet_id, valuable_plant_id, game.get_planet_by_id(valuable_plant_id).num_ships + 1))
                                    my_ships -= game.get_planet_by_id(
                                        valuable_plant_id).num_ships + 1
                    except:
                        return orders_to_send
            case "E":
                for plant in my_planets:
                    try:
                        my_ships = plant.num_ships
                        for i in range(len(self.plant_rating(game, plant))):
                            valuable_plant_id = self.plant_rating(game, plant)[
                                i][1]
                            if (game.get_planet_by_id(valuable_plant_id).num_ships < my_ships):
                                orders_to_send.append(
                                    Order(plant.planet_id, valuable_plant_id, game.get_planet_by_id(valuable_plant_id).num_ships + 1))
                                my_ships -= game.get_planet_by_id(
                                    valuable_plant_id).num_ships + 1
                    except:
                        return orders_to_send

        return orders_to_send


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
    run_and_view_battle(AD_BOT(), ETerror(), map_str)


def check_bot():
    """
    Test AD_BOT against the 2 other bots.
    Print the battle results data frame and the PlayerScore object of the tested bot.
    So is AD_BOT worse than the 2 other bots? The answer might surprise you.
    """
    maps = [get_random_map(), get_random_map()]
    player_bot_to_test = AD_BOT()
    tester = TestBot(
        player=player_bot_to_test,
        competitors=[
            SpacePirateBot(), dyBot(), DreamTeamV1(), ETerror()
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
