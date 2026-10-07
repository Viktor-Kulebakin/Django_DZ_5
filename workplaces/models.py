from django.db import models


class Workplace(models.Model):
    # Номер стола
    table_number = models.IntegerField(
        unique=True, 
        verbose_name="Номер стола"
    )
    
    # Дополнительная информация по желанию студента
    equipment_info = models.TextField(
        blank=True, 
        null=True, 
        verbose_name="Установленное оборудование",
        help_text="Например: Монитор 27', клавиатура, док-станция"
    )
    is_occupied = models.BooleanField(
        default=False, 
        verbose_name="Стол занят"
    )

    class Meta:
        verbose_name = "Рабочее место"
        verbose_name_plural = "Рабочие места"
        ordering = ['table_number']

    def __str__(self):
        status = "Занято" if self.is_occupied else "Свободно"
        return f"Стол №{self.table_number} ({status})"
