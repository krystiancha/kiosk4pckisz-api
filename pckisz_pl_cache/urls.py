from django.conf.urls import url

from pckisz_pl_cache import views

urlpatterns = [
    url(r'^screenings/$', views.ScreeningList.as_view()), # depreciated
    url(r'^movies/$', views.MovieList.as_view()), # depreciated
    url(r'^$', views.AllList.as_view()),
]