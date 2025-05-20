from django.shortcuts import render, redirect
from Event_Hub.models import Utente, Organizzatore, Evento, Prenotazione, Recensione
from .models import Evento
import hashlib

def registrati(request):
    if request.method == 'POST':
        nome = request.POST.get('nome')
        cognome = request.POST.get('cognome')
        data_nascita = request.POST.get('data_nascita')
        email = request.POST.get('email')
        password = request.POST.get('password')

        hashed_password = hashlib.md5(password.encode()).hexdigest()

        #crea l'utente
        Utente.objects.create(
            nome=nome,
            cognome=cognome,
            data_nascita=data_nascita,
            email=email,
            password=hashed_password
        )
        return redirect('login')
    return render(request, 'Registrati.html')

def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Hash the password for comparison
        hashed_password = hashlib.md5(password.encode()).hexdigest()

        try:
            utente = Utente.objects.get(email=email, password=hashed_password)
            # Here you would typically set up a session
            return redirect('eventi')
        except Utente.DoesNotExist:
            return render(request, 'login.html', {'error': 'Credenziali non valide'})

    return render(request, 'login.html')

def benvenuto(request):
    return render(request, 'Benvenuto.html')

def lista_eventi(request):
    eventi = Evento.objects.all()
    return render(request, 'eventi.html', {'eventi': eventi})