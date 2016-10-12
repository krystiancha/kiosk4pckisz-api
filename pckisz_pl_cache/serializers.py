from rest_framework import serializers

from pckisz_pl_cache.models import Screening, Movie


class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = ('id', 'title', 'description', 'poster', 'production', 'genre', 'duration', 'yt_video_id')


class ScreeningSerializer(serializers.ModelSerializer):
    movie = MovieSerializer()

    class Meta:
        model = Screening
        filter = ('id', 'movie', 'start')
