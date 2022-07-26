from typing import Any

from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Q, QuerySet
from django.http import JsonResponse
from django.views.generic.detail import BaseDetailView
from django.views.generic.list import BaseListView
from movies.models import Filmwork, RoleType

from .utilities import MovieContextType, MoviesContextType


class MoviesApiMixin:  # noqa: WPS306
    """Миксин для классов MoviesListApi и MoviesDetailApi."""

    model = Filmwork
    http_method_names = ['get']

    def get_queryset(self) -> QuerySet:
        """Метод возвращает подготовленный QuerySet.

        Returns:
            queryset: объект QuerySet
        """
        queryset = self.model.objects.all().prefetch_related('genres', 'persons').values(
            'id',
            'title',
            'description',
            'creation_date',
            'rating',
            'type',
        ).annotate(
            genres=ArrayAgg('genres__name', distinct=True),
            actors=ArrayAgg('persons__full_name', filter=Q(personfilmwork__role=RoleType.ACTOR), distinct=True),
            directors=ArrayAgg('persons__full_name', filter=Q(personfilmwork__role=RoleType.DIRECTOR), distinct=True),
            writers=ArrayAgg('persons__full_name', filter=Q(personfilmwork__role=RoleType.WRITER), distinct=True),
        )
        return queryset

    def render_to_response(self, context: MovieContextType | MoviesContextType, **response_kwargs: Any) -> JsonResponse:
        """Метод отвечает за форматирование данных, которые вернутся при GET-запросе.

        Args:
            context: словарь с информацией о фильмах

        Returns:
            JsonResponse: страница API в виде Json
        """
        return JsonResponse(context)


class MoviesListApi(MoviesApiMixin, BaseListView):
    """Класс для представления атрибутов полей модели Filmwork."""

    def get_context_data(self, *, object_list=None, **kwargs) -> MoviesContextType:
        """Метод возвращает словарь с данными для формирования страницы.

        Returns:
            context: словарь с информацией о фильмах
        """
        self.paginate_by = 50
        queryset = self.get_queryset()
        paginator, page, queryset, is_paginated = self.paginate_queryset(queryset, self.paginate_by)
        context = {
            'count': paginator.count,
            'total_pages': paginator.num_pages,
            'prev': page.previous_page_number() if page.has_previous() else None,
            'next': page.next_page_number() if page.has_next() else None,
            'results': list(page.object_list),
        }
        return context


class MoviesDetailApi(MoviesApiMixin, BaseDetailView):
    """Класс для представления атрибутов поля модели Filmwork."""

    def get_context_data(self, *, object_list=None, **kwargs) -> MovieContextType:
        """Метод возвращает словарь с данными для формирования страницы.

        Returns:
            context: словарь с информацией о фильме
        """
        return self.get_object()
