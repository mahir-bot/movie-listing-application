from django import forms
from .models import Cast, Category, Movie
from django.forms.widgets import DateInput


class MovieForm(forms.ModelForm):
    class Meta:
        model = Movie
        fields = ['title', 'release_date', 'budget',
                  'category', 'casts', 'thumbnail']

    release_date = forms.DateField(
        widget=DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    category = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control'})
    )
    casts = forms.ModelMultipleChoiceField(
        queryset=Cast.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control'})
    )


class AddCastForm(forms.ModelForm):
    class Meta:
        model = Cast
        fields = ['name']


class AddCategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']
