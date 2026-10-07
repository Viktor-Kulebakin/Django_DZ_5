from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.core.paginator import Paginator
from django.db.models import Prefetch
from django.utils import timezone
from .models import EmployeeProfile, EmployeeImage

def index_view(request):
    """Главная страница: описание проекта и карточки сотрудников."""
    # Оптимально подтягиваем профили и связанные картинки
    employees_queryset = EmployeeProfile.objects.prefetch_related(
        Prefetch('images', queryset=EmployeeImage.objects.order_by('position', 'id'))
    )
    
    # 1. Общее количество сотрудников в базе данных
    total_employees = employees_queryset.count()
    
    # 2. Только 4 последних по дате приёма на работу
    latest_employees = employees_queryset.order_by('-date_joined')[:4]
    
    # 3. Вычисляем стаж в днях для каждого из 4-х сотрудников
    today = timezone.now().date()
    for emp in latest_employees:
        emp.experience_days = (today - emp.date_joined).days

    context = {
        'title': 'Главная страница', 
        'employees': latest_employees,  # Передаем только 4 последних
        'total_employees': total_employees  # Передаем общее количество
    }
    return render(request, 'employees/index.html', context)


def employee_list_view(request):
    """Список всех сотрудников с пагинацией."""
    # Подгружаем сотрудников с картинками, сортируем (например, по фамилии)
    employees_queryset = EmployeeProfile.objects.prefetch_related(
        Prefetch('images', queryset=EmployeeImage.objects.order_by('position', 'id'))
    ).order_by('last_name', 'first_name')
    
    # Вычисляем стаж в днях для всех сотрудников в списке
    today = timezone.now().date()
    for emp in employees_queryset:
        emp.experience_days = (today - emp.date_joined).days

    # 1. Настройка пагинации по 10 сотрудников на страницу
    paginator = Paginator(employees_queryset, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'title': 'Список сотрудников', 
        'page_obj': page_obj  # Шаблон теперь будет итерировать page_obj вместо employees
    }
    return render(request, 'employees/list.html', context)


@login_required
def employee_detail_view(request, pk):
    """Подробная карточка сотрудника (только для авторизованных)."""
    # Загружаем сотрудника со связанными данными
    employee = get_object_or_404(
        EmployeeProfile.objects.prefetch_related(
            Prefetch('images', queryset=EmployeeImage.objects.order_by('position', 'id'))
        ), 
        pk=pk
    )
    
    skills = employee.employeeskill_set.all()
    all_images = list(employee.images.all())
    
    # Вычисляем стаж в днях
    today = timezone.now().date()
    employee.experience_days = (today - employee.date_joined).days
    
    # Разделяем изображения по требованию задания
    main_image = all_images[0] if all_images else None  # Заглавное фото (первое)
    gallery_images = all_images[1:] if len(all_images) > 1 else []  # Остальные фото (без первого)

    context = {
        'employee': employee, 
        'skills': skills, 
        'main_image': main_image,        # Передаем первое фото отдельно
        'gallery_images': gallery_images  # Передаем галерею без первого фото
    }
    return render(request, 'employees/detail.html', context)


def logout_view(request):
    """Кастомное представление для безопасного выхода пользователя."""
    logout(request)
    return redirect('employees:index')
