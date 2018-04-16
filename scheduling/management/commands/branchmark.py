import time
from django.core.management import BaseCommand

from scheduling.algorithms.branch_and_bound import BranchAndBoundAlgorithm
from scheduling.algorithms.genetic_algorithm import GeneticAlgorithmSchedule
from scheduling.algorithms.helpers import ScheduleOperators
from scheduling.algorithms.heuristics import PriorityHeuristic
from scheduling.models import Task


class Command(BaseCommand):
    PROBABILITY_CROSSOVER = 0.2
    POPULATION_SIZE = 20
    LIMIT = 200
    LAUNCH_COUNT = 5

    def add_arguments(self, parser):
        parser.add_argument('p_id', default=1, type=int)

    def handle(self, *args, **options):
        project_id = options['p_id']
        tasks = Task.objects.get_project_tasks(project_id)
        new_tasks = []
        for task in tasks:
            new_tasks.append(task.as_dict())

        times = []
        delayed_days = 0

        for i in range(self.LAUNCH_COUNT):
            operators = ScheduleOperators(task_objects=new_tasks)
            gs = GeneticAlgorithmSchedule(self.PROBABILITY_CROSSOVER, self.POPULATION_SIZE,self.LIMIT,
                                          operators)
            # gs = PriorityHeuristic(operators=operators)
            # gs = BranchAndBoundAlgorithm(operators=operators)
            t_start = time.time()
            statistic = gs.run()
            t_end = time.time()
            print t_end - t_start
            times.append(t_end - t_start)
            # print statistic
            # delayed_days += statistic['delayed_days']
            print 'best: {}'.format(statistic['best_fit'][-1])
            # print 'delayed days: {}'.format(statistic['delayed_days'])
            # print 'ave: {}'.format(statistic['ave_fit'][-1])
            # print 'cache: {}'.format(sum(statistic['cache_calls'])/len(statistic['cache_calls']))

        # print delayed_days/self.LAUNCH_COUNT
        print sum(times)/self.LAUNCH_COUNT
