"""
URL configuration for Event_Hub project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.shortcuts import redirect
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from Event_Hub.views import (
    registrati, login, benvenuto, aggiungi_al_carrello, carrello, rimuovi_dal_carrello,
    area_personale, biglietti, profilo, storico_acquisti, recensioni, eventi_salvati, salva_evento,
    checkout
)
from .views import lista_eventi

urlpatterns = [
    #path('admin/', admin.site.urls),
    path('admin/', admin.site.urls),
    path('', lambda request: redirect('benvenuto'), name='home'),
    path('benvenuto/', benvenuto, name='benvenuto'),
    path('Registrati/', registrati, name='Registrati'),
    path('login/', login, name='login'),
    path('eventi/', lista_eventi, name='eventi'),
    path('carrello/', carrello, name='carrello'),
    path('aggiungi-al-carrello/', aggiungi_al_carrello, name='aggiungi_al_carrello'),
    path('rimuovi-dal-carrello/', rimuovi_dal_carrello, name='rimuovi_dal_carrello'),
    path('checkout/', checkout, name='checkout'),

    # Area Personale URLs
    path('area-personale/', area_personale, name='area_personale'),
    path('area-personale/biglietti/', biglietti, name='biglietti'),
    path('area-personale/profilo/', profilo, name='profilo'),
    path('area-personale/storico-acquisti/', storico_acquisti, name='storico_acquisti'),
    path('area-personale/recensioni/', recensioni, name='recensioni'),
    path('area-personale/eventi-salvati/', eventi_salvati, name='eventi_salvati'),
    path('salva-evento/', salva_evento, name='salva_evento'),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
