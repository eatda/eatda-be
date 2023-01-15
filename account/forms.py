from django import forms

from .models import User


class UserCreationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('social_id', 'social_provider', 'email')

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('social_id', 'social_provider', 'email')
