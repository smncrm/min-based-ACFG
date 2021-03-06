import itertools
import numpy as np


class Structure:
    def __init__(self, collection):
        self.struct = self.freeze(collection)

    def __str__(self):
        return str(self.unfreeze(self.struct))

    def __repr__(self):
        return str(self.unfreeze(self.struct))

    def __hash__(self):
        return self.struct.__hash__()

    def __eq__(self, other):
        return self.__hash__() == other.__hash__()

    def freeze(self, struct):
        """
        converts coalition structure to a frozenset to be hashable.
        :param struct: A collection of collections.
        :return: The frozenset version.
        """
        return frozenset(map(frozenset, struct))

    def unfreeze(self, frozen_struct):
        """
        converts a frozenset back to a mutable collection.
        :param frozen_struct: A frozen coalition structure.
        :return: A list object representing the structure.
        """
        return list(map(list, frozen_struct))

    def move_coalition(self, coalition):
        """
        moves all players in coalition from their original coalition
        to form a new one.
        :param coalition: The new coalition to form.
        :return: The new coalition structure.
        """
        structure = self.unfreeze(self.struct)
        new_structure = [remove_players(c, coalition)
                         for c in structure] + [coalition]
        filtered = list(filter(None, new_structure))
        return Structure(filtered)

    def check_blocking_coalition(self, dic, coalition):
        """
        checks whether the coalition blocks the structure.
        :param dic: Dict containing all utilities for all structures.
        :param coalition: The coalition to check.
        :return: True if the coalition blocks the structure.
        """
        new_structure = self.move_coalition(coalition)

        for p in coalition:
            if dic[self][p] >= dic[new_structure][p]:
                return False
        return True

    def check_weakly_blocking_coalition(self, dic, coalition):
        """
        checks whether the coalition weakly blocks the structure.
        :param dic: Dict containing all utilities for all structures.
        :param coalition: The coalition to check.
        :return: True if the coalition weakly blocks the structure.
        """
        new_structure = self.move_coalition(coalition)

        happier_player_flag = False

        for p in coalition:
            if dic[self][p] > dic[new_structure][p]:
                return False
            if dic[self][p] < dic[new_structure][p]:
                happier_player_flag = True
        return happier_player_flag

    def is_core_stable(self, dic, all_cs, strict=False):
        """
        checks whether the structure is core stable.
        :param dic: Dict containing all utilities for all structures.
        :param all_cs: List of all possible coalitions.
        :param strict: 'True' checks for strict core stability.
        :return: True if the structure is core stable.
        """
        for c in all_cs:
            if strict:
                if self.check_weakly_blocking_coalition(dic, c):
                    return False
            else:
                if self.check_blocking_coalition(dic, c):
                    return False
        return True


def partition(collection):
    """
    https://stackoverflow.com/questions/19368375/set-partitions-in-python
    :param collection: A collection.
    :return: A collection of all possible partitions.
    """
    if len(collection) == 1:
        yield [collection]
        return

    first = collection[0]
    for smaller in partition(collection[1:]):
        # insert `first` in each of the subpartition's subsets
        for n, subset in enumerate(smaller):
            yield smaller[:n] + [[first] + subset] + smaller[n + 1:]
        # put `first` in its own subset
        yield [[first]] + smaller


def remove_players(coalition, players_to_remove):
    """
    removes all given players from the coalition.
    :param coalition: List representing a coalition.
    :param players_to_remove: List of players to remove.
    :return: The coalition without the removed players.
    """
    return [p for p in coalition if p not in players_to_remove]


def find_coalition(structure, player):
    """
    finds the coalition that contains the given player.
    :param structure: The coalition structure.
    :param player: The player to find.
    :return: The coalition containing the player.
    """
    return [c for c in structure if player in c][0]


def calc_value(coalition, n, player, friends):
    """
    calculates the value of the given coalition for the given player.
    :param coalition: The coalition.
    :param n: Number of players in the game.
    :param player: The player to consider.
    :param friends: The player's friends.
    :return: The numerical value the player assigns to the coalition.
    """
    v = 0
    for p in coalition:
        if p == player:
            continue
        elif p in friends:
            v += n
        else:
            v -= 1
    return v


