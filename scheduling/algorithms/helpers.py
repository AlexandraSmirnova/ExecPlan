# coding=utf-8
import copy
import numpy as np


class ScheduleOperators(object):
    def __init__(self, task_objects=None):
        self.task_objects = task_objects
        self.task_count = len(task_objects)
        self.predecessors = []
        #self.predecessors.append(None)

        id_indexer = dict((p['id'], i) for i, p in enumerate(task_objects))
        for task in task_objects:
            preds = []
            for pred in task['predecessors']:
                id = id_indexer.get(pred)
                preds.append(id)
            self.predecessors.append(preds)

    def fitness(self, chromosome):
        decoded = self.decode_chromosome(chromosome)
        return max(x['end_time'] for x in decoded)

    def decode_chromosome(self, chromosome):
        max_time = 1
        decoded_ch = copy.deepcopy(self.task_objects)

        for gen_id in chromosome:
            #gen_key = gen_id - 1
            duration = decoded_ch[gen_id]['duration']

            if not gen_id == chromosome[0]:
                executor_check = True
                preds_ended = True
                while executor_check or not preds_ended:
                    executor_check, time1 = self.is_executor_busy(decoded_ch, decoded_ch[gen_id]['executor_id'],
                                                                  max_time, max_time + duration)
                    preds_ended, time2 = self.check_predecessors_end(decoded_ch, gen_id, max_time)
                    max_time = max(time1, time2)
            decoded_ch[gen_id]['start_time'] = max_time
            decoded_ch[gen_id]['end_time'] = max_time + duration

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
        preds = self.predecessors[gen_id]
        result = True
        till_time = 1

        if not preds:
            return result, till_time

        for pred in preds:
            #pred_key = pred - 1
            if decoded_chromosome[pred]['end_time'] >= start_time:
                result = False
                till_time = decoded_chromosome[pred]['end_time'] + 1
                break
        return result, till_time

    def check_chromosome(self, chromosome):
        valid = True
        for j in range(len(chromosome)):
            if not self.predecessors_included(chromosome[:j], chromosome[j]):
                valid = False
                break
        return valid

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

    def create_individ(self):
        i = 0
        while i < 300000:
            chromosome = list(np.random.permutation([x for x in range(0, self.task_count)]))
            if self.check_chromosome(chromosome):
                return chromosome
            i += 1
        raise Exception(u'Не удалось создать расписание')