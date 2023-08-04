from django import forms
from .models import Review


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = {'original_text'}
        labels = {'original_text': ''}
        widgets = {
            'original_text': forms.Textarea(attrs={'rows': 8, 'cols': 40})
        }
