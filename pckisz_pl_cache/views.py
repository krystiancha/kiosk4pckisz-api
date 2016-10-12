from django.utils.timezone import now
from rest_framework import generics

from pckisz_pl_cache.models import Screening, Movie
from pckisz_pl_cache.serializers import ScreeningSerializer, MovieSerializer


class ScreeningList(generics.ListAPIView):
    queryset = Screening.objects.filter(start__gte=now())
    serializer_class = ScreeningSerializer


class MovieList(generics.ListAPIView):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer