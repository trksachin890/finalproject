from django import forms
from .models import ProductReview

class RatingForm(forms.ModelForm):
    class Meta:
        model = ProductReview
        fields = ['rating']
        widgets = {
            'rating': forms.RadioSelect(choices=[
                (1, "★☆☆☆☆"),
                (2, "★★☆☆☆"),
                (3, "★★★☆☆"),
                (4, "★★★★☆"),
                (5, "★★★★★"),
            ])
        }