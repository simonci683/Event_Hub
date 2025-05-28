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
    eventi = Evento.objects.all().order_by('nome')
    return render(request, 'eventi.html', {'eventi': eventi})

def carrello(request):
    if request.method == 'POST':
        evento_nome = request.POST.get('evento_nome')
        numero_biglietti = int(request.POST.get('numero_biglietti', 1))
        utente_email = request.session.get('utente_email')

        if not utente_email:
            return redirect('login')

        try:
            utente = Utente.objects.get(email=utente_email)
            evento = Evento.objects.get(nome=evento_nome)

            # Check if the user already has a cart for this event
            existing_cart = carrello.objects.filter(utente=utente, evento=evento).first()
            if existing_cart:
                existing_cart.numero_biglietti += numero_biglietti
                existing_cart.save()
            else:
                carrello.objects.create(
                    utente=utente,
                    evento=evento,
                    numero_biglietti=numero_biglietti
                )
            return redirect('eventi')
        except (Utente.DoesNotExist, Evento.DoesNotExist):
            return render(request, 'error.html', {'message': 'Evento o utente non trovato.'})

    return render(request, 'carrello.html')