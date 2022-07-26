import uuid

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class TimeStampedMixin(models.Model):
    """Миксин для автозаполнения created и modified."""

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UUIDMixin(models.Model):
    """Миксин для автозаполнения UUID ключей."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class Genre(UUIDMixin, TimeStampedMixin):
    """Модель для Genre."""

    name = models.CharField(_('name'), max_length=255)  # noqa: WPS432
    description = models.TextField(_('description'), null=True, blank=True)

    def __str__(self):  # noqa: D105
        return self.name

    class Meta:
        db_table = 'content"."genre'
        verbose_name = _('genre')
        verbose_name_plural = _('genres')
        indexes = [
            models.Index(
                fields=['name'],
                name='genre_name_idx',
            ),
        ]


class Person(UUIDMixin, TimeStampedMixin):
    """Модель для Person."""

    full_name = models.CharField(_('full name'), max_length=255)  # noqa: WPS432

    def __str__(self):  # noqa: D105
        return self.full_name

    class Meta:
        db_table = 'content"."person'
        verbose_name = _('person')
        verbose_name_plural = _('persons')
        indexes = [
            models.Index(
                fields=['full_name'],
                name='p_full_name_idx',
            ),
        ]


class Filmwork(UUIDMixin, TimeStampedMixin):
    """Модель для Filmwork."""

    class FilmType(models.TextChoices):  # noqa: WPS431
        """Варианты значений для поля typt."""

        MOVIE = 'movie', _('movie')
        TV_SHOW = 'tv_show', _('tv_show')

    title = models.CharField(_('title'), max_length=255, blank=True)  # noqa: WPS432
    description = models.TextField(_('description'), null=True, blank=True)
    creation_date = models.DateField(_('creation date'), null=True, blank=True)
    rating = models.FloatField(
        _('rating'),
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    type = models.CharField(_('type'), max_length=255, choices=FilmType.choices)  # noqa: WPS432
    genres = models.ManyToManyField(Genre, through='GenreFilmwork')
    persons = models.ManyToManyField(Person, through='PersonFilmwork')
    file_path = models.FileField(
        _('file'), blank=True, null=True, upload_to='movies/')

    def __str__(self):  # noqa: D105
        return self.title

    class Meta:
        db_table = 'content"."film_work'
        verbose_name = _('film_work')
        verbose_name_plural = _('film_works')
        indexes = [
            models.Index(fields=['title'], name='fw_title_idx'),
            models.Index(
                fields=['creation_date', 'title'],
                name='fw_creation_date_title_idx',
            ),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['rating', 'title', 'id'],
                name='fw_rating_title_id_idx',
            ),
        ]


class GenreFilmwork(UUIDMixin):
    """Модель m2m для Genre и Filmwork."""

    film_work = models.ForeignKey(Filmwork, on_delete=models.CASCADE)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'content"."genre_film_work'
        verbose_name = _('genre')
        verbose_name_plural = _('genres')
        indexes = [
            models.Index(
                fields=['genre_id', 'film_work_id'],
                name='g_fw_genre_id_film_work_id_idx',
            ),
        ]


class RoleType(models.TextChoices):  # noqa: WPS431
    """Варианты значений для поля role."""

    ACTOR = 'actor', _('actor')
    COMPOSER = 'composer', _('composer')
    DIRECTOR = 'director', _('director')
    EDITOR = 'editor', _('editor')
    OPERATOR = 'operator', _('operator')
    PAINTER = 'painter', _('painter')
    PRODUCER = 'producer', _('producer')
    WRITER = 'writer', _('writer')


class PersonFilmwork(UUIDMixin):
    """Модель m2m для Person и Filmwork."""

    film_work = models.ForeignKey(Filmwork, on_delete=models.CASCADE)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    role = models.TextField(
        _('role'), choices=RoleType.choices, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'content"."person_film_work'
        verbose_name = _('person')
        verbose_name_plural = _('persons')
        constraints = [
            models.UniqueConstraint(
                fields=['film_work_id', 'person_id', 'role'],
                name='p_fw_person_id_idx',
            ),
        ]
