from django.contrib import admin
from django import forms
from .models import Source, Quote


class QuoteForm(forms.ModelForm):
    class Meta:
        model = Quote
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        source = cleaned_data.get('source')

        if source and not self.instance.pk and source.quotes.count() >= 3:
            raise forms.ValidationError(
                {'source': 'У этого источника уже 3 цитаты. Максимальное количество достигнуто.'}
            )
        return cleaned_data


@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'quotes_count')
    list_filter = ('type',)
    search_fields = ('name',)

    def quotes_count(self, obj):
        return obj.quotes.count()

    quotes_count.short_description = 'Количество цитат'


@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    form = QuoteForm
    list_display = ('truncated_text', 'source', 'weight', 'views', 'created_at')
    list_filter = ('source__type', 'created_at')
    search_fields = ('text', 'source__name')
    list_editable = ('weight',)
    readonly_fields = ('views', 'likes', 'dislikes', 'created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('text', 'source', 'weight')
        }),
        ('Статистика', {
            'fields': (('views', 'likes', 'dislikes'),
                       ('created_at', 'updated_at')),
            'classes': ('collapse',)
        }),
    )

    def truncated_text(self, obj):
        return obj.text[:100] + '...' if len(obj.text) > 100 else obj.text

    truncated_text.short_description = 'Текст цитаты'