from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Q, F, Value
from django.db.models import Prefetch
from django.db.models.functions import Concat
from django.http import JsonResponse
from django.views.generic.detail import BaseDetailView
from django.views.generic.list import BaseListView
from django.core.paginator import Paginator

from movies.models import Filmwork, Genre, PersonRole


class MoviesApiMixin:
    model = Filmwork
    http_method_names = ['get']

    def get_queryset(self):
        """Обработка данных из БД """
        prefetch_genres = Prefetch(
            'genres',
            queryset=Genre.objects.all(),
            to_attr='name'
        )
        prefetch_persons = Prefetch(
            'persons',
            queryset=PersonRole.objects.select_related('person')
        )
        queryset = Filmwork.objects.prefetch_related(prefetch_genres, prefetch_persons).all()
        queryset = queryset.annotate(genre=ArrayAgg('genres__name', distinct=True))
        queryset = queryset.annotate(actors=ArrayAgg(Concat(F('persons__last_name'),
                                                            Value(' '), F('persons__first_name')),
                                                     filter=(Q(personrole__role='actor') | Q(personrole__role='актер') &
                                                             Q(persons__id=F('personrole__person'))), distinct=True))
        queryset = queryset.annotate(directors=ArrayAgg(Concat(F('persons__last_name'),
                                                               Value(' '), F('persons__first_name')),
                                                        filter=(Q(personrole__role='director') |
                                                                Q(personrole__role='режиссер') &
                                                                Q(persons__id=F('personrole__person'))), distinct=True))
        queryset = queryset.annotate(writers=ArrayAgg(Concat(F('persons__last_name'),
                                                             Value(' '), F('persons__first_name')),
                                                      filter=(Q(personrole__role='scriptwriter') |
                                                              Q(personrole__role='сценарист') &
                                                              Q(persons__id=F('personrole__person'))), distinct=True))
        queryset = queryset.annotate(type=F('filmwork_type'))
        queryset = queryset.values("id", "title", "description", "creation_date", "rating", "type", "actors",
                                   "directors", "writers").annotate(genres=F('genre'))
        return queryset

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context)


class Movies(MoviesApiMixin, BaseListView):
    paginate_by = 50

    def custom_paginate_queryset(self, queryset):
        """Дополнение встроенного пагинатора"""
        paginator, page, qs, has_other_pages = self.paginate_queryset(queryset, self.paginate_by)
        prev = paginator.previous_page_number if paginator.has_previous() else None
        next = paginator.next_page_number if paginator.has_other_pages() else None
        return {"count": len(queryset), "total_pages": paginator.num_pages, "prev": prev, "next": next,
                "results": qs}

    def get_context_data(self, *, object_list=None, **kwargs):
        """Возвращает постраничную информацию о фильмах"""
        queryset = self.get_queryset()
        context = self.custom_paginate_queryset(queryset)
        return context


class MoviesDetailApi(MoviesApiMixin, BaseDetailView):
    """Возвращает информацию об 1 фильме"""
    def get_context_data(self, **kwargs):
        context = list(self.get_queryset())[0]
        return context
