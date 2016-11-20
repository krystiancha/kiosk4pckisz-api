import uuid

from django.db import models
from django.utils.translation import ugettext as _


class Model(models.Model):
    id = models.UUIDField(_('identifier'), primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class Movie(Model):
    title = models.CharField(_('title'), max_length=255, blank=True)
    description = models.TextField(_('description'), blank=True)
    poster = models.URLField(_('poster'), blank=True)
    production = models.CharField(_('production'), max_length=255, blank=True)
    genre = models.CharField(_('genre'), max_length=255, blank=True)
    duration = models.DurationField(_('duration'), blank=True, null=True)
    yt_video_id = models.CharField(_('YouTube video id'), max_length=255, blank=True)

    def __str__(self):
        return self.title or self.id

    class Meta:
        verbose_name = _('movie')
        verbose_name_plural = _('movies')


class Screening(Model):
    movie = models.ForeignKey(Movie, verbose_name=_('movie'))
    start = models.DateTimeField(_('start'))
    end = models.DateTimeField(_('end'), blank=True, help_text=_(
        'This field is automatically determined based on start time and movie length.'
    ), null=True)
    meeting = models.BooleanField(_('meeting with the director'), default=False)
    premiere = False

    def __str__(self):
        return (str(self.start) + ' ' + str(self.movie)) or self.id

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.end = self.start + self.movie.duration
        super().save(force_insert, force_update, using, update_fields)

    class Meta:
        verbose_name = _('screening')
        verbose_name_plural = _('screenings')
        ordering = ('start', 'movie')
