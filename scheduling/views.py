from django.http import JsonResponse, HttpResponseBadRequest
from django.views.generic import DetailView
from django.views.generic.base import View
from django.views.generic.edit import FormView

from scheduling.algorithms.branch_and_bound import BranchAndBoundAlgorithm
from scheduling.algorithms.genetic_algorithm import GeneticAlgorithmSchedule
from scheduling.algorithms.helpers import ScheduleOperators
from scheduling.forms import GeneticAlgorithmForm
from scheduling.models import Project, Task


class ProjectView(DetailView):
    template_name = 'project.html'
    model = Project
    context_object_name = 'project'
    pk_url_kwarg = 'project_id'


class GaView(FormView):
    http_method_allowed = ['post']
    project_id = None
    form_class = GeneticAlgorithmForm

    def post(self, request, *args, **kwargs):
        self.project_id = int(request.POST.get('id', None))
        if not self.project_id:
            return HttpResponseBadRequest()
        return super(GaView, self).post(request, *args, **kwargs)

    def form_valid(self, form):
        tasks = Task.objects.get_project_tasks(self.project_id)
        new_tasks = []
        for task in tasks:
            new_tasks.append(task.as_dict())

        probability_crossover = form.cleaned_data.get('probability_crossover')
        population_size = form.cleaned_data.get('population_size')
        limit = form.cleaned_data.get('limit')
        operators = ScheduleOperators(task_objects=new_tasks)
        gs = GeneticAlgorithmSchedule(probability_crossover=probability_crossover, population_size=population_size,
                                      limit=limit, operators=operators)
        statistic = gs.run()
        return JsonResponse({'status': 'OK', 'statistic': statistic})

    def form_invalid(self, form):
        return JsonResponse({'status': 'ERROR', 'errors': {k: v for k, v in form.errors.items()}})


class BranchAndBoundView(View):
    http_method_allowed = ['post']
    project_id = None

    def post(self, request, *args, **kwargs):
        self.project_id = request.POST.get('id', None)
        if not self.project_id:
            return HttpResponseBadRequest()
        tasks = Task.objects.get_project_tasks(self.project_id)
        new_tasks = []
        for task in tasks:
            new_tasks.append(task.as_dict())

        operators = ScheduleOperators(task_objects=new_tasks)
        algorithm = BranchAndBoundAlgorithm( operators=operators)
        statistic = algorithm.run()
        return JsonResponse({'status': 'OK', 'statistic': statistic})
