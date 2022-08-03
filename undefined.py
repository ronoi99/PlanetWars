from typing import Iterable, List

import pandas as pd

from baseline_bot import AttackWeakestPlanetFromStrongestBot, AttackEnemyWeakestPlanetFromStrongestBot, \
    AttackWeakestPlanetFromStrongestSmarterNumOfShipsBot, get_random_map
from planet_wars.battles.tournament import run_and_view_battle, TestBot
from planet_wars.planet_wars import Player, PlanetWars, Order, Planet,Fleet

class Undefined(Player):

    def get_enemy_fleets(self, game: PlanetWars) -> List[Fleet]:
        return [f for f in game.fleets if f.owner != PlanetWars.ME]

    def get_planets_to_attack(self, game: PlanetWars) -> List[Planet]:
        return [p for p in game.planets if p.owner != PlanetWars.ME]

    def attackAfterEnemyFleet(self, game: PlanetWars) -> List[Order]:
        orders = []
        my_planets = game.get_planets_by_owner(owner=PlanetWars.ME)
        planets_to_attack = self.get_planets_to_attack(game)
        my_fleets = game.get_fleets_by_owner(owner=PlanetWars.ME)
        enemy_fleets = self.get_enemy_fleets(game)
        my_fleets_planets = list(map(lambda fleet: fleet.source_planet_id, my_fleets))
        for e_fleet in enemy_fleets:
            dest_planet = game.get_planet_by_id(e_fleet.destination_planet_id)
            for my_planet in my_planets:
                if e_fleet.turns_remaining < my_planet.distance_between_planets(my_planet, dest_planet) < 17 :
                    if(my_planet.num_ships // 2> 20 and my_planet.num_ships // 2 > e_fleet.num_ships):
                        orders.append(Order(my_planet, dest_planet, e_fleet.num_ships+1))
        return orders

    def attackWeakNeutralFirstTurn(self,game: PlanetWars) -> List[Order]:
        orders = []
        get_all_natural_planets = [p for p in game.get_planets_by_owner(0)]
        get_all_my_planets = [p for p in game.get_planets_by_owner(1)]
        enemy_planets = [p for p in game.get_planets_by_owner(2)]
        neutral_small_planets =sorted([ p for p in get_all_natural_planets if p.num_ships<=25 and p.growth_rate >=2 ],key=lambda p: p.num_ships)
        my_fleets = game.get_fleets_by_owner(owner=PlanetWars.ME)
        my_fleets_planets = list(map(lambda fleet: fleet.source_planet_id, my_fleets))
        for p in neutral_small_planets:
            if get_all_my_planets[0].planet_id not in my_fleets_planets:
                if len(enemy_planets) > 0:
                    if get_all_my_planets[0].distance_between_planets(get_all_my_planets[0], p) < enemy_planets[0].distance_between_planets(enemy_planets[0], p):
                        orders.append(Order(get_all_my_planets[0],p,p.num_ships+10))
                elif get_all_my_planets[0].distance_between_planets(get_all_my_planets[0], p) < 14:
                    orders.append(Order(get_all_my_planets[0],p,p.num_ships+1))
        return orders

    def play_turn(self, game: PlanetWars) -> Iterable[Order]:
        orders = []
        # My planets
        my_planets = game.get_planets_by_owner(owner=PlanetWars.ME)
        # Enemy / Neutral planets
        planets_to_attack = self.get_planets_to_attack(game)
        # Neutral planets
        neutral_planets = [p for p in game.get_planets_by_owner(0)]
        enemy_planets = [p for p in game.get_planets_by_owner(2)]
        # My fleets
        my_fleets = game.get_fleets_by_owner(owner=PlanetWars.ME)
        # Enemy fleets
        enemy_fleets = self.get_enemy_fleets(game)
        # Enemy fleets to my planets
        # =============================================
        if len(my_planets) > 0:
            short_enemy_fleets_to_me = [f for f in enemy_fleets if f.destination_planet_id == my_planets[0].planet_id and f.turns_remaining <= 5]
            if(0 < game.turns < 5 and len(short_enemy_fleets_to_me) == 0):
                return self.attackWeakNeutralFirstTurn(game)
        orders = orders + self.attackAfterEnemyFleet(game)
        # =============================================
        my_fleets = game.get_fleets_by_owner(owner=PlanetWars.ME)
        my_fleets_planets = list(map(lambda fleet: fleet.destination_planet_id, my_fleets))
        my_spaceships = sum([p.num_ships for p in my_planets])
        if(game.turns >= 5):
            for p in my_planets:
                good_neutral_planets = [p for p in neutral_planets if p.growth_rate > 1]
                relative_weak_planets = [n_p for n_p in good_neutral_planets if n_p.num_ships <= p.num_ships*0.2 and n_p.distance_between_planets(n_p,p)<15]
                if len(relative_weak_planets) == 0:
                    relative_weak_planets = [n_p for n_p in good_neutral_planets if n_p.num_ships <= p.num_ships*0.4 and n_p.distance_between_planets(n_p,p)<15]
                if len(relative_weak_planets) == 0:
                    relative_weak_planets = [n_p for n_p in good_neutral_planets if n_p.num_ships <= p.num_ships*0.5 and n_p.distance_between_planets(n_p,p)<15]
                relative_weak_planets = sorted(relative_weak_planets, key = lambda p: p.num_ships)
                for rw_p in relative_weak_planets:
                    if rw_p.planet_id not in my_fleets_planets:
                        orders.append(Order(p,rw_p,rw_p.num_ships+5))
        # =============================================
            my_planets_ships = [p.num_ships for p in my_planets]
            my_planets_ids = [p.planet_id for p in my_planets]
            for o in orders:
                index = my_planets_ids.index(o.source_planet_id)
                my_planets_ships[index] -= o.num_ships
            if len(enemy_planets) > 0:
                my_planets_ships_sum = sum(my_planets_ships)
                for p in my_planets_ships:
                    index = my_planets_ships.index(p)
                    weak_enemies = [e_p for e_p in enemy_planets if e_p.num_ships < my_planets_ships_sum * .15]
                    if len(weak_enemies)>0:
                        weakest_enemy = min(enemy_planets, key=lambda planet: planet.num_ships)
                        if p > my_planets_ships_sum * .15:
                            orders.append(Order(my_planets[index], weakest_enemy, my_planets[index].num_ships // 4))
        return orders
        
   


       










def view_bots_battle():
    """
    Runs a battle and show the results in the Java viewer

    Note: The viewer can only open one battle at a time - so before viewing new battle close the window of the
    previous one.
    Requirements: Java should be installed on your device.
    """
    map_str = get_random_map()
    run_and_view_battle(Undefined(), AttackEnemyWeakestPlanetFromStrongestBot(), map_str)


def check_bot():
    """
    Test AttackWeakestPlanetFromStrongestBot against the 2 other bots.
    Print the battle results data frame and the PlayerScore object of the tested bot.
    So is AttackWeakestPlanetFromStrongestBot worse than the 2 other bots? The answer might surprise you.
    """
    maps = [get_random_map(), get_random_map()]
    player_bot_to_test = Undefined()
    tester = TestBot(
        player=player_bot_to_test,
        competitors=[
            AttackEnemyWeakestPlanetFromStrongestBot(), AttackEnemyWeakestPlanetFromStrongestBot()
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
