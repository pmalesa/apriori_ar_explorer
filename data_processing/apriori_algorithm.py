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

        # self.__vectorized_data = []

    def run(self, row_data: list = [], unique_items = None):
        self.__row_data = row_data
        self.__unique_items = unique_items

        self.__find_frequent_sets()
        # self.__find_strong_association_rules()


        # print(unique_items)
    
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
            print(f"    |---- {len(self.__frequent_sets[current_level])} frequent sets found.")
            current_level += 1

        print(self.__get_frequent_sets(5))

    def __find_strong_association_rules(self):
        self.__strong_association_rules = []
        if self.__frequent_sets == None or len(self.__frequent_sets) == 0:
            return
        
        pass

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
