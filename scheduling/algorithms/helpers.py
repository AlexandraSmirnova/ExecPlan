# coding=utf-8
import copy
import numpy as np
from datetime import timedelta, datetime

from core.models import User
from scheduling.models import Task, Project


class ScheduleOperators(object):
    FINE_FOR_DELAY = 1000

    def __init__(self, task_objects=None):
        self.task_objects = task_objects
        self.task_count = len(task_objects)
        self.predecessors = []

        id_indexer = dict((p['id'], i) for i, p in enumerate(task_objects))

        for task in task_objects:
            preds = []

            for pred in task['predecessors']:
                id = id_indexer.get(pred)
                preds.append(id)

            self.predecessors.append(preds)

    def fitness(self, chromosome):
        decoded = self.decode_chromosome(chromosome)
        costs = []
        delayed_count = 0

        for x in decoded:
            costs.append(x['end_time'])
            if x['limit_time'] and x['end_time'] < x['limit_time']:
               delayed_count += 1

        return max(costs) + delayed_count * self.FINE_FOR_DELAY

    def get_schedule_duration(self, chromosome):
        decoded = self.decode_chromosome(chromosome)
        return max(x['end_time'] for x in decoded)

    def decode_chromosome(self, chromosome):
        max_time = 1
        decoded_ch = copy.deepcopy(self.task_objects)

        for gen_id in chromosome:
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

    def predecessors_included(self, chromosome, gen_id):
        predecessors = self.predecessors[gen_id]
        result = True

        if not predecessors:
            return result

        for pr in predecessors:
            if pr not in chromosome:
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


def get_dict_for_gantt(schedule):
    data = list()

    for item in schedule:
        task = Task.objects.filter(id=item.get('id')).first()

        if not task:
            return data

        task_dict = {
            'id_num': task.id,
            'name': task.name,
            'executor_name': User.objects.filter(id=item.get('executor_id', 1)).first().get_full_name(),
            'predecessors': ", ".join([str(x) for x in item.get('predecessors')])
        }
        data.append(task_dict)

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
            'start_time': datetime.strftime(s, '%m/%d/%Y %H:%M'),
            'end_time': datetime.strftime(e, '%m/%d/%Y %H:%M'),
        })

    return tasks_list


def check_date(date, start_work, end_work):
    end_of_day = date.replace(hour=end_work, minute=0, second=0, microsecond=0)

    if end_of_day < date:
        delta = date - end_of_day
        date = date.replace(hour=start_work + delta.seconds / 3600) + timedelta(days=1)

    return date
