from typing import Iterable

import pandas as pd
from typing import Union, Iterable, List
from baseline_bot import AttackWeakestPlanetFromStrongestBot, AttackEnemyWeakestPlanetFromStrongestBot, \
    AttackWeakestPlanetFromStrongestSmarterNumOfShipsBot, get_random_map
from planet_wars.battles.tournament import run_and_view_battle, TestBot
from planet_wars.planet_wars import Player, PlanetWars, Order, Planet


class TeamRocketBot(Player):
    """
    Implement here your smart logic.
    Rename the class and the module to your team name
    """

    MAX_GROWTH = 1
    MAX_DIST = 1
    MAX_SHIPS = 800
    NUM_ATTACKS = 3
    def get_max(self,game:PlanetWars):
        max_g = 0
        max_g = max([p.growth_rate for p in game.planets])
        self.MAX_GROWTH = max_g
        max_d=0
        for p1 in game.planets:
            for p2 in game.planets:
                curr_d = p1.distance_between_planets(p1,p2)
                if max_d < curr_d:
                    max_d = curr_d

        self.MAX_DIST = max_d
        self.MAX_SHIPS =  max([p.num_ships for p in self.get_planets_to_attack(game)])



    def get_planets_to_attack(self, game: PlanetWars) -> List[Planet]:
        """
        :param game: PlanetWars object representing the map
        :return: The planets we need to attack
        """
        return [p for p in game.planets if p.owner != PlanetWars.ME]

    def get_my_planets(self, game: PlanetWars) -> List[Planet]:
        """
        :param game: PlanetWars object representing the map
        :return: The planets we need to attack
        """
        return [p for p in game.planets if p.owner == PlanetWars.ME]

    """
    :return: factor of ships to add to attacking fleet amount in order to handle the enemies attacks
    """
    def curr_inflight_fleet_factor(self, dst_planet: Planet, dist: int, game: PlanetWars):
        flee_array = game.get_fleets_by_owner(owner=PlanetWars.ENEMY)
        sum_return = 0
        neutral_attack = False
        for flee in flee_array:
            if flee.destination_planet_id == dst_planet.planet_id:
                if flee.turns_remaining < dist:
                    if dst_planet.owner == PlanetWars.NEUTRAL:
                        if flee.num_ships <= dst_planet.num_ships:
                            sum_return -= flee.num_ships
                        else:
                            if not neutral_attack:
                                sum_return -= dst_planet.num_ships
                                neutral_attack = True
                            sum_return += flee.num_ships - dst_planet.num_ships + dst_planet.growth_rate * (
                                    dist - flee.turns_remaining)

                    if dst_planet.owner == PlanetWars.ENEMY:
                        sum_return += flee.num_ships
                elif flee.turns_remaining == dist:
                    if dst_planet.owner == PlanetWars.NEUTRAL:
                        if flee.num_ships > dst_planet.num_ships:
                            # if not neutral_attack:
                            #     sum_return -= dst_planet.num_ships
                            #     neutral_attack = True
                            sum_return += flee.num_ships - dst_planet.num_ships

                    if dst_planet.owner == PlanetWars.ENEMY:
                        sum_return += flee.num_ships

        return sum_return

    def can_leave_planet(self, game: PlanetWars, src_planet: Planet, sent_ships: int):
        flee_array = game.get_fleets_by_owner(owner=PlanetWars.ENEMY)
        attacking_fleets = []
        for fleet in flee_array:
            if fleet.destination_planet_id == src_planet.planet_id:
                attacking_fleets.append(fleet)

        if len(attacking_fleets) == 0:
            return True

        turn_dict = {}
        for flee in attacking_fleets:
            list_turns = turn_dict.get(flee.turns_remaining, [])
            if len(list_turns) == 0:
                turn_dict[flee.turns_remaining] = list_turns
            list_turns.append(flee)

        curr_ships = src_planet.num_ships - sent_ships
        last_key = 0
        for key in range(1, max(turn_dict.keys())+1):
            if key in turn_dict.keys():
                curr_ships += (key-last_key) * src_planet.growth_rate
                list_flee = turn_dict.get(key)
                curr_enemy_ships = sum([f.num_ships for f in list_flee])
                last_key = key
                if curr_ships<curr_enemy_ships:
                    return False
                curr_ships -= curr_enemy_ships

        return True


    def get_max_num_ship(self,game:PlanetWars):
        return max([p.num_ships for p in self.get_my_planets(game)])

    def play_turn(self, game: PlanetWars) -> Iterable[Order]:
        """
        See player.play_turn documentation.
        :param game: PlanetWars object representing the map - use it to fetch all the planets and flees in the map.
        :return: List of orders to execute, each order sends ship from a planet I own to other planet.
        """
       #  possible_attacks = [(src, dst, num_ships, rank)]
        possible_attacks = []
        orders = []
        self.get_max(game)
        for dst_planet in self.get_planets_to_attack(game):

            for my_planet in self.get_my_planets(game):


                dist = dst_planet.distance_between_planets(my_planet, dst_planet)

                growth_rate = dst_planet.growth_rate
                growth_factor = (dist * growth_rate) if dst_planet.owner == PlanetWars.ENEMY else 0

                num_curr_target_ships = dst_planet.num_ships
                curr_inflight_fleet_factor = self.curr_inflight_fleet_factor(dst_planet, dist, game)
                # curr_inflight_fleet_factor = 0
                ships_to_send_thres = num_curr_target_ships + growth_factor + curr_inflight_fleet_factor +1

                if ships_to_send_thres < 0:
                    print(ships_to_send_thres)
                if my_planet.num_ships > ships_to_send_thres:
                    rank = 10*(dst_planet.growth_rate/self.MAX_GROWTH) +1/(1000*(dist/self.MAX_DIST)) \
                           - (ships_to_send_thres / my_planet.num_ships) - \
                           (dst_planet.num_ships/self.get_max_num_ship(game))

                    possible_attacks.append((my_planet, dst_planet, ships_to_send_thres, rank))

                # if my_planet.num_ships >= ships_to_send_thres:
                #     rank = (dst_planet.growth_rate / self.MAX_GROWTH) - 10000 * (dist / self.MAX_DIST) \
                #            - (ships_to_send_thres / my_planet.num_ships) - (dst_planet.num_ships/self.get_max_num_ship(game))
                #     possible_attacks.append((my_planet, dst_planet, ships_to_send_thres, rank))


        # sort attacks by rank
        possible_attacks.sort(key=lambda x: x[3], reverse=True)
        # TODO: possible defends??
        # attck_idx = 0
        # print(len(possible_attacks))
        for attack in possible_attacks:
            # if attck_idx < self.NUM_ATTACKS:
            if self.can_leave_planet(game, attack[0], attack[2]):
                orders.append(Order(attack[0], attack[1], attack[2]))
                # attck_idx += 1
        return orders



