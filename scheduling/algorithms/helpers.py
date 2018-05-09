# coding=utf-8
from __future__ import unicode_literals
import copy
import random
import numpy as np
from datetime import timedelta, datetime
from scheduling.models import Task, Project
from utils.decorators import memoize


class ScheduleOperators(object):
    FINE_FOR_DELAY = 100

    def __init__(self, task_objects=None):
        self.task_objects = task_objects
        self.task_count = len(task_objects)
        self.predecessors = []

        id_indexer = dict((p['id'], i) for i, p in enumerate(task_objects))

        for task in task_objects:
            preds = [id_indexer.get(pred) for pred in task['predecessors']]
            self.predecessors.append(preds)

    @memoize
    def fitness(self, chromosome):
        decoded = self.decode_chromosome(chromosome)
        costs = []
        delayed_days = 0

        for x in decoded:
            costs.append(x['end_time'])
            if x['s_deadline_time'] and x['end_time'] > x['s_deadline_time']:
                delayed_days += int((x['end_time'] - x['s_deadline_time']) / 9) + 1

        return max(costs) + delayed_days * self.FINE_FOR_DELAY

    def get_schedule_duration(self, chromosome):
        return max(x['end_time'] for x in self.decode_chromosome(chromosome))

    @memoize
    def decode_chromosome(self, chromosome):
        max_time = 1.0
        decoded_ch = copy.deepcopy(self.task_objects)

        for gen_id in chromosome:
            task = decoded_ch[gen_id]
            duration = task['duration']

            if not gen_id == chromosome[0]:
                executor_check = True
                preds_ended = True

                while executor_check or not preds_ended:
                    executor_check, time1 = self.is_executors_busy(decoded_ch, task['executors_ids'],
                                                                  max_time, max_time + duration)
                    preds_ended, time2 = self.check_predecessors_end(decoded_ch, gen_id, max_time)
                    max_time = max(time1, time2)

            task['start_time'] = max_time
            task['end_time'] = max_time + duration

        return decoded_ch

    @staticmethod
    def is_executors_busy(decoded_chromosome, executors_ids, start_time, end_time):
        result = False
        time_till = start_time
        # tasks_list = filter(lambda x: x['executor_id'] == executor, decoded_chromosome)
        for executor_id in executors_ids:
            tasks_list = filter(lambda x: executor_id in x['executors_ids'], decoded_chromosome)
            for task in tasks_list:
                if not (start_time > task['end_time'] or end_time < task['start_time']):
                    return True, task['end_time'] + 1

        return result, time_till

    def check_predecessors_end(self, decoded_chromosome, gen_id, start_time):
        preds = self.predecessors[gen_id]
        result = True
        till_time = 1.0

        if not preds:
            return result, till_time

        for pred in preds:
            if decoded_chromosome[pred]['end_time'] >= start_time:
                result = False
                till_time = decoded_chromosome[pred]['end_time'] + 1.0
                break

        return result, till_time

    @memoize
    def check_deadline(self, chromosome):
        decoded = self.decode_chromosome(chromosome)

        for x in decoded:
            if x['h_deadline_time'] and x['end_time'] > x['h_deadline_time']:
                # print x['id']
                return False

        return True

    @memoize
    def check_chromosome(self, chromosome):
        for j in range(len(chromosome)):
            valid, pred = self.predecessors_included(chromosome[:j], chromosome[j])
            if not valid:
                return False, j, chromosome.index(pred)

        if not self.check_deadline(chromosome):
            return False, 0, None

        return True, 0, None

    @memoize
    def predecessors_included(self, chromosome, gen_id):
        predecessors = self.predecessors[gen_id]

        for pr in predecessors:
            if pr not in chromosome:
                return False, pr

        return True, None

    def create_individ(self):
        i = 0
        chromosome = list(np.random.permutation([x for x in range(0, self.task_count)]))
        while i < 300000:
            valid, index, pred_index = self.check_chromosome(chromosome)
            if valid:
                return chromosome
            changed_part = chromosome[index:]
            random.shuffle(changed_part)
            chromosome = chromosome[:index] + changed_part
            i += 1

        raise Exception('Не удалось создать расписание')


def prepare_data_for_gantt(schedule):
    from core.models import User

    data = list()

    for item in schedule:
        task = Task.objects.filter(id=item.get('id')).first()

        data.append({
            'id_num': task.id,
            'name': task.name,
            'executor_name': User.objects.filter(id=item.get('executors_ids')[0]).first().get_full_name(),
            'predecessors': ", ".join([str(x) for x in item.get('predecessors')])
        })

    get_gantt_dates(data, schedule)

    return data


def get_gantt_dates(tasks_list, schedule):
    project = Project.objects.filter(task_project__id=schedule[0].get('id')).first()
    current_date = project.start_date
    start_work = 9
    end_work = 18

    for i in range(0, len(schedule)):
        item = schedule[i]
        st_hours = item['start_time']
        ed_hours = item['end_time']
        s = current_date + timedelta(hours=int(st_hours / 9) * 24) + timedelta(hours=st_hours % 9)
        e = current_date + timedelta(hours=int(ed_hours / 9) * 24) + timedelta(hours=ed_hours % 9)

        s = check_date(s, start_work, end_work)
        e = check_date(e, start_work, end_work)
        tasks_list[i].update({
            'start_time': datetime.strftime(s, '%Y-%m-%d %H:%M'),
            'end_time': datetime.strftime(e, '%Y-%m-%d %H:%M'),
        })

    return tasks_list


def check_date(date, start_work, end_work):
    end_of_day = date.replace(hour=end_work, minute=0, second=0, microsecond=0)

    if end_of_day < date:
        delta = date - end_of_day
        date = date.replace(hour=start_work + delta.seconds / 3600) + timedelta(days=1)

    return date
