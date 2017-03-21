# views.py - django app called ajx
from django.shortcuts import render, HttpResponse
# from django.shortcuts import get_object_or_404, redirect, render_to_response, HttpResponseRedirect
# from django.core.urlresolvers import reverse
# from django.contrib.auth import authenticate, login
# import json
import os
from django.templatetags.static import static


def my_get_view(request):
    if request.method == 'GET':
        print("**get**")
        data = request.GET['mydata']
        html_txt = "<html><b> you sent a get request </b> <br> returned data: %s</html>" % data
        return HttpResponse(html_txt)
    return render(request)


def my_post_view(request):
    if request.method == 'POST':
        print("**post**")
        data = request.POST['mydata']
        html_txt = "<html><b> you sent a post request </b> <br> returned data: %s</html>" % data
        return HttpResponse(html_txt)
    return render(request)


def my_ajax_view(request):
    if request.method == 'POST':
        if request.is_ajax():
            print("**ajax post**")
            data = request.POST['mydata']
            html_txt = "<html><b> you sent an ajax post request </b> <br> returned data: %s</html>" % data
            return HttpResponse(html_txt)
    return render(request)


def my_ajax_form_view(request):
    if request.method == 'POST':
        if request.is_ajax():
            import json

            print("**ajax form post**")
            for k, v in request.POST.items():
                print(k, v)
            print("field1 data: %s" % request.POST['field1'])
            print("field2 data: %s" % request.POST['field2'])

            my_data = [{'url': '/static/ajx/SPOUT.wav'}]
            return HttpResponse(json.dumps(my_data), content_type="application/json")

    return render(request)


def foo(request, template='ajx/foo.html'):
    return render(request, template)


def play_audio_file(request):
    fname = 'ajx/static/ajx/test.mp3'
    f = open(fname, "rb")
    response = HttpResponse()
    response.write(f.read())
    response['Content-Type'] = 'audio/wav'
    response['Content-Length'] = os.path.getsize(fname)
    return response