def view_bots_battle():
    """
    Runs a battle and show the results in the Java viewer

    Note: The viewer can only open one battle at a time - so before viewing new battle close the window of the
    previous one.
    Requirements: Java should be installed on your device.
    """
    map_str = get_random_map()
    # run_and_view_battle(AttackWeakestPlanetFromStrongestBot(), AttackEnemyWeakestPlanetFromStrongestBot(), map_str)
    # run_and_view_battle(TeamRocketBot(), AlexDavidBot(), map_str)
    results=[]
    for i in range(100):
        map_str = get_random_map()
        run_and_view_battle(TeamRocketBot(), AlexDavidBot(), map_str)
    print(f'Player 1 wins: {len([result for result in results if result == 1])}, Player 2 wins {len([result for result in results if result == 2])}')


def check_bot():
    """
    Test AttackWeakestPlanetFromStrongestBot against the 2 other bots.
    Print the battle results data frame and the PlayerScore object of the tested bot.
    So is AttackWeakestPlanetFromStrongestBot worse than the 2 other bots? The answer might surprise you.
    """
    maps = [get_random_map(), get_random_map()]
    player_bot_to_test = TeamRocketBot()
    tester = TestBot(
        player=player_bot_to_test,
        competitors=[
            AlexDavidBot(),
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
    #view_bots_battle()