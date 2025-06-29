from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator


class Source(models.Model):
    TYPE_CHOICES = (
        ('Book', 'Книга'),
        ('Game', 'Игра'),
        ('Movie', 'Фильм'),
    )

    class Meta:
        verbose_name = 'Источник'
        verbose_name_plural = 'Источники'

    name = models.CharField(max_length=100, unique=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='Book')

    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"

    def clean(self):
        if self.pk and self.quotes.count() > 3:
            raise ValidationError('Максимум 3 цитаты на источник')


class Quote(models.Model):
    text = models.TextField(max_length=1000, unique=True)
    source = models.ForeignKey(
        Source,
        on_delete=models.CASCADE,
        related_name='quotes',
        null=False,
        verbose_name='Источник'
    )
    weight = models.PositiveSmallIntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Вероятность показа (1-10)"
    )
    views = models.PositiveIntegerField(default=0, editable=False)
    likes = models.PositiveIntegerField(default=0, editable=False)
    dislikes = models.PositiveIntegerField(default=0, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-weight', '-created_at']
        verbose_name = 'Цитата'
        verbose_name_plural = 'Цитаты'

    def __str__(self):
        return f'"{self.text[:50]}..." - {self.source.name}'

    def clean(self):
        if Quote.objects.filter(text=self.text).exclude(pk=self.pk).exists():
            raise ValidationError({'text': 'Такая цитата уже существует'})

        if self.pk and self.source.quotes.count() >= 3:
            raise ValidationError(
                {'source': 'У источника уже есть 3 цитаты. Выберите другой источник.'}
            )