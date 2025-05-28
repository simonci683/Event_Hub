from django.contrib import admin
from .models import Utente, Organizzatore, Evento, Prenotazione, Recensione

admin.site.register(Utente)
admin.site.register(Organizzatore)
admin.site.register(Evento)
admin.site.register(Prenotazione)
admin.site.register(Recensione)