def calc_utility(structure, n, player, F, degree='SF'):
    """
    calculates the utility of the structure for the given player.
    :param structure: A coalition structure.
    :param n: The number of players in total.
    :param player: The player to consider.
    :param F: The network of friends.
    :param degree: The degree of altruism to use.
    :return: The utility the player assigns to the structure.
    """
    M = n ** 2

    c = find_coalition(structure, player)
    own_value = calc_value(c, n, player, F[player])
    vs_friends = [calc_value(find_coalition(structure, friend),
                             n, friend, F[friend])
                  for friend in F[player]]
    min_value_friends = min(vs_friends) if len(vs_friends) != 0 \
                                        else 0

    if degree == 'SF':
        return M * own_value \
               + min_value_friends

    if degree == 'EQ':
        return min([own_value, min_value_friends])

    if degree == 'AL':
        return own_value \
               + M * min_value_friends


def calc_all_utilities(N, F, degree='SF'):
    """
    calculates a dict containing all possible structure and their
    utilities for each player.
    :param N: The set of players.
    :param F: The network of friends.
    :param degree: The degree of altruism.
    :return: A dict with all possible structures as keys and the
             respective list of utilities of each player as values.
    """
    n = len(N)
    partitions = enumerate(partition(list(N)), 1)
    dic = dict()

    for i, p in partitions:
        uts = []
        for player in N:
            uts.append(calc_utility(p, n, player, F, degree=degree))
        dic[Structure(p)] = uts
    return dic


def find_all_coalitions(N):
    """
    finds all subsets of the set of players.
    :param N: The set of players.
    :return: A list containing all possible coalitions.
    """
    res = []
    for m in range(len(N) - 1):
        res += (list(itertools.combinations(N, m + 1)))
    return res


def find_core_stable_structure(N, F, dic=None, degree='SF', strict=False):
    """
    checks all possible coalition structures in the given ACFG
    for a core-stable coalition structure.
    :param N: The set of players.
    :param F: The network of friends.
    :param dic: The dict containing all structures and utilities.
                If 'None', it is computed.
    :param degree: The degree of altruism.
    :param strict: 'True' looks for a strict core stable structure.
    :return: The first core-stable structure in dic,
            'None' if there is none.
    """
    all_cs = find_all_coalitions(N)

    if dic is None:
        dic = calc_all_utilities(N, F, degree=degree)

    for struct in dic.keys():
        if struct.is_core_stable(dic, all_cs, strict=strict):
            return struct

    return None


def compare_structures(uts_gamma, uts_delta):
    """
    compares two structures regarding their popularity.
    :param uts_gamma: The utilities of the first structure.
    :param uts_delta: The utilities of the second structure.
    :return: 1 (-1) if Gamma (Delta) is more popular,
             0 if equally popular.
    """
    s = sum([np.sign(a - b) for a, b in zip(uts_gamma, uts_delta)])
    return np.sign(s)


def find_popular_structure(N, F, dic=None, degree='SF', strict=False):
    """
    checks all possible structures for a (strictly) popular one.
    :param N: The set of players.
    :param F: The network of friends.
    :param dic: The dict containing all structures and utilities.
                If 'None', it is computed.
    :param degree: The degree of altruism.
    :param strict: If True, checks for a strictly popular structure.
    :return: The first (strictly) popular structure in dic,
            'None' if there is none.
    """
    if dic is None:
        dic = calc_all_utilities(N, F, degree=degree)

    for struct1, uts1 in dic.items():
        res = True
        for struct2, uts2 in dic.items():
            if struct1 == struct2:
                continue
            if strict:
                if compare_structures(uts1, uts2) != 1:
                    res = False
                    break
            else:
                if compare_structures(uts1, uts2) < 0:
                    res = False
                    break

        if res:
            return struct1

    return None
