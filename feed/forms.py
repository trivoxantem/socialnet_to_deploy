from django import forms
from .models import Profile
from .models import Group

class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['profile_picture', 'bio']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Tell us about yourself...'}),
        }


class GroupCreateForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name']