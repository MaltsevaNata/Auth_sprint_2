from django.contrib import admin

from .models import Filmwork, Genre, PersonRole, Person


class PersonRoleInline(admin.TabularInline):
    model = PersonRole
    extra = 0


@admin.register(Filmwork)
class FilmworkAdmin(admin.ModelAdmin):
    # отображение полей в списке
    list_display = ('title', 'filmwork_type', 'creation_date', 'rating', 'created', 'modified')

    # фильтрация в списке
    list_filter = ('filmwork_type',)

    # поиск по полям
    search_fields = ('title', 'description', 'id')

    # порядок следования полей в форме создания/редактирования
    fields = (
        'title', 'filmwork_type', 'description', 'creation_date', 'genres',
        'file_path', 'rating', 'age_limit',
    )

    inlines = [
            PersonRoleInline
        ]


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    pass


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    pass
