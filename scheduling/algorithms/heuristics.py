import copy

from scheduling.algorithms.helpers import prepare_data_for_gantt


class PriorityHeuristic(object):
    def __init__(self, operators):
        self.operators = operators
        self.statistic = {}

    def run(self):
        tasks = self.operators.task_objects
        sorted_tasks = copy.deepcopy(tasks)
        sorted_tasks.sort(key=lambda x: (
            x['h_deadline_time'] if x['h_deadline_time'] else 999999,
            x['s_deadline_time'] if x['s_deadline_time'] else 999999,
            x['duration']
        ))
        # print [x['duration'] for x in sorted_tasks]
        chromosome = []
        for item in sorted_tasks:
            index = [tasks.index(elem) for elem in tasks if elem['id'] == item['id']]
            if len(index) > 0:
                chromosome.append(index[0])

        i = 0
        while i < 300000:
            valid, index, pred_index = self.operators.check_chromosome(chromosome)
            if valid:
                break

            if pred_index:
                next_index = pred_index
            elif index == 0:
                next_index = 1
            else:
                next_index = (index + 1) % len(tasks)
            chromosome[index], chromosome[next_index] = chromosome[next_index], chromosome[index]
            i += 1

        fit = self.operators.fitness(chromosome)
        self.statistic['best_fit'] = fit
        print fit
        self.statistic['data_dict'] = prepare_data_for_gantt(self.operators.decode_chromosome(chromosome))
        schedule_time = max(x['end_time'] for x in self.operators.decode_chromosome(chromosome))
        self.statistic['delayed_days'] = (fit - schedule_time) / self.operators.FINE_FOR_DELAY
        return self.statistic
