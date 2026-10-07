import os
from ckeditor.fields import RichTextField
from django.contrib.auth.models import User
# ДОБАВИЛИ ИМПОРТЫ: ValidationError для валидатора и timezone для даты по умолчанию
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver


class Skill(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название навыка")

    class Meta:
        verbose_name = "Навык"
        verbose_name_plural = "Навыки"

    def __str__(self):
        return self.name


class EmployeeProfile(models.Model):
    GENDER_CHOICES = [
        ('M', 'Мужской'),
        ('F', 'Женский'),
    ]

    # СПИСКИ ДЛЯ ВАЛИДАЦИИ СТОЛОВ
    DEVELOPERS = ['backend', 'frontend']
    TESTER = 'qa'

    ROLE_CHOICES = [
        ('backend', 'Бэкенд-разработчик'),
        ('frontend', 'Фронтенд-разработчик'),
        ('qa', 'Тестировщик'),
        ('other', 'Другое'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name="Пользователь"
    )
    first_name = models.CharField(max_length=50, verbose_name="Имя")
    last_name = models.CharField(max_length=50, verbose_name="Фамилия")
    middle_name = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Отчество (при наличии)"
    )
    gender = models.CharField(
        max_length=1,
        choices=GENDER_CHOICES,
        verbose_name="Пол"
    )
    skills = models.ManyToManyField(
        'Skill',
        through='EmployeeSkill',
        verbose_name="Навыки"
    )
    description = RichTextField(
        blank=True,
        null=True,
        verbose_name="Описание"
    )

    # --- НОВЫЕ ПОЛЯ ---
    role = models.CharField(
        max_length=20, 
        choices=ROLE_CHOICES, 
        default='other',
        verbose_name="Должность"
    )
    desk_number = models.IntegerField(
        verbose_name="Номер стола",
        blank=True,
        null=True  # null=True на случай, если у кого-то временно нет стола
    )
    date_joined = models.DateField(
        default=timezone.now, 
        verbose_name="Дата приёма на работу"
    )
    # ------------------

    class Meta:
        verbose_name = "Профиль сотрудника"
        verbose_name_plural = "Профили сотрудников"

    def __str__(self):
        return f"{self.last_name} {self.first_name}"

    # --- ТРЕБУЕМАЯ ВАЛИДАЦИЯ СОСЕДНИХ СТОЛОВ ---
    def clean(self):
        super().clean()
        
        # Если стол или роль не указаны, пропускаем проверку соседства
        if self.desk_number is None or not self.role:
            return

        # Номера соседних столов (слева и справа)
        neighbor_desks = [self.desk_number - 1, self.desk_number + 1]
        
        # Ищем соседей в базе данных
        neighbors = EmployeeProfile.objects.filter(desk_number__in=neighbor_desks)
        
        # Если профиль редактируется, исключаем самого себя из проверки
        if self.pk:
            neighbors = neighbors.exclude(pk=self.pk)
            
        # Логика 1: Текущий — тестировщик. Проверяем, нет ли рядом разработчиков
        if self.role == self.TESTER:
            if neighbors.filter(role__in=self.DEVELOPERS).exists():
                raise ValidationError({
                    'desk_number': f"Ошибка! За соседним столом (№{self.desk_number-1} или №{self.desk_number+1}) сидит разработчик. Тестировщики и разработчики не могут сидеть рядом."
                })
                
        # Логика 2: Текущий — разработчик. Проверяем, нет ли рядом тестировщиков
        if self.role in self.DEVELOPERS:
            if neighbors.filter(role=self.TESTER).exists():
                raise ValidationError({
                    'desk_number': f"Ошибка! За соседним столом (№{self.desk_number-1} или №{self.desk_number+1}) сидит тестировщик. Разработчики и тестировщики не могут сидеть рядом."
                })

    # Принудительный запуск полной валидации перед сохранением в базу данных
    def save(self, *args, **kwargs):
        self.full_clean()  # Вызывает clean() при любом сохранении
        super().save(*args, **kwargs)


class EmployeeSkill(models.Model):
    employee = models.ForeignKey(EmployeeProfile, on_delete=models.CASCADE)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    level = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        verbose_name="Уровень освоения (1-10)"
    )

    class Meta:
        verbose_name = "Навык сотрудника"
        verbose_name_plural = "Навыки сотрудников"
        unique_together = ('employee', 'skill')

    def __str__(self):
        return f"{self.skill.name} ({self.level})"


class EmployeeImage(models.Model):
    employee = models.ForeignKey(
        EmployeeProfile, 
        on_delete=models.CASCADE, 
        related_name='images', 
        verbose_name="Сотрудник"
    )
    image = models.FileField(
        upload_to='employee_gallery/', 
        verbose_name="Изображение"
    )
    position = models.PositiveIntegerField(
        default=1, 
        verbose_name="Порядковый номер"
    )

    class Meta:
        verbose_name = "Изображение сотрудника"
        verbose_name_plural = "Галерея изображений"
        ordering = ['position', 'id']

    def __str__(self):
        return f"Фото {self.position} для {self.employee.last_name}"
