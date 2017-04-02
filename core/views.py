from django.views.generic import TemplateView

from scheduling.models import Project


class IndexView(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data()
        context['projects'] = Project.objects.all()
        return context
