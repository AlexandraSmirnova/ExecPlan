import copy


class BranchAndBoundAlgorithm(object):
    def __init__(self, operators):
        self.operators = operators
        self.individ = None
        self.best_fit = None
        self.best_time = None
        self.count = self.operators.task_count
        self.statistic = {'best_fit': [], 'data_dict': None}

    def run(self):
        from scheduling.algorithms.helpers import prepare_data_for_gantt

        self.individ = self.operators.create_individ()
        self.best_fit = self.operators.fitness(self.individ)

        self.statistic['best_fit'].append(self.best_fit)
        self.branch([])
        self.statistic['data_dict'] = prepare_data_for_gantt(self.operators.decode_chromosome(self.individ))
        return self.statistic

    def branch(self, path=None):

        solutions = [x for x in range(self.count) if x not in path]

        for solution in solutions:
            new_path = path + list([solution])
            if not self.operators.predecessors_included(new_path, solution) or not self.operators.check_deadline(new_path):
                continue

            fitness = self.operators.fitness(new_path)
            multipy = 1.0 if self.count - len(new_path) else 0.0
            low_boundary = fitness + (self.count - len(new_path)) * multipy
            self.statistic['best_fit'].append(self.best_fit)

            if low_boundary >= self.best_fit:
                continue

            if len(solutions) == 1:
                self.individ = new_path
                self.best_fit = copy.copy(fitness)
                self.statistic['best_fit'][-1] = self.best_fit

            else:
                self.branch(new_path)

    def branch2(self):

        solutions = [[]]

        while len(solutions) > 0 and len(solutions[0]) != self.count:
            new_solutions = []

            for solution in solutions:
                next_path = [x for x in range(self.count) if x not in solution]

                for path in next_path:
                    new_path = solution + [path]
                    self.statistic['best_fit'].append(self.best_fit)

                    if not self.operators.predecessors_included(new_path, path):
                        continue

                    fitness = self.operators.fitness(new_path)
                    multipy = 1 if self.count - len(new_path) else 0
                    low_boundary = fitness + (self.count - len(new_path)) * multipy

                    if low_boundary >= self.best_fit:
                        continue

                    new_solutions.append(new_path)
                    if len(new_path) == self.count:
                        self.individ = new_path
                        self.best_fit = copy.copy(fitness)
                        self.statistic['best_fit'][-1] = self.best_fit

            solutions = new_solutions



