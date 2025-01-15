from django import forms
from .models import GalleryImage


class GalleryImageForm(forms.ModelForm):
    class Meta:
        model = GalleryImage
        fields = ["image", "orientation"]
        widgets = {
            "orientation": forms.Select(choices=GalleryImage.ORIENTATION_CHOICES),
        }
