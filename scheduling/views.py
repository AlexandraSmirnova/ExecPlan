from django.http import JsonResponse, HttpResponseBadRequest
from django.views.generic import DetailView
from django.views.generic.base import TemplateView, View

from scheduling.algorithms.ga import GeneticSchedule, GeneticAlgorithm
from scheduling.models import Project, Task


class ProjectView(DetailView):
    template_name = 'project.html'
    model = Project
    context_object_name = 'project'
    pk_url_kwarg = 'project_id'

    # def get_context_data(self, **kwargs):
    #     context = super(ProjectView, self).get_context_data(**kwargs)
    #     context['project'] =
    #     return context


class GaView(View):
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

        gs = GeneticSchedule(population_size=20, task_objects=new_tasks, limit=200)
        statistic = GeneticAlgorithm(gs).run()
        return JsonResponse({'status': 'OK', 'statistic': statistic})

