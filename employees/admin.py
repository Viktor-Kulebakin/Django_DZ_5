from django.contrib import admin
from django.contrib.auth.models import Group, User
from .models import EmployeeProfile, EmployeeImage, Skill, EmployeeSkill


class EmployeeImageInline(admin.TabularInline):
    model = EmployeeImage
    extra = 1
    fields = ['image', 'position']
    ordering = ['position']


class EmployeeSkillInline(admin.TabularInline):
    model = EmployeeSkill
    extra = 1


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(EmployeeProfile)
class EmployeeProfileAdmin(admin.ModelAdmin):
    # Добавили новые поля в список отображения таблицы сотрудников
    list_display = ('last_name', 'first_name', 'gender', 'role', 'desk_number', 'date_joined')
    
    # Добавили удобные фильтры на боковую панель админки
    list_filter = ('role', 'gender', 'date_joined')
    
    # Добавили поиск по фамилии, имени и номеру стола
    search_fields = ('last_name', 'first_name', 'desk_number')
    
    inlines = [EmployeeSkillInline, EmployeeImageInline]

    # Группируем поля на форме редактирования для удобства администрирования
    fieldsets = [
        ('Основная информация', {
            'fields': ('user', 'last_name', 'first_name', 'middle_name', 'gender', 'description')
        }),
        ('Рабочее место и учёт', {
            'fields': ('role', 'desk_number', 'date_joined'),
            'description': 'Параметры размещения сотрудника в офисе. Автоматический валидатор запрещает сажать тестировщиков и разработчиков за соседние столы.'
        }),
    ]


# Переименование встроенных моделей в админке для красоты
Group._meta.verbose_name = 'Группа'
Group._meta.verbose_name_plural = 'Группы'
User._meta.verbose_name = 'Пользователь'
User._meta.verbose_name_plural = 'Пользователи'
