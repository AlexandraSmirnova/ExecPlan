
class BranchAndBoundAlgorithm(object):
    def __init__(self, operators):
        self.operators = operators
        self.individ = None
        self.best = None
        self.statistic = []

    def run(self):
        self.individ = self.operators.create_individ()
        self.best = self.operators.fitness(self.individ)
        self.statistic.append(self.best)
        self.branch([])
        return self.statistic

    def branch(self, path=None):
        solutions = [x for x in range(self.operators.task_count) if x not in path]

        for solution in solutions:
            new_path = path + list([solution])
            low_boundary = self.operators.fitness(new_path) + (self.operators.task_count - len(new_path))
            if low_boundary < self.best and self.operators.predecessors_included(new_path, solution):
                print new_path
                if len(solutions) == 1:
                    self.individ = new_path
                    self.best = low_boundary
                    self.statistic.append(self.best)
                else:
                    self.branch(new_path)




