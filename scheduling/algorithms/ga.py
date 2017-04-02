# coding=utf-8
import random
import numpy as np
import copy


class GeneticAlgorithm(object):
    def __init__(self, operators):
        self.operators = operators

    def run(self):
        population = self.operators.create_initial()
        statistic = {'best_fit': [], 'ave_fit': []}
        while True:
            fits = [(self.operators.fitness(ch),  ch) for ch in population]
            best, ave = self.operators.get_statistic(fits)
            statistic['best_fit'].append(best)
            statistic['ave_fit'].append(ave)
            if self.operators.check_end(fits):
                break
            population = self.next(fits)
            # print "**{0}".format(population)
        return statistic

    def next(self, fits):
        parents_generator = self.operators.parents(fits)
        nexts = list()
        nexts.append(min(fits)[1])
        while len(nexts) < len(fits):
            parents = parents_generator.next()
            rand = random.random()
            cross = rand < self.operators.probability_crossover
            child = self.operators.crossover(parents) if cross else self.operators.mutation(parents[0])
            nexts.append(child)
        return nexts


class GeneticFunctions(object):
    def __init__(self, probability_crossover=0.8, limit=200):
        self.probability_crossover = probability_crossover
        self.counter = 0
        self.limit = limit

    def create_initial(self):
        return []

    def parents(self, fits_populations):
        pop = self.fitness_scaling(fits_populations)
        while True:
            ch1, ch2 = None, None
            for i in range(0, len(pop)-1, 2):
                f1, ch1 = pop[i]
                f2, ch2 = pop[i+1]
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
            result.append((dividend / (i+1), sorted_s[i][1]))
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


class GeneticSchedule(GeneticFunctions):
    def __init__(self, probability_crossover=0.8, population_size=30, task_objects=None, limit=200):
        self.population_size = population_size
        self.task_count = len(task_objects)
        self.task_objects = task_objects
        self.best_individ = None

        self.predecessors = []
        self.predecessors.append(None)
        for task in task_objects:
            self.predecessors.append(task['predecessors'])
        self.best_fits = []
        self.ave_fits = []

        super(GeneticSchedule, self).__init__(probability_crossover, limit)

    def create_initial(self):
        population = []
        i = 0

        while i < self.population_size:
            chromosome = list(np.random.permutation([x for x in range(1, self.task_count + 1)]))
            if self.check_chromosome(chromosome):
                population.append(chromosome)
                i += 1
        return population

    def parents(self, fits_populations):
        pop = self.fitness_scaling(fits_populations)
        while True:
            first_parent = self.roulette(pop)
            second_parent = self.roulette(pop)
            yield (first_parent, second_parent)

    def check_chromosome(self, chromosome):
        valid = True
        for j in range(len(chromosome)):
            if not self.predecessors_included(chromosome[:j], chromosome[j]):
                valid = False
                break
        return valid

    def check_gen(self, chromosome, gen):
        return gen not in chromosome and self.predecessors_included(chromosome, gen)

    def fitness(self, chromosome):
        decoded = self.decode_chromosome(chromosome)
        return max(x['end_time'] for x in decoded)

    # TODO: поменять crossover
    def crossover(self, parents):
        child = []
        i = 0
        while i < self.task_count:
            current_parent = parents[i % 2]
            valid = False
            for j in range(i, i + self.task_count):
                new_gen = current_parent[j % self.task_count]
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
            index_gen = random.randint(1, self.task_count - 1)
            gen = chromosome[index_gen]
            left_gen = chromosome[index_gen - 1]
            gen_predecessors = self.predecessors[gen]

            if not gen_predecessors or left_gen not in gen_predecessors:
                chromosome[index_gen - 1], chromosome[index_gen] = gen, left_gen
                need_swap = False
        return chromosome

    def predecessors_included(self, chromosome, gen):
        gen_predecessors = self.predecessors[gen]
        result = True
        if not gen_predecessors:
            return result

        for pred in gen_predecessors:
            if pred not in chromosome:
                result = False
                break
        return result

    def decode_chromosome(self, chromosome):
        max_time = 1
        decoded_ch = copy.deepcopy(self.task_objects)

        for gen_id in chromosome:
            gen_key = gen_id - 1
            duration = decoded_ch[gen_key]['duration']

            if not gen_id == chromosome[0]:
                executor_check = True
                preds_ended = True
                while executor_check or not preds_ended:
                    executor_check, time1 = self.is_executor_busy(decoded_ch, decoded_ch[gen_key]['executor_id'],
                                                                  max_time, max_time + duration)
                    preds_ended, time2 = self.check_predecessors_end(decoded_ch, gen_id, max_time)
                    max_time = max(time1, time2)
            decoded_ch[gen_key]['start_time'] = max_time
            decoded_ch[gen_key]['end_time'] = max_time + duration

        return decoded_ch

    @staticmethod
    def is_executor_busy(decoded_chromosome, executor, start_time, end_time):
        result = False
        time_till = start_time
        tasks_list = filter(lambda x: x['executor_id'] == executor, decoded_chromosome)

        for task in tasks_list:
            if not (start_time > task['end_time'] or end_time < task['start_time']):
                result = True
                time_till = task['end_time'] + 1
                break
        return result, time_till

    def check_predecessors_end(self, decoded_chromosome, gen_id, start_time):
        preds = self.predecessors[gen_id - 1]
        result = True
        till_time = 1

        if not preds:
            return result, till_time

        for pred in preds:
            pred_key = pred - 1
            if decoded_chromosome[pred_key]['end_time'] >= start_time:
                result = False
                till_time = decoded_chromosome[pred_key]['end_time'] + 1
                break
        return result, till_time

    def check_end(self, fits):
        self.counter += 1
        ave = sum([x[0] for x in fits]) / len(fits)
        # print "{0}: {1}, ave:{2}".format(self.counter, min(fits), ave)
        self.ave_fits.append(ave)
        self.best_fits.append(min(fits)[0])
        return self.counter >= self.limit


