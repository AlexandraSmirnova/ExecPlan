# coding=utf-8
import time
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.urlresolvers import reverse
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.generic import DetailView
from django.views.generic.base import View, TemplateView
from django.views.generic.edit import FormView

from scheduling.algorithms.branch_and_bound import BranchAndBoundAlgorithm
from scheduling.algorithms.genetic_algorithm import GeneticAlgorithmSchedule
from scheduling.algorithms.helpers import ScheduleOperators
from scheduling.algorithms.heuristics import PriorityHeuristic
from scheduling.forms import GeneticAlgorithmForm, AddProjectForm
from scheduling.models import Project, Task, ProjectMember
from utils.base_views import AjaxFormView


class ProjectView(LoginRequiredMixin, DetailView):
    template_name = 'scheduling/project.html'
    model = Project
    context_object_name = 'project'
    pk_url_kwarg = 'project_id'

    def get(self, request, *args, **kwargs):
        project_id = kwargs.get('project_id', None)
        is_member = ProjectMember.objects.check_membership(request.user, project_id)
        if not is_member:
            return HttpResponseBadRequest()
        return super(ProjectView, self).get(request, *args, **kwargs)


class AddProjectView(LoginRequiredMixin, TemplateView, AjaxFormView):
    http_method_names = ['get', 'post']
    form_class = AddProjectForm
    template_name = 'scheduling/add_project.html'

    def get_success_url(self):
        return reverse('core:profile')

    def get_form_kwargs(self):
        kwargs = super(AddProjectView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.save()
        return super(AddProjectView, self).form_valid(form)


class GaView(FormView):
    http_method_allowed = ['post']
    project_id = None
    form_class = GeneticAlgorithmForm

    def post(self, request, *args, **kwargs):
        self.project_id = int(request.POST.get('id', None))
        is_member = ProjectMember.objects.check_membership(request.user, self.project_id)
        if not self.project_id or not is_member:
            return HttpResponseBadRequest()
        return super(GaView, self).post(request, *args, **kwargs)

    def form_valid(self, form):
        tasks = Task.objects.get_project_tasks(self.project_id)
        new_tasks = []
        for task in tasks:
            new_tasks.append(task.as_dict())
        # ToDo: добавить ошибку, если задач < 5

        probability_crossover = form.cleaned_data.get('probability_crossover')
        population_size = form.cleaned_data.get('population_size')
        limit = form.cleaned_data.get('limit')
        operators = ScheduleOperators(task_objects=new_tasks)
        gs = GeneticAlgorithmSchedule(probability_crossover=probability_crossover, population_size=population_size,
                                      limit=limit, operators=operators)
        t_start = time.time()
        statistic = gs.run()
        t_end = time.time()
        print t_end - t_start
        return JsonResponse({'status': 'OK', 'statistic': statistic})

    def form_invalid(self, form):
        return JsonResponse({'status': 'ERROR', 'errors': {k: v for k, v in form.errors.items()}})


class BranchAndBoundView(View):
    http_method_allowed = ['post']
    project_id = None

    def post(self, request, *args, **kwargs):
        self.project_id = int(request.POST.get('id', None))
        is_member = ProjectMember.objects.check_membership(request.user, self.project_id)
        if not self.project_id or not is_member:
            return HttpResponseBadRequest()
        tasks = Task.objects.get_project_tasks(self.project_id)
        new_tasks = []
        for task in tasks:
            new_tasks.append(task.as_dict())

        operators = ScheduleOperators(task_objects=new_tasks)
        algorithm = BranchAndBoundAlgorithm(operators=operators)
        t_start = time.time()
        statistic = algorithm.run()
        t_end = time.time()
        print t_end - t_start
        return JsonResponse({'status': 'OK', 'statistic': statistic})


class PriorityHeuristicView(View):
    http_method_allowed = ['post']
    project_id = None

    def post(self, request, *args, **kwargs):
        self.project_id = int(request.POST.get('id', None))
        is_member = ProjectMember.objects.check_membership(request.user, self.project_id)
        if not self.project_id or not is_member:
            return HttpResponseBadRequest()
        tasks = Task.objects.get_project_tasks(self.project_id)
        new_tasks = []
        for task in tasks:
            new_tasks.append(task.as_dict())

        operators = ScheduleOperators(task_objects=new_tasks)
        algorithm = PriorityHeuristic(operators=operators)
        t_start = time.time()
        statistic = algorithm.run()
        t_end = time.time()
        print t_end - t_start
        return JsonResponse({'status': 'OK', 'statistic': statistic})

