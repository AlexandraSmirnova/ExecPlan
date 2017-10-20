from django.http import JsonResponse
from django.views.generic.edit import FormView


class AjaxFormView(FormView):
    ok_status = 'OK'
    error_status = 'ERROR'

    def get_success_url(self):
        return self.success_url

    def form_valid(self, form):
        return JsonResponse({
            'status': self.ok_status,
            'success_url': self.get_success_url()
        })

    def form_invalid(self, form):
        return JsonResponse({
            "status": self.error_status,
            "errors": form.errors
        })