from abc import abstractmethod

from django.conf.urls import url
from django.contrib import admin
from django.shortcuts import redirect
from django.template.response import TemplateResponse

from pckisz_pl_cache.extractors import ScreeningExtractor
from pckisz_pl_cache.models import Movie, Screening


class ExtractableAdmin(admin.ModelAdmin):
    change_list_template = 'pckisz_pl_cache/change_list.html'

    @property
    @abstractmethod
    def extraction_class(self):
        pass

    def get_urls(self):
        return [
            url(r'^extract/$', self.extract),
        ] + super().get_urls()

    def extract(self, request):
        if not request.user.is_authenticated:
            return redirect('%s?next=%s' % ('/admin/login/', request.path[:-8]))

        context = dict(
            self.admin_site.each_context(request),
            added=self.extraction_class().extract(),
        )
        return TemplateResponse(request, "pckisz_pl_cache/extraction_summary.html", context)


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    fields = ('id', 'title', 'description', 'poster', 'production', 'genre', 'duration', 'yt_video_id')
    list_display = ('title', 'production', 'genre', 'duration')
    list_filter = ('genre', 'duration')
    readonly_fields = ['id']
    search_fields = ['id', 'title', 'description', 'production']


@admin.register(Screening)
class ScreeningAdmin(ExtractableAdmin):
    extraction_class = ScreeningExtractor
    fields = ('id', 'movie', 'start', 'meeting')
    list_display = ('movie', 'start', 'meeting')
    list_filter = ('start', 'meeting')
    raw_id_fields = ['movie']
    readonly_fields = ['id']
    search_fields = ['id', 'movie__title', 'movie__description', 'movie__production']
