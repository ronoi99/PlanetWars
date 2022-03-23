from typing import Iterable, List

import pandas as pd

from baseline_bot import AttackWeakestPlanetFromStrongestBot, AttackEnemyWeakestPlanetFromStrongestBot, \
    AttackWeakestPlanetFromStrongestSmarterNumOfShipsBot, get_random_map
from planet_wars.battles.tournament import run_and_view_battle, TestBot
from planet_wars.planet_wars import Player, PlanetWars, Order, Planet



class RonenYuvalBot(Player):
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
        # (1) If we currently have a fleet in flight, just do nothing.
        #if len(game.get_fleets_by_owner(owner=PlanetWars.ME)) >= 1:
        #    return []

        # (2) Find my strongest planet.
        my_planets = game.get_planets_by_owner(owner=PlanetWars.ME)
        if len(my_planets) == 0:
            return []
        my_strongest_planet = max(my_planets, key=lambda planet: planet.num_ships)

        # (3) Find the weakest enemy or neutral planet.
        planets_to_attack = self.get_planets_to_attack(game)
        if len(planets_to_attack) == 0:
            return []

        enemy_fleets = game.get_fleets_by_owner(owner=PlanetWars.ENEMY)

        balances = []
        for my_planet in my_planets:
            my_balance = my_planet.num_ships - sum(enemy_fleet.num_ships for enemy_fleet in enemy_fleets
                                                   if enemy_fleet.destination_planet_id == my_planet.planet_id)
            balances.append((my_planet, my_balance))

        positive_balances = [(balance, planet) for (planet, balance) in balances if balance > 0]
        positive_planets = [planet for (balance, planet) in positive_balances]

        orders = []
        for planet in positive_planets:
            closest_planets = sorted(planets_to_attack, key=lambda d: Planet.distance_between_planets(planet, d))[:8]
            best_growth_lst = sorted(closest_planets, key=lambda d: d.growth_rate, reverse=True)[:4]
            weakest_planet = min(best_growth_lst, key=lambda d: d.num_ships)

            if weakest_planet.owner == PlanetWars.NEUTRAL:
                needed = weakest_planet.num_ships
            else:
                needed = weakest_planet.num_ships + Planet.distance_between_planets(weakest_planet, planet) * weakest_planet.growth_rate

            if planet.num_ships > needed:
                orders.append(Order(planet, weakest_planet, needed + 1))
            else:
                pass

        return orders

        # TODO: don't kill growth == 0, unless it's an enemy
        ordered_planets_to_attack_by_ships_number = sorted([planet for planet in planets_to_attack if planet.growth_rate > 0],
                                                           key=lambda planet: planet.num_ships)[:8]

        planet_to_attack = min([planet for planet in ordered_planets_to_attack_by_ships_number],
                                key=lambda planet: sum(Planet.distance_between_planets(planet, pos_planet)
                                                       for pos_planet in positive_planets))

        balances_sum = sum(balance for (balance, planet) in positive_balances)

        orders1 = [
            Order(
                pos_planet,
                planet_to_attack,
                [min(int(0.5 * pos_planet.num_ships), int(3 * planet_to_attack.num_ships * (balance / balances_sum))) for (balance, planet) in positive_balances if planet.planet_id == pos_planet.planet_id][0]
            ) for pos_planet in positive_planets
        ]

        # Don't forget to filter the growth == 0 condition\

        orders2 = []
        # positive_planet_ids = {planet.planet_id for planet in positive_planets}
        # non_positive_planets = [planet for planet in my_planets if planet.planet_id not in positive_planet_ids]
        #
        # if len(non_positive_planets) > 1:
        #
        #     max_growth_rate_planet = max(non_positive_planets, key=lambda planet: planet.growth_rate)
        #     orders2 = [
        #         Order(
        #             source_planet,
        #             max_growth_rate_planet,
        #             source_planet.num_ships
        #         )
        #         for source_planet in non_positive_planets if source_planet.planet_id != max_growth_rate_planet.planet_id
        #     ]
        # else:
        #     orders2 = []

        return orders1 + orders2

        # ordered_planets_to_attack_by_ships_number = sorted([planet for planet in planets_to_attack],
        #                                                    key=lambda planet: planet.num_ships)[:8]
        #
        # planet_to_attack = min([planet for planet in ordered_planets_to_attack_by_ships_number],
        #                         key=lambda planet: sum(Planet.distance_between_planets(planet, my_planet)
        #                                                for my_planet in my_planets))
        #
        # optional_attackers = my_planets.copy()
        # can_attack = False
        # each_attack_power = 10
        # while not can_attack and len(optional_attackers) > 1:
        #     max_needed = 1
        #     for my_planet in optional_attackers:
        #         if planet_to_attack.owner == PlanetWars.NEUTRAL:
        #             needed = planet_to_attack.num_ships
        #         else:
        #             needed = planet_to_attack.num_ships + Planet.distance_between_planets(planet_to_attack, my_planet) * planet_to_attack.growth_rate
        #
        #         if needed > max_needed:
        #             max_needed = needed
        #
        #     min_attacker = min(optional_attackers, key=lambda p: p.num_ships)
        #     each_attack_power = max_needed // len(optional_attackers)
        #     if each_attack_power > min_attacker.num_ships:
        #         optional_attackers = [at for at in optional_attackers if at.planet_id != min_attacker.planet_id]
        #     else:
        #         can_attack = True
        #
        # orders = []
        # if can_attack:
        #     for optional_att in optional_attackers:
        #         orders.append(Order(optional_att, planet_to_attack, each_attack_power))
        #
        # for planet in my_planets:
        #     if planet.planet_id not in {order.source_planet_id for order in orders}:
        #         orders.append(Order(planet.planet_id, planet_to_attack, 5))
        #
        # return orders


    def ships_to_send_in_a_flee(self, source_planet: Planet, dest_planet: Planet) -> int:
        return source_planet.num_ships // 2

    def get_planets_to_attack(self, game: PlanetWars) -> List[Planet]:
        """
        :param game: PlanetWars object representing the map
        :return: The planets we need to attack
        """
        not_mine_planets = [p for p in game.planets if p.owner != PlanetWars.ME]
        return not_mine_planets

        my_fleets = game.get_fleets_by_owner(owner=PlanetWars.ME)
        my_fleets_dest = {my_fleet.destination_planet_id for my_fleet in my_fleets}

        return [p for p in not_mine_planets if p.planet_id not in my_fleets_dest]


def view_bots_battle():
    """
    Runs a battle and show the results in the Java viewer

    Note: The viewer can only open one battle at a time - so before viewing new battle close the window of the
    previous one.
    Requirements: Java should be installed on your device.
    """
    map_str = get_random_map()
    run_and_view_battle(AlexDavidBot(), RonenYuvalBot(), map_str)


def check_bot():
    """
    Test AttackWeakestPlanetFromStrongestBot against the 2 other bots.
    Print the battle results data frame and the PlayerScore object of the tested bot.
    So is AttackWeakestPlanetFromStrongestBot worse than the 2 other bots? The answer might surprise you.
    """
    maps = [get_random_map() for _ in range(100)]
    player_bot_to_test = RonenYuvalBot()
    tester = TestBot(
        player=player_bot_to_test,
        competitors=[
            AlexDavidBot()
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