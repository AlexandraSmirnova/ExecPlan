# coding=utf-8
import random
import copy


class GeneticAlgorithm(object):
    def __init__(self, probability_crossover=0.8, population_size=20, limit=200):
        self.probability_crossover = probability_crossover
        self.population_size = population_size
        self.counter = 0
        self.limit = limit

    def run(self):
        population = self.create_initial()
        statistic = {'best_fit': [], 'ave_fit': []}
        while True:
            fits = [(self.fitness(ch),  ch) for ch in population]
            best, ave = self.get_statistic(fits)
            statistic['best_fit'].append(best)
            statistic['ave_fit'].append(ave)
            if self.check_end(fits):
                break
            population = self.next(fits)
        return statistic

    def next(self, fits):
        parents_generator = self.parents(fits)
        nexts = list()
        nexts.append(min(fits)[1])
        while len(nexts) < len(fits):
            parents = parents_generator.next()
            rand = random.random()
            cross = rand < self.probability_crossover
            child = self.crossover(parents) if cross else self.mutation(parents[0])
            nexts.append(child)
        return nexts

    def create_initial(self):
        return []

    def parents(self, fits_populations):
        pop = self.fitness_scaling(fits_populations)
        while True:
            ch1, ch2 = None, None
            for i in range(0, len(pop) - 1, 2):
                f1, ch1 = pop[i]
                f2, ch2 = pop[i + 1]
            yield (ch1, ch2)

    def fitness(self, chromosome):
        return max(chromosome)

    def crossover(self, parents):
        return parents

    def mutation(self, chromosome):
        return chromosome

    def check_end(self, fits):
        return True

    def fitness_scaling(self, fits):
        # return sorted(fits, key=lambda x: x[0])
        return self.rank_scaling(fits)

    @staticmethod
    def rank_scaling(fits):
        n = len(fits)
        dividend = (n + 1) * n / 2
        sorted_s = sorted(fits, key=lambda x: x[0])
        result = []
        for i in range(len(sorted_s)):
            result.append((dividend / (i + 1), sorted_s[i][1]))
        return result

    @staticmethod
    def tournament(fits_population):
        alicef, alice = random.choice(fits_population)
        bobf, bob = random.choice(fits_population)
        return alice if alicef < bobf else bob

    @staticmethod
    def roulette(fits):
        sum_f = sum([x[0] for x in fits])
        random_num = random.randint(1, sum_f)
        current_sum = 0
        parent = fits[0][1]
        for item in fits:
            current_sum += item[0]
            if random_num < current_sum:
                parent = item[1]
                break
        return parent

    @staticmethod
    def get_statistic(fits):
        best_fit = min(fits)[0]
        ave_fit = sum([x[0] for x in fits]) / len(fits)
        return best_fit, ave_fit


class GeneticAlgorithmSchedule(GeneticAlgorithm):
    def __init__(self, probability_crossover=0.8, population_size=30, limit=200, operators=None):
        self.operators = operators
        self.best_fits = []
        self.ave_fits = []
        super(GeneticAlgorithmSchedule, self).__init__(probability_crossover, population_size, limit)

    def create_initial(self):
        population = []
        i = 0
        while i < self.population_size:
            chromosome = self.operators.create_individ()
            population.append(chromosome)
            i += 1
        return population

    def parents(self, fits_populations):
        pop = self.fitness_scaling(fits_populations)
        while True:
            first_parent = self.roulette(pop)
            second_parent = self.roulette(pop)
            yield (first_parent, second_parent)

    def check_gen(self, chromosome, gen):
        return gen not in chromosome and self.operators.predecessors_included(chromosome, gen)

    def fitness(self, chromosome):
        return self.operators.fitness(chromosome)

    def crossover(self, parents):
        child = []
        i = 0
        while i < self.operators.task_count:
            current_parent = parents[i % 2]
            valid = False
            for j in range(i, i + self.operators.task_count):
                new_gen = current_parent[j % self.operators.task_count]
                if self.check_gen(child, new_gen):
                    child.append(new_gen)
                    valid = True
                    break
            if not valid:
                parents[0], parents[1] = parents[1], parents[0]
            else:
                i += 1
        return child

    def mutation(self, parent):
        need_swap = True
        chromosome = copy.copy(parent)
        while need_swap:
            index_gen = random.randint(1, self.operators.task_count - 1)
            gen = chromosome[index_gen]
            left_gen = chromosome[index_gen - 1]
            gen_predecessors = self.operators.predecessors[gen]

            if not gen_predecessors or left_gen not in gen_predecessors:
                chromosome[index_gen - 1], chromosome[index_gen] = gen, left_gen
                need_swap = False
        return chromosome

    def check_end(self, fits):
        self.counter += 1
        ave = sum([x[0] for x in fits]) / len(fits)
        # print "{0}: {1}, ave:{2}".format(self.counter, min(fits), ave)
        self.ave_fits.append(ave)
        self.best_fits.append(min(fits)[0])
        return self.counter >= self.limit
