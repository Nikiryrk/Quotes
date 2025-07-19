from django import forms
from .models import Quote, Source


class SourceForm(forms.ModelForm):
    class Meta:
        model = Source
        fields = ['name', 'type']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Название источника'}),
            'type': forms.Select(attrs={'class': 'source-type-select'})
        }


class QuoteForm(forms.ModelForm):
    new_source_name = forms.CharField(
        required=False,
        label='Добавьте новый источник',
        widget=forms.TextInput(attrs={'placeholder': 'Название нового источника'})
    )
    new_source_type = forms.ChoiceField(
        required=False,
        choices=Source.TYPE_CHOICES,
        label='Тип нового источника',
        widget=forms.Select(attrs={'class': 'source-type-select'})
    )

    class Meta:
        model = Quote
        fields = ['text', 'source', 'weight']
        labels = {
            'text': 'Содержание цитаты',
            'source': 'Выберите источник',
            'weight': 'Вероятность появления (1-10)',
        }
        widgets = {
            'text': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['source'].required = False

    def clean(self):
        cleaned_data = super().clean()
        source = cleaned_data.get('source')
        new_source_name = cleaned_data.get('new_source_name')
        new_source_type = cleaned_data.get('new_source_type')

        if not source and not new_source_name:
            raise forms.ValidationError('Необходимо выбрать существующий источник или создать новый')

        if source and new_source_name:
            raise forms.ValidationError(
                'Пожалуйста, выберите только один вариант - существующий источник или создание нового')

        return cleaned_data

    def save(self, commit=True):
        quote = super().save(commit=False)
        new_source_name = self.cleaned_data.get('new_source_name')

        if new_source_name:
            new_source_type = self.cleaned_data.get('new_source_type')
            source = Source.objects.create(
                name=new_source_name,
                type=new_source_type
            )
            quote.source = source

        if commit:
            quote.save()
        return quote