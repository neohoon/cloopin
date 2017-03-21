from django.shortcuts import render, get_object_or_404
from django.views import generic
from .models import Video, Subtitle
# import operator
# from django.db.models import Q
# from datetime import date

# from haystack.generic_views import SearchView
from haystack.query import SearchQuerySet


class EntryView(generic.TemplateView):
    template_name = 'ivsearch/entry.html'


class ResultView(generic.ListView):
    template_name = 'ivsearch/result.html'
    context_object_name = 'context'

    def get_queryset(self):
        query = self.request.GET.get('q')
        query_list, results, results3 = None, None, []
        if query:
            query_list = query_postprocessing(query.split())
            results = Video.objects.all()
            for k in range(len(query_list)):
                results = results.filter(sub_script__contains=query_list[k])
            # for k in range(len(results)):
            #     results[k].title = (results[k].title[:40] + '...') if len(results[k].title) > 45 else results[k].title
            for k in range(len(results)):
                results[k].thumbnail = results[k].thumbnail.replace('/default.', '/mqdefault.')
                results[k].num_matches = 34
            results_limit = min(20, int(len(results)/3))
            num_videos = results_limit * 3
            for k in range(0, results_limit):
                results3.append([results[3*k], results[3*k+1], results[3*k+2]])
            context = {'query': query_list, 'num_videos': num_videos, 'videos': results3}
            self.request.session['query_list'] = query_list
            return context


class ResultHsView(generic.ListView):
    template_name = 'ivsearch/result.html'
    context_object_name = 'context'

    def get_queryset(self):
        query = self.request.GET.get('q')
        query_list, results, results3 = None, None, []

        if (self.request.method == "GET") and query:
            query_list = query.split()
            results = SearchQuerySet().filter(sub_script__contains=query).load_all()

            for k in range(results.count()):
                results[k].thumbnail = results[k].thumbnail.replace('/default.', '/mqdefault.')
                results[k].num_matches = int(results[k].score * 100)

            results_limit = min(20, int(len(results)/3))
            num_videos = results_limit * 3
            for k in range(0, results_limit):
                results3.append([results[3*k], results[3*k+1], results[3*k+2]])

            context = {'query': query_list, 'num_videos': num_videos, 'videos': results3}
            self.request.session['query_list'] = query_list

            return context


class DetailView(generic.ListView):
    template_name = 'ivsearch/detail.html'
    context_object_name = 'context'

    def get_queryset(self):
        vid = int(self.request.get_full_path().split('/')[-2])
        # video = Video.objects.get(pk=vid)
        subtitle_list = []
        query_list = self.request.session['query_list']
        for subtitle in Subtitle.objects.filter(video=vid):
            subtitle_q = Subtitle.objects.filter(id=subtitle.id)
            for kq in range(len(query_list)):
                results = subtitle_q.filter(script__contains=query_list[kq])
                if results:
                    subtitle_list.append(subtitle)
                    break
        context = {'query': query_list, 'video': list(Video.objects.filter(id=vid))[0], 'subtitles': subtitle_list}
        return context


def query_postprocessing(query_list):
    return query_list


def entry(request):
    return render(request, 'ivsearch/entry.html')


def result(request):
    all_videos = Video.objects.all()
    context = {'all_videos': all_videos}
    return render(request, 'ivsearch/result.html', context)


def detail(request, vid):
    video = get_object_or_404(Video, pk=vid)
    # try:
    #     video = Video.objects.get(pk=vid)
    # except Video.DoesNotExist:
    #     raise Http404("Video does not exist...")
    context = {'video': video}
    return render(request, 'ivsearch/detail.html', context)