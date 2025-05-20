from django import forms
from Event_Hub.models import Utente

class RegistrazioneForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Utente
        fields = ['nome', 'cognome', 'data_nascita', 'email', 'password']