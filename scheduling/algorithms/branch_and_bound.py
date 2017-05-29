import copy


class BranchAndBoundAlgorithm(object):
    def __init__(self, operators):
        self.operators = operators
        self.individ = None
        self.best = None
        self.statistic = []
        self.decoder = Decoder()

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
            fitness = self.operators.fitness(new_path)
            fitness2 = self.fitness(new_path)
            print '{0} and {1}'.format(fitness, fitness2)
            multipy = 1 if self.operators.task_count - len(new_path) else 0
            low_boundary = fitness + (self.operators.task_count - len(new_path)) * multipy
            if low_boundary < self.best and self.operators.predecessors_included(new_path, solution):
                # print new_path
                if len(solutions) == 1:
                    self.individ = new_path
                    self.best = copy.copy(fitness)
                else:
                    self.branch(new_path)
            self.statistic.append(self.best)

    def fitness(self, path):
        print len(path)
        if len(path) == 1:
            self.decoder.set_max_time(1)
            self.decoder.set_decoded_ch(copy.deepcopy(self.operators.task_objects))
            print('change')
           # print self.decoder.decoded_ch
        decoded = self.decoder.decode_chromosome(path, path[-1], self.operators)
        return max(x['end_time'] for x in decoded)


class Decoder(object):
    max_time = 1
    decoded_ch = None

    def decode_chromosome(self, chromosome, gen_id, operators):

        # if 'duration' not in self.decoded_ch:
        #     return
        duration = self.decoded_ch[gen_id]['duration']
        if not gen_id == chromosome[0]:
            executor_check = True
            preds_ended = True
            while executor_check or not preds_ended:
                executor_check, time1 = operators.is_executor_busy(self.decoded_ch, self.decoded_ch[gen_id]['executor_id'],
                                                                   self.max_time, self.max_time + duration)
                preds_ended, time2 = operators.check_predecessors_end(self.decoded_ch, gen_id, self.max_time)
                self.max_time = max(time1, time2)
        self.decoded_ch[gen_id]['start_time'] = self.max_time
        self.decoded_ch[gen_id]['end_time'] = self.max_time + duration

        print self.decoded_ch
        return self.decoded_ch

    def set_max_time(self, new_max_time):
        self.max_time = new_max_time

    def set_decoded_ch(self, new_decoded_ch):
        self.decoded_ch = new_decoded_ch





