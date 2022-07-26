from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Filmwork, Genre, GenreFilmwork, Person, PersonFilmwork


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    """Определение таблицы Genre в админке."""

    list_display = (
        'name',
        'description',
    )
    list_filter = ('name',)
    search_fields = ('name', 'description', 'id')


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    """Определение таблицы Person в админке."""

    list_display = ('full_name',)
    search_fields = ('full_name', 'id')


class GenreFilmworkInline(admin.TabularInline):
    """Определение вложенной таблицы Genre в админке."""

    model = GenreFilmwork
    autocomplete_fields = ('genre',)


class PersonFilmworkInline(admin.TabularInline):
    """Определение вложенной таблицы Person в админке."""

    model = PersonFilmwork
    autocomplete_fields = ('person',)


@admin.register(Filmwork)
class FilmworkAdmin(admin.ModelAdmin):
    """Определение таблицы Filmwork в админке."""

    inlines = (GenreFilmworkInline, PersonFilmworkInline)
    list_display = (
        'title',
        'rating',
        'get_genres',
        'get_actors',
        'get_writers',
        'get_directors',
        'creation_date',
    )
    list_filter = ('type', 'rating', 'genres')
    search_fields = ('title', 'description', 'id')
    list_prefetch_related = ('genres', 'persons')

    def get_queryset(self, request) -> object:
        """Метод получения объекта QuerySet для представления в list_display"""
        queryset = (
            super()
            .get_queryset(request)
            .prefetch_related(*self.list_prefetch_related)
        )
        return queryset

    def get_genres(self, obj) -> str:
        """Метод получения значений полей "name" модели Genre."""
        return ', '.join([genre.name for genre in obj.genres.all()])

    @admin.display
    def get_actors(self, obj) -> str:
        """Метод получения значений полей "full_name" модели Person, где "role" == "actor"."""
        return ', '.join([actor.full_name for actor in obj.persons.filter(personfilmwork__role='actor')])

    @admin.display
    def get_writers(self, obj) -> str:
        """Метод получения значений полей "full_name" модели Person, где "role" == "writer"."""
        return ', '.join([writer.full_name for writer in obj.persons.filter(personfilmwork__role='writer')])

    @admin.display
    def get_directors(self, obj) -> str:
        """Метод получения значений полей "full_name" модели Person, где "role" == "director"."""
        return ', '.join([director.full_name for director in obj.persons.filter(personfilmwork__role='director')])

    get_genres.short_description = _('genres')
    get_actors.short_description = _('actors')
    get_writers.short_description = _('writers')
    get_directors.short_description = _('directors')
