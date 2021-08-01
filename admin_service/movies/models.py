import uuid

from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from model_utils.models import TimeStampedModel


class Genre(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_('название'), max_length=255, unique=True)
    description = models.TextField(_('описание'), blank=True)

    class Meta:
        verbose_name = _('жанр')
        verbose_name_plural = _('жанры')

    def __str__(self):
        return self.name


class Person(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(_('имя'), max_length=255)
    last_name = models.CharField(_('фамилия'), max_length=255)

    class Meta:
        verbose_name = _('Участник')
        verbose_name_plural = _('Участники')
        unique_together = ('first_name', 'last_name')

    def __str__(self):
        return f"""{self.first_name} {self.last_name}"""


class FilmworkType(models.TextChoices):
    MOVIE = 'movie', _('фильм')
    TV_SHOW = 'tv_show', _('шоу')
    SERIES = 'series', _('сериал')


class Filmwork(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(_('название'), max_length=255)
    description = models.TextField(_('описание'), blank=True, null=True)
    creation_date = models.DateField(_('дата создания фильма'), blank=True, null=True)
    file_path = models.FileField(_('файл'), upload_to='film_works/', blank=True, null=True)
    rating = models.FloatField(_('рейтинг'), validators=[MinValueValidator(0)], blank=True, null=True)
    filmwork_type = models.CharField(_('тип'), max_length=20, choices=FilmworkType.choices, default=_('фильм'))
    genres = models.ManyToManyField(Genre)
    persons = models.ManyToManyField(Person, through='PersonRole')
    age_limit = models.IntegerField(_('Возрастной ценз'), null=True, blank=True)

    class Meta:
        verbose_name = _('кинопроизведение')
        verbose_name_plural = _('кинопроизведения')
        indexes = [
            models.Index(fields=['rating', ]),
            models.Index(fields=['creation_date', ]),
            models.Index(fields=['filmwork_type', ]),
        ]

    def __str__(self):
        return self.title


class Role(models.TextChoices):
    ACTOR = 'actor', _('актер')
    DIRECTOR = 'director', _('режиссер')
    SCRIPTWRITER = 'scriptwriter', _('сценарист')


class PersonRole(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    filmwork = models.ForeignKey(Filmwork, on_delete=models.CASCADE)
    role = models.CharField(_('роль'), max_length=255, choices=Role.choices, null=False, blank=False)

    class Meta:
        verbose_name = _('Роль')
        verbose_name_plural = _('Роли')
        unique_together = ('person', 'filmwork', 'role')

    def __str__(self):
        return str(self.role)
