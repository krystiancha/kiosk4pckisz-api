from django.utils.timezone import now
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView

from pckisz_pl_cache.models import Screening, Movie
from pckisz_pl_cache.serializers import OldScreeningSerializer, ScreeningSerializer, MovieSerializer


class ScreeningList(generics.ListAPIView): # depreciated
    serializer_class = OldScreeningSerializer

    def get_queryset(self):
        return Screening.objects.filter(start__gt=now()).prefetch_related('movie')


class MovieList(generics.ListAPIView): # depreciated
    serializer_class = MovieSerializer

    def get_queryset(self):
        return Movie.objects.filter(screening__start__gt=now()).distinct()


class AllList(APIView):
    def get(self, request, format=None):
        screenings = Screening.objects.filter(end__gt=now()).prefetch_related('movie__screening_set')

        movies = []
        for screening in screenings:
            if screening.movie not in movies:
                movies += [screening.movie]
            if screening == screening.movie.screening_set.first():
                screening.premiere = True

        screenings_serializer = ScreeningSerializer(screenings, many=True)
        movie_serializer = MovieSerializer(movies, many=True)

        return Response(
            {
                'movies': movie_serializer.data,
                'screenings': screenings_serializer.data
            }
        )
