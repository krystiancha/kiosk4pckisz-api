from abc import ABCMeta, abstractmethod
from datetime import datetime, timedelta

import pytz
import requests
from contextlib import suppress
from django.core.exceptions import ObjectDoesNotExist
from django.utils.timezone import now
from lxml import html

from pckisz_pl_cache.models import Screening, Movie


class Extractor(metaclass=ABCMeta):
    base_url = 'http://www.pckisz.pl'

    @property
    @abstractmethod
    def relative_url(self):
        pass

    def __init__(self):

        self.added = []
        self.failed = []

        self.tree = []
        self.populate_tree()

        try:
            self.box_g_page = self.tree.xpath('//div[@class=\'box-g-page\']')[0]
        except IndexError:
            pass  # TODO: handle

    def populate_tree(self):
        self.tree = html.fromstring(requests.get(self.url(self.relative_url)).content)

    def url(self, relative_url):
        return self.base_url + relative_url

    @abstractmethod
    def extract(self):
        pass


class ListExtractor(Extractor, metaclass=ABCMeta):
    def __init__(self):
        super().__init__()

        with suppress(IndexError):
            self.row = self.box_g_page.xpath('div[@class=\'row\']')[0]
            self.anchors = self.row.xpath('a')
            self.styles = self.row.xpath('div[@class=\'col-xs-6 col-sm-5 col-md-4 col-lg-3\']/a/@style')
            self.titles = self.row.xpath('a/div[@class=\'col-xs-6 col-sm-7 col-md-8 col-lg-9\']/h3/text()')
            self.descriptions = self.row.xpath('//div[@class=\'a-txt\']/text()')
            self.items = []
            for idx, anchor in enumerate(self.anchors):
                self.items += [
                    (
                        self.url(anchor.xpath('@href')[0]),
                        self.url(self.styles[idx][22:self.styles[idx].find('\')')]),
                        self.titles[idx],
                        self.descriptions[idx].strip().replace(' ...', '...'),
                        anchor.xpath(
                            'div[@class=\'col-xs-6 col-sm-7 col-md-8 col-lg-9\']/span[@class=\'date small\']/text()'
                        ),
                    )
                ]


class ScreeningExtractor(ListExtractor):
    relative_url = '/filmy'

    def __init__(self):
        super().__init__()

    def parse_item(self, item):
        movie_exists = False

        try:
            for start_str in reversed(item[4][0].split('\xa0 | \xa0')[:-1]):
                start_strs = start_str.split(' - ')
                date_str = start_strs[0]
                time_strs = start_strs[1].split(', ')
                for time_str in time_strs:
                    naive = datetime.strptime(date_str + ' ' + time_str, '%Y.%m.%d %H:%M')
                    start = pytz.timezone('Europe/Warsaw').localize(naive, is_dst=None)
                    if now() > start:
                        return
                    if not movie_exists:
                        tree = html.fromstring(requests.get(item[0]).content)
                        box_g_page = tree.xpath('//div[@class=\'box-g-page\']')[0]
                        description = '\n'.join(box_g_page.xpath('p/text()')).strip()
                        span = tree.xpath('/html/body/div[2]/div/div[3]/div[2]/div/div/span[2]/text()')
                        production = span[0][11:]
                        genre = find_between(span[1], '\r\n\tGatunek: ', ', Czas:')
                        duration = timedelta(minutes=int(find_between(span[1], 'Czas:', ' min.')))
                        try:
                            yt_video_id_dirty = tree.xpath('//iframe[last()]/@src')[0].split('/')[-1]
                            yt_video_id = yt_video_id_dirty[:yt_video_id_dirty.find('?')]
                        except IndexError:
                            yt_video_id = ''
                        try:
                            movie = Movie.objects.get(
                                title=item[2],
                                description=description,
                                poster=item[1],
                                production=production,
                                genre=genre,
                                duration=duration,
                                yt_video_id=yt_video_id
                            )
                            movie_exists = True
                        except ObjectDoesNotExist:
                            movie = Movie(
                                title=item[2],
                                description=description,
                                poster=item[1],
                                production=production,
                                genre=genre,
                                duration=duration,
                                yt_video_id=yt_video_id
                            )
                            movie.save()
                    if not Screening.objects.filter(
                        movie=movie,
                        start=start
                    ).exists():
                        self.added += [Screening(
                            movie=movie,
                            start=start
                        )]
                        self.added[-1].save()
        except IndexError:
            pass
            self.failed.append((item[2], item[0]))

    def extract(self):

        self.added = []
        self.failed = []

        for item in self.items:
            self.parse_item(item)

        return self.added, self.failed


def find_between(s, first, last):
    try:
        start = s.index(first) + len(first)
        end = s.index(last, start)
        return s[start:end]
    except ValueError:
        return ''
