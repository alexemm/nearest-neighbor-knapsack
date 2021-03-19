from utils import read_csv
from nn_knapsack import search_optimal_local_solution

def test():
    file_name = "test/data0.csv"
    problem = read_csv(file_name)
    search_optimal_local_solution(frozenset({"1","2","3","4","6"}), problem, 12, True)


test()
