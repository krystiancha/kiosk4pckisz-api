from datetime import datetime, timedelta
from time import strptime, mktime
from typing import List, Tuple

import requests
from bs4 import BeautifulSoup
from django.utils.timezone import now, make_aware
from django.core.exceptions import ObjectDoesNotExist

from pckisz_pl_cache.models import Movie, Screening


class ExtractionException(Exception):
    def __init__(self, msg, movie_title=None, movie_link=None, movie_showtimes_raw=None) -> None:
        super().__init__()
        self.msg = msg
        self.movie_title = movie_title
        self.movie_link = movie_link
        self.movie_showtimes_raw = movie_showtimes_raw

    def __str__(self) -> str:
        return '{} ({}): {}'.format(self.movie_title or '', self.movie_link or '', self.msg)


class NoFutureShows(Exception):
    pass


class ScreeningExtractor:
    BASE_URL = 'http://pckisz.pl'
    PATH = '/filmy,80'

    @classmethod
    def __call__(cls, *args, **kwargs):
        cls.extract()

    @classmethod
    def extract(cls):  # throws: requests.RequestException
        r = requests.get('{}{}'.format(cls.BASE_URL, cls.PATH))
        soup = BeautifulSoup(r.text)
        movies, failed_movies = cls._parse_movies_from_list(soup)

        return movies, failed_movies

    @classmethod
    def _parse_movies_from_list(cls, soup):
        box_g_page = soup.find(class_='box-g-page')
        if not box_g_page:
            raise ExtractionException('box-g-page not found')
        movie_list = box_g_page.find(class_='row')
        if not movie_list:
            raise ExtractionException('box-g-page row not found')
        a_tags = movie_list.find_all('a', recursive=False)

        movies: List[Movie] = []
        failed_movies: List[Tuple[str, str]] = []
        for a_tag in a_tags:
            try:
                movie_raw = cls._parse_movie_from_list(a_tag)
                if movie_raw:
                    movie = cls._extract_movie_details(*movie_raw)
                    movies.append(movie)
            except NoFutureShows:
                break
            except ExtractionException:
                link = a_tag.get('href')

                title = ''
                details_div = a_tag.find('div')
                if details_div:
                    title_h3 = a_tag.find('h3')
                    if title_h3:
                        title = title_h3.text

                failed_movies.append((title, link))

        return movies, failed_movies

    @classmethod
    def _parse_movie_from_list(cls, a_tag, ignore_past=False):
        details_div = a_tag.find('div')
        if not details_div:
            raise ExtractionException('div not found', )
        title_h3 = details_div.find('h3')
        if not title_h3:
            raise ExtractionException('h3 not found')
        title = title_h3.text
        shows_span = details_div.find('span', class_='date')
        if not shows_span:
            raise ExtractionException('showtimes not found')
        showdays_raw = shows_span.text.split('  |  ')
        if showdays_raw == ['']:
            raise ExtractionException('could not parse showtimes')
        if showdays_raw[-1] == '':
            showdays_raw.pop(-1)
        showtimes = []
        for showday_raw in showdays_raw:
            date_raw, showtimes_raw = showday_raw.split(' - ')
            for showtime_raw in showtimes_raw.split(', '):
                showtime = datetime.fromtimestamp(
                    mktime(strptime('{} {}'.format(date_raw, showtime_raw), '%Y.%m.%d %H:%M')))
                showtime = make_aware(showtime)
                if showtime > now() or ignore_past:
                    showtimes.append(showtime)
        if showtimes:
            link = a_tag.get('href')
            return title, link, showtimes
        else:
            raise NoFutureShows

    @classmethod
    def _extract_movie_details(cls, title, link, showtimes):
        r = requests.get('{}{}'.format(cls.BASE_URL, link))
        soup = BeautifulSoup(r.text)

        box_g_page = soup.find(class_='box-g-page')
        if not box_g_page:
            raise ExtractionException('box-g-page not found', title, link)
        poster_img = box_g_page.find('img')
        details_span = box_g_page.find('span',
                                       style='display:block; position:relative; padding-left:18px; line-height:145%;',
                                       recursive=False)

        try:
            movie = Movie.objects.get(
                title=title,
                description=''.join(map(lambda p_tag: p_tag.text, box_g_page.find_all('p', recursive=False))),
                poster='{}{}'.format(cls.BASE_URL, poster_img.get('src')) if poster_img else '',
                production=find_between(details_span.text, 'Produkcja:', '\r\n\t').strip(),
                genre=find_between(details_span.text, 'Gatunek:', ', Czas').strip(),
                duration=timedelta(minutes=float(find_between(details_span.text, 'Czas:', 'min').strip())),
            )
        except ObjectDoesNotExist:
            movie = Movie(
                title=title,
                description=''.join(map(lambda p_tag: p_tag.text, box_g_page.find_all('p', recursive=False))),
                poster='{}{}'.format(cls.BASE_URL, poster_img.get('src')) if poster_img else '',
                production=find_between(details_span.text, 'Produkcja:', '\r\n\t').strip(),
                genre=find_between(details_span.text, 'Gatunek:', ', Czas').strip(),
                duration=timedelta(minutes=float(find_between(details_span.text, 'Czas:', 'min').strip())),
            )

            movie.save()

        for showtime in showtimes:
            show = Screening(movie=movie, start=showtime)
            show.save()


def find_between(s, first, last):
    try:
        start = s.index(first) + len(first)
        end = s.index(last, start)
        return s[start:end]
    except ValueError:
        return ''
