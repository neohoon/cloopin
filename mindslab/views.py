from django.shortcuts import render
# from django.shortcuts import HttpResponse
from django.views.generic import TemplateView
from django.http import HttpResponse

import json


def index(request):
    return render(request, 'mindslab/index.html')


class PostExample(TemplateView):
    template_name = 'mindslab/start.html'

    @staticmethod
    def post(request):
        return HttpResponse(json.dumps({'key': 'value'}), mimetype="application/json")