import copy
from scheduling.algorithms.helpers import get_dict_for_gantt


class BranchAndBoundAlgorithm(object):
    def __init__(self, operators):
        self.operators = operators
        self.individ = None
        self.best = None
        self.statistic = {'best': [], 'data_dict': None}

    def run(self):
        self.individ = self.operators.create_individ()
        self.best = self.operators.fitness(self.individ)
        self.statistic['best'].append(self.best)
        self.branch([])
        self.statistic['data_dict'] = get_dict_for_gantt(self.operators.decode_chromosome(self.individ))
        return self.statistic

    def branch(self, path=None):
        solutions = [x for x in range(self.operators.task_count) if x not in path]

        for solution in solutions:
            new_path = path + list([solution])
            fitness = self.operators.fitness(new_path)
            multipy = 1 if self.operators.task_count - len(new_path) else 0
            low_boundary = fitness + (self.operators.task_count - len(new_path)) * multipy
            if low_boundary < self.best and self.operators.predecessors_included(new_path, solution):
                if len(solutions) == 1:
                    self.individ = new_path
                    self.best = self.best = copy.copy(fitness)
                else:
                    self.branch(new_path)
            self.statistic['best'].append(self.best)