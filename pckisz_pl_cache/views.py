from django.utils.timezone import now
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView

from pckisz_pl_cache.models import Screening, Movie
from pckisz_pl_cache.serializers import OldScreeningSerializer, ScreeningSerializer, MovieSerializer


class ScreeningList(generics.ListAPIView):
    queryset = Screening.objects.filter(start__gt=now()).prefetch_related('movie')
    serializer_class = OldScreeningSerializer


class MovieList(generics.ListAPIView):
    queryset = Movie.objects.filter(screening__start__gt=now()).distinct()
    serializer_class = MovieSerializer


class AllList(APIView):
    def get(self, request, format=None):
        screenings = Screening.objects.filter(end__gt=now()).prefetch_related('movie__screening_set')

        movies = set()
        screenings_today = []
        screenings_later = []
        for screening in screenings:
            movies.add(screening.movie)
            if screening == screening.movie.screening_set.first():
                screening.premiere = True
            if screening.start.date() == now().date():
                screenings_today += [screening]
            else:
                screenings_later += [screening]

        screenings_today_serializer = ScreeningSerializer(screenings_today, many=True)
        screenings_later_serializer = ScreeningSerializer(screenings_later, many=True)
        movie_serializer = MovieSerializer(movies, many=True)

        return Response(
            {
                'movies': movie_serializer.data,
                'screenings': {
                    'today': screenings_today_serializer.data,
                    'later': screenings_later_serializer.data,
                },
            }
        )
