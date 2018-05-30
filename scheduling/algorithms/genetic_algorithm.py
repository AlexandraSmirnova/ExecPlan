# coding=utf-8
import random
import copy


class GeneticAlgorithm(object):
    def __init__(self, probability_crossover=0.8, population_size=20, limit=200, operators=None):
        self.probability_crossover = probability_crossover
        self.population_size = population_size
        self.counter = 0
        self.limit = limit
        self.operators = operators

    def run(self):
        from scheduling.algorithms.helpers import prepare_data_for_gantt

        population = self.create_initial()
        statistic = {}

        while True:
            fits = [(self.fitness(ch),  ch) for ch in population]
            statistic_item = self.get_statistic(fits)

            for key, value in statistic_item.items():
                if key not in statistic:
                    statistic[key] = []
                statistic[key].append(value)

            if self.check_end(fits):
                best_fit = statistic_item['best_fit'] if 'best_fit' in statistic else None
                best_schedules = [item[1] for item in fits if item[0] == best_fit]
                decoded_best_schedule = self.operators.decode_chromosome(best_schedules[0])
                statistic['data_dict'] = prepare_data_for_gantt(decoded_best_schedule)
                best_time = max([x['end_time'] for x in decoded_best_schedule])
                statistic['delayed_days'] = (best_fit - best_time) / self.operators.FINE_FOR_DELAY
                # print decoded_best_schedule
                # for i in range(len(decoded_best_schedule)):
                #     print '{}  {}  {}'.format(i+2, decoded_best_schedule[i]['start_time'],  decoded_best_schedule[i]['duration'])
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
            child = self.crossover2(parents) if cross else self.mutation(parents[0])
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

    def crossover2(self, parents):
        return parents

    def mutation(self, chromosome):
        return chromosome

    def check_end(self, fits):
        return True

    def fitness_scaling(self, fits):
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

    def get_statistic(self, fits):
        best_fit = min(fits)[0]
        ave_fit = sum([x[0] for x in fits]) / len(fits)
        return {'best_fit': best_fit, 'ave_fit': ave_fit}


class GeneticAlgorithmSchedule(GeneticAlgorithm):
    def __init__(self, probability_crossover=0.8, population_size=30, limit=200, operators=None):
        super(GeneticAlgorithmSchedule, self).__init__(probability_crossover, population_size,
                                                       limit, operators)

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

    def crossover2(self, parents):
        half = self.operators.task_count / 2
        child = parents[0][:half]
        i = half - 1
        current_parent = parents[1]
        search_index = current_parent.index(child[-1])

        while i < self.operators.task_count:
            i += 1
            for j in range(search_index, search_index + self.operators.task_count):
                new_gen = current_parent[j % self.operators.task_count]

                if self.check_gen(child, new_gen):
                    child.append(new_gen)
                    search_index = current_parent.index(new_gen)
                    break

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
        return self.counter >= self.limit

    def get_statistic(self, fits):
        # durations = [self.operators.get_schedule_duration(x[1]) for x in fits]
        # cache_calls = len(fits) - self.operators.fitness_count
        return {
            'best_fit': min(fits)[0],
            'ave_fit': sum([x[0] for x in fits]) / len(fits),
            # 'cache_calls': cache_calls
            # 'best_time': min(durations),
            # 'ave_time': sum(durations)/len(fits)
        }

