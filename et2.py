from typing import Iterable

import pandas as pd
import numpy as np

from baseline_bot import AttackWeakestPlanetFromStrongestBot, AttackEnemyWeakestPlanetFromStrongestBot, \
    AttackWeakestPlanetFromStrongestSmarterNumOfShipsBot, get_random_map
from planet_wars.battles.tournament import run_and_view_battle, TestBot
from planet_wars.planet_wars import Player, PlanetWars, Order, Planet


class ET(Player):
    """
    Implement here your smart logic.
    Rename the class and the module to your team name
    """

    def get_planets_to_attack(self, game: PlanetWars):
        """
        :param game: PlanetWars object representing the map
        :return: The planets we need to attack
        """
        return [p for p in game.planets if p.owner != PlanetWars.ME]

    def play_turn(self, game: PlanetWars) -> Iterable[Order]:
        """
        See player.play_turn documentation.
        :param game: PlanetWars object representing the map - use it to fetch all the planets and flees in the map.
        :return: List of orders to execute, each order sends ship from a planet I own to other planet.
        """
        orders = []
        my_planets = game.get_planets_by_owner(owner=PlanetWars.ME)
        # fleets = game.get_fleets_by_owner(owner=PlanetWars.ENEMY)
        # for fleet in fleets:
        #     attackers = []
        #     dest_planet = game.get_planet_by_id(fleet.destination_planet_id)
        #     if dest_planet.owner == PlanetWars.NEUTRAL:
        #         for my_planet in my_planets:
        #             num_turns = Planet.distance_between_planets(my_planet, dest_planet)
        #             # print(num_turns)
        #             ships_to_send = fleet.num_ships - dest_planet.num_ships + dest_planet.growth_rate + 1
        #             if (num_turns == fleet.turns_remaining + 1) & (ships_to_send <= my_planet.num_ships) &\
        #                     (num_turns < 5):
        #                 attackers.append([my_planet, fleet.destination_planet_id, ships_to_send + 1])
        #         if len(attackers) > 0:
        #             num_ships = 0
        #             strongest_attacker = attackers[0][0]
        #             max_num_ships = strongest_attacker.num_ships
        #             for attacker in attackers:
        #                 if (attacker[0].num_ships > max_num_ships):
        #                     max_num_ships = attacker[0].num_ships
        #                     num_ships = attacker[2]
        #                     strongest_attacker = attacker[0]
        #
        #             orders.append(Order(strongest_attacker.planet_id, dest_planet,num_ships))
        #
        #             my_planets.remove(strongest_attacker)

        planets_to_attack = self.get_planets_to_attack(game)
        if len(planets_to_attack) == 0:
            return []

        enemys_costs = {}
        neutral_costs = {}
        enemy_fleets = game.get_fleets_by_owner(owner=PlanetWars.ENEMY)
        atack_per_planet = {}
        # for i in (game.get_planets_by_owner(owner=PlanetWars.NEUTRAL)):
        #     print('growth_rate', i.growth_rate, 'number', i.num_ships, 'dist', i.x, i.y)
        # for dist in range(100):
        for current_planet in my_planets:
            for dist in range(100):

                current_dist = 0
              # for each of my planets we are looking for destination planets to attack
                for other_planet in planets_to_attack:

                    current_dist = Planet.distance_between_planets(current_planet, other_planet)
                    if current_dist == dist:
                        # candidates are planets that are 1 turn away from me
                        n_resistant_ships = other_planet.num_ships
                        for fleet in enemy_fleets:
                            # checking whether the enemy will fight for this planet
                            # making sure that we have enough ships to win
                            if fleet.destination_planet_id == other_planet.planet_id & fleet.turns_remaining == 1:
                                n_resistant_ships += fleet.num_ships
                        if current_planet.num_ships > n_resistant_ships + 1:
                            if other_planet.owner == PlanetWars.ENEMY:
                                enemys_costs[other_planet.planet_id] = n_resistant_ships
                            else:
                                neutral_costs[other_planet.planet_id] = n_resistant_ships
                minimal_cost = 100000
                selected_enemy = ''
                selected_enemy_cost = 0

                for enemy_id, enemy_cost in enemys_costs.items():
                    if game.get_planet_by_id(enemy_id).growth_rate != 0:
                        new_min = (enemy_cost/(game.get_planet_by_id(enemy_id).growth_rate) ** 3)
                        if minimal_cost > new_min:
                            minimal_cost = new_min
                            selected_enemy = enemy_id
                            selected_enemy_cost = enemy_cost
                if selected_enemy != '':
                    atack_per_planet[current_planet.planet_id] = [selected_enemy, selected_enemy_cost]
                else:
                    selected_neutral = ''
                    selected_neutral_cost = 0
                    for neutral_id, neutral_cost in neutral_costs.items():
                        if game.get_planet_by_id(neutral_id).growth_rate != 0:
                            new_min = (neutral_cost/(game.get_planet_by_id(neutral_id).growth_rate) ** 3)
                            if minimal_cost > new_min:
                                minimal_cost = new_min
                                selected_neutral = neutral_id
                                selected_neutral_cost = neutral_cost
                    if selected_neutral != '':
                        atack_per_planet[int(current_planet.planet_id)] = [selected_neutral, selected_neutral_cost]
        # chosen_attack = ''
        # max_attack_score = 0
        # for agressor, attacked_val in atack_per_planet.items():
        #     score = attacked_val[1] + 1/(attacked_val[3] * 10 + attacked_val[2])
        #     if score > max_attack_score:
        #         max_attack_score = score
        #         chosen_attack = agressor
        # if len(atack_per_planet.keys()) == 0:
        #     return []
        # if chosen_attack not in atack_per_planet:
        #     return []return
        # score = attacked_val[1] + 1 / (attacked_val[3] * 10 + attacked_val[2])

        for agressor, attacked_val in atack_per_planet.items():
            orders.append(Order(agressor, atack_per_planet[agressor][0], atack_per_planet[agressor][1] + 1))

        return orders



        # if len(planets_to_attack) == 0:
        #     return []

        # n_guards = 0
        # for x in game.get_fleets_by_owner(owner=PlanetWars.ENEMY):
        #     print(self.NAME)
        #     if (x.destination_planet_id == self.NAME) & (x.turns_remaining == 1):
        #         n_guards += x.num_ships

        # n_attackers = self.my_planets
        # print('gaurds', n_guards)
        # print('my planet', self.NAME)
        #return []
        #
        #     # (2) Find my strongest planet.
        # my_planets = game.get_planets_by_owner(owner=PlanetWars.ME)
        # if len(my_planets) == 0:
        #     return []
        # my_strongest_planet = max(my_planets, key=lambda planet: planet.num_ships)
        #
        # # (3) Find the weakest enemy or neutral planet.
        # planets_to_attack = self.get_planets_to_attack(game)
        # if len(planets_to_attack) == 0:
        #     return []
        # enemy_or_neutral_weakest_planet = min(planets_to_attack, key=lambda planet: planet.num_ships)
        #
        # # (4) Send half the ships from my strongest planet to the weakest planet that I do not own.
        # return [Order(
        #     my_strongest_planet,
        #     enemy_or_neutral_weakest_planet,
        #     self.ships_to_send_in_a_flee(my_strongest_planet, enemy_or_neutral_weakest_planet)


def view_bots_battle():
    """
    Runs a battle and show the results in the Java viewer

    Note: The viewer can only open one battle at a time - so before viewing new battle close the window of the
    previous one.
    Requirements: Java should be installed on your device.
    """
    map_str = get_random_map()
    run_and_view_battle(AttackWeakestPlanetFromStrongestBot(), ET(), map_str)


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