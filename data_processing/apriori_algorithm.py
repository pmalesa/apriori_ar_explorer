from itertools import combinations
import math

class Apriori:
    def __init__(self, min_sup: int = None, min_conf: float = None):
        self.__min_sup = min_sup
        self.__min_conf = min_conf

        self.__row_data = []
        self.__unique_items = {}

        self.__frequent_sets = {}
        self.__strong_association_rules = [] # list of pairs of sets [(X, Y)], where X and Y are sets

        self.__sup_cache = {}
        self.__conf_cache = {}

        self.__n_transactions = 0

    def run(self, row_data: list = [], unique_items = None):
        self.__row_data = row_data
        self.__n_transactions = len(self.__row_data)
        self.__unique_items = unique_items
        self.__find_frequent_sets()
        self.__find_strong_association_rules()

        # Return an object of all strong association rules with calculated metrics

        rule = self.__strong_association_rules[0]
        print(self.__strong_association_rules[0])
        print(f"SUP: {self.__sup(rule[0] | rule[1])}")
        print(f"rSUP: {self.__rsup(rule[0] | rule[1])}")
        print(f"CONF: {self.__conf(rule[0], rule[1])}")
        print(f"LIFT: {self.__lift(rule[0], rule[1])}")
        print(f"COSINE: {self.__cosine(rule[0], rule[1])}")
        print(f"JACCARD: {self.__jaccard(rule[0], rule[1])}")
        print(f"CF: {self.__certainty_factor(rule[0], rule[1])}")

        # return self.__strong_association_rules
    
    # TODO
    def __create_list_of_strong_rules_with_metrics(self):
        pass

    def __find_frequent_sets(self):
        self.__frequent_sets = {}

        # Initialize by setting the frequent sets of size 0 and 1
        self.__add_frequent_set({})
        current_level = 1
        for item in self.__unique_items:
            temp_set = {item}
            if self.__is_frequent(temp_set):
                self.__add_frequent_set(temp_set)

        # Loop over frequent sets for size equal to current_level
        while current_level in self.__frequent_sets:
            print(f"[INFO] Searching for candidates of size {current_level}")
            current_level_frequent_sets = self.__get_frequent_sets(current_level)      

            for i in range(len(current_level_frequent_sets)):
                for j in range(i + 1, len(current_level_frequent_sets)):
                    set1 = current_level_frequent_sets[i]
                    set2 = current_level_frequent_sets[j]

                    # Merge two sets if they have k - 1 items in common
                    if len(set1.intersection(set2)) == current_level - 1:
                        new_candidate = set1.union(set2)
                        if len(new_candidate) == current_level + 1:
                            if self.__is_frequent(new_candidate):
                                self.__add_frequent_set(new_candidate)
            print(f"    |---- Done. found {len(self.__frequent_sets[current_level])}.")
            current_level += 1

    def __find_strong_association_rules(self):
        if self.__frequent_sets == None or len(self.__frequent_sets) == 0:
            return

        self.__strong_association_rules = []
        current_level = 1
        while current_level in self.__frequent_sets:
            n = 0
            print(f"[INFO] Searching for strong rules of size {current_level}.")
            current_level_frequent_sets = self.__get_frequent_sets(current_level)      

            for frequent_set in current_level_frequent_sets:
                all_rule_combinations = self.__generate_combinations(frequent_set)

                for rule in all_rule_combinations:
                    if self.__is_strong_ar(rule[0], rule[1]):
                        self.__strong_association_rules.append(rule)
                        n += 1
            
            print(f"    |---- Done. Found {n}.")
            current_level += 1

        print(f"[INFO] {len(self.__strong_association_rules)} strong association rules found in total.")

    def __get_frequent_sets(self, size: int):
        if size not in self.__frequent_sets:
            return []
        
        frequent_sets_frozen = self.__frequent_sets[size]
        frequent_sets_unfrozen = []

        for frozen_set in frequent_sets_frozen:
            frequent_sets_unfrozen.append(set(frozen_set))

        return frequent_sets_unfrozen

    def __add_frequent_set(self, X: set):
        size = len(X)
        if size not in self.__frequent_sets:
            self.__frequent_sets[size] = {frozenset(X)}
        else:
            self.__frequent_sets[size].add(frozenset(X))

    def __generate_combinations(self, X: set):
        all_combinations = []
        for r in range(1, len(X)):
            for subset in combinations(X, r):
                all_combinations.append((set(subset), X - set(subset)))
        return all_combinations

    def __is_frequent(self, X: set):
        return True if self.__sup(X) >= self.__min_sup else False

    def __is_strong_ar(self, X: set, Y: set):
        return True if self.__conf(X, Y) >= self.__min_conf and self.__is_frequent(X | Y) else False

    def __sup(self, X: set, Y = None) -> int:
        if X == None:
            return -1
        
        if len(X) == 0:
            X = set()
        if Y == None or len(Y) == 0:
            Y = set()

        union = X | Y

        # Retrieve cached value if present
        if frozenset(union) in self.__sup_cache:
            return self.__sup_cache[frozenset(union)]

        sup = 0
        for row_set in self.__row_data:
            if union.issubset(row_set):
                sup += 1

        # Cache value
        self.__sup_cache[frozenset(union)] = sup

        return sup
    
    def __rsup(self, X: set, Y = None) -> float:
        return self.__sup(X, Y) / self.__n_transactions

    def __conf(self, X: set, Y: set):
        if X == None or Y == None:
            return -1
        
        if len(X) == 0:
            X = set()
        if len(Y) == 0:
            Y = set()

        rule = (frozenset(X), frozenset(Y))

        # Retrieve cached value if present
        if rule in self.__conf_cache:
            return self.__conf_cache[rule]
        
        conf = float(self.__sup(X, Y) / self.__sup(X))

        # Cache value
        self.__conf_cache[rule] = conf

        return conf
    
    def __lift(self, X: set, Y: set):
        if X == None or Y == None:
            return -1
        
        if len(X) == 0:
            X = set()
        if len(Y) == 0:
            Y = set()

        lift = self.__conf(X, Y) / self.__rsup(Y)

        return lift
    
    def __cosine(self, X: set, Y: set):
        if X == None or Y == None:
            return -1
        
        if len(X) == 0:
            X = set()
        if len(Y) == 0:
            Y = set()

        return self.__rsup(X, Y) / math.sqrt(self.__rsup(X) * self.__rsup(Y))

    def __jaccard(self, X: set, Y: set):
        if X == None or Y == None:
            return -1
        
        if len(X) == 0:
            X = set()
        if len(Y) == 0:
            Y = set()

        return self.__rsup(X, Y) / (self.__rsup(X) + self.__rsup(Y) - self.__rsup(X, Y))

    def __certainty_factor(self, X: set, Y: set):
        if X == None or Y == None:
            return -1
        
        if len(X) == 0:
            X = set()
        if len(Y) == 0:
            Y = set()

        prob_Y = self.__rsup(Y)
        conf_XY = self.__conf(X, Y)

        if conf_XY > prob_Y:
            return (conf_XY - prob_Y) / (1 - prob_Y)
        elif conf_XY == prob_Y:
            return 0
        else:
            return -1 * ((prob_Y - conf_XY) / prob_Y)