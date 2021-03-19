from operator import itemgetter
from typing import FrozenSet, List, Set, Union, Optional, Tuple

name: int = 0
weight: int = 1
profit: int = 2


class Solution:

    def __init__(self, package: FrozenSet[str], instance: List[List[Union[str, int]]], capacity: int, step: int):
        self.step: int = step
        self.package: FrozenSet[str] = package
        self.instance: List[List[str]] = instance
        self.profit: float = calculate_profit(package, instance)
        self.weight: float = calculate_weight(package, instance)
        self.feasible: bool = capacity > self.weight

    def __lt__(self, other):
        if other is None:
            # 'Nothing' is better than a non-feasible solution
            return not self.feasible
        return not self.feasible or (self.profit < other.profit and other.feasible)

    def __gt__(self, other):
        return other < self

    def __eq__(self, other):
        if isinstance(other, FrozenSet):
            # to save the calculations for profit and weight if there is already an instance
            return other == self.package
        return self.package == other.package

    def __hash__(self):
        return hash(self.package)

    def __or__(self, other):
        return Solution

    def __str__(self):
        return "%s" % set(self.package)

    def get_information(self) -> str:
        return f"{str(self.package)}: profit:{self.profit}, weight:{self.weight}, feasible:{self.feasible}"


def calculate_profit(packed_items: FrozenSet[str], instance: List[List[str]]) -> float:
    return sum(item[profit] for item in instance if item[name] in packed_items)


def calculate_weight(packed_items: FrozenSet[str], instance: List[List[str]]) -> float:
    return sum(item[weight] for item in instance if item[name] in packed_items)


def analyze_solution(optimal_solution, next_package, pieces, instance, capacity, step, cache, print_output):
    if print_output:
        print("%s" % pieces)
    query = lookup_solution(next_package, cache)
    if query is not None:
        if print_output:
            print("%s: refer to step %i" % (set(query.package), query.step))
    else:
        solution: Solution = Solution(next_package, instance, capacity, step)
        cache.add(solution)
        if print_output:
            print(solution.get_information())
        if optimal_solution < solution:
            optimal_solution = solution
    return optimal_solution, cache


def remove(curr_sol, instance, capacity, cache: Set[Solution], step, print_output) -> Tuple[
    str, Solution, Optional[str], Set[Solution]]:
    optimal_solution: Solution = curr_sol
    removed_piece: Optional[str] = None
    if print_output:
        print("Removal")
    for curr_rem_piece in curr_sol.package:
        next_package: FrozenSet[str] = curr_sol.package - {curr_rem_piece}
        analyzed_solution, cache = analyze_solution(optimal_solution, next_package, curr_rem_piece, instance, capacity,
                                                    step, cache, print_output)
        if optimal_solution != analyzed_solution:
            optimal_solution = analyzed_solution
            removed_piece = curr_rem_piece
    return "remove", optimal_solution, removed_piece, cache


def add(curr_sol, instance, capacity, cache, step, print_output) -> Tuple[str, Solution, Optional[str], Set[Solution]]:
    optimal_solution: Solution = curr_sol
    added_piece: Optional[str] = None
    if print_output:
        print("Addition")
    for curr_add_piece in get_item_names(instance) - curr_sol.package:
        next_package: FrozenSet[str] = curr_sol.package | {curr_add_piece}
        analyzed_solution, cache = analyze_solution(optimal_solution, next_package, curr_add_piece, instance, capacity,
                                                    step, cache, print_output)
        if optimal_solution != analyzed_solution:
            optimal_solution = analyzed_solution
            added_piece = curr_add_piece
    return "add", optimal_solution, added_piece, cache


def replace(curr_sol, instance, capacity, cache, step, print_output) -> Tuple[
    str, Solution, Optional[str], Set[Solution]]:
    optimal_solution: Solution = curr_sol
    replaced_pieces: Optional[str] = None
    if print_output:
        print("Replacement")
    for curr_add_piece in get_item_names(instance) - curr_sol.package:
        for curr_rm_piece in curr_sol.package:
            next_package: FrozenSet[str] = (curr_sol.package - {curr_rm_piece}) | {curr_add_piece}
            curr_repl_piece: str = f"{curr_rm_piece}, {curr_add_piece}"
            analyzed_solution, cache = analyze_solution(optimal_solution, next_package, curr_repl_piece, instance,
                                                        capacity,
                                                        step, cache, print_output)
            if optimal_solution != analyzed_solution:
                optimal_solution = analyzed_solution
                replaced_pieces = curr_repl_piece
    return "replace", optimal_solution, replaced_pieces, cache


def get_item_names(instance: List[List[Union[str, int]]]) -> FrozenSet[str]:
    return frozenset(item[name] for item in instance)


def lookup_solution(solution: Union[FrozenSet[str], Solution], cache: Set[Solution]) -> Optional[Solution]:
    for tmp_solution in cache:
        if tmp_solution == solution:
            return tmp_solution
    return None


def find_best_option(curr_sol, instance: List[List[Union[str, int]]], capacity: int, cache: Set[Solution], step: int,
                     print_output: bool) -> Tuple[str, Solution]:
    best_options: List[Tuple[str, Solution]] = []
    for func in [remove, add, replace]:
        # if print_output:
        # print("%s:\n" % func.__name__)
        option, optimal_solution, pieces, cache = func(curr_sol, instance, capacity, cache, step, print_output)
        best_options.append((option, optimal_solution, pieces))
    return max(best_options, key=itemgetter(1))


def search_optimal_local_solution(initial_set: FrozenSet[str], instance: List[List[Union[str, int]]], capacity: int,
                                  print_output: bool) -> Optional[Solution]:
    step: int = 0
    initial_solution = Solution(initial_set, instance, capacity, step)
    cache: Set[Solution] = {initial_solution}
    curr_sol = initial_solution
    optimal_solution: Solution = initial_solution if initial_solution.feasible else None
    if print_output:
        print(curr_sol.get_information())
    while True:
        step += 1
        if print_output:
            print("Step %i" % step)
        best_option = find_best_option(curr_sol, instance, capacity, cache, step, print_output)
        if not best_option[1].feasible or best_option[1] < optimal_solution or best_option[2] is None:
            break
        optimal_solution = best_option[1]
        curr_sol = optimal_solution
        if print_output:
            print("We %s %s\n" % (best_option[0], best_option[2]))

    if print_output:
        if optimal_solution is not None:
            print("The best solution is %s with a profit of %f and weights of %f" % (
                optimal_solution.package, optimal_solution.profit, optimal_solution.weight))
        else:
            print("There is no feasible solution!")
    return optimal_solution
