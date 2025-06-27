from django.shortcuts import render, redirect, get_object_or_404
from Event_Hub.models import Utente, Organizzatore, Evento, Prenotazione, Recensione, Carrello, EventoSalvato
from .models import Evento
from django.db.models import Q
import hashlib
from django.contrib import messages
from django.utils import timezone
from django.shortcuts import render, redirect
from Event_Hub.models import Utente


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
            # Set up the user session
            request.session['utente_email'] = utente.email
            return redirect('eventi')
        except Utente.DoesNotExist:
            return render(request, 'login.html', {'error': 'Credenziali non valide'})

    return render(request, 'login.html')

def login_organizzatore(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Hash the password for comparison
        hashed_password = hashlib.md5(password.encode()).hexdigest()

        try:
            organizzatore = Organizzatore.objects.get(email=email, password=hashed_password)
            # Set up the organizer session
            request.session['organizzatore_email'] = organizzatore.email
            return redirect('principale_organizzatore')
        except Organizzatore.DoesNotExist:
            return render(request, 'login_organizzatore.html', {'error': 'Credenziali non valide'})

    return render(request, 'login_organizzatore.html')

def principale_organizzatore(request):
    # Check if organizer is logged in
    organizzatore_email = request.session.get('organizzatore_email')
    if not organizzatore_email:
        return redirect('login_organizzatore')

    try:
        organizzatore = Organizzatore.objects.get(email=organizzatore_email)
        context = {
            'organizzatore': organizzatore,
        }
        return render(request, 'principale_organizzatore.html', context)
    except Organizzatore.DoesNotExist:
        # If organizer doesn't exist, clear session and redirect to login
        request.session.flush()
        return redirect('login_organizzatore')

def crea_evento(request):
    # Check if organizer is logged in
    organizzatore_email = request.session.get('organizzatore_email')
    if not organizzatore_email:
        return redirect('login_organizzatore')

    if request.method == 'POST':
        try:
            organizzatore = Organizzatore.objects.get(email=organizzatore_email)

            # Get form data
            nome = request.POST.get('nome')
            data = request.POST.get('data')
            ora_inizio = request.POST.get('ora_inizio')
            ora_fine = request.POST.get('ora_fine')
            luogo = request.POST.get('luogo')
            descrizione = request.POST.get('descrizione')
            biglietti_disponibili = request.POST.get('biglietti_disponibili')
            prezzo = request.POST.get('prezzo')

            # Validate data
            if not all([nome, data, ora_inizio, ora_fine, luogo, descrizione, biglietti_disponibili, prezzo]):
                return render(request, 'principale_organizzatore.html', {
                    'organizzatore': organizzatore,
                    'error_message': 'Tutti i campi sono obbligatori.'
                })

            # Create the event
            Evento.objects.create(
                nome=nome,
                data=data,
                ora_inizio=ora_inizio,
                ora_fine=ora_fine,
                luogo=luogo,
                descrizione=descrizione,
                organizzatore=organizzatore,
                biglietti_disponibili=biglietti_disponibili,
                prezzo=prezzo
            )

            return render(request, 'principale_organizzatore.html', {
                'organizzatore': organizzatore,
                'success_message': 'Evento creato con successo!'
            })

        except Organizzatore.DoesNotExist:
            request.session.flush()
            return redirect('login_organizzatore')
        except Exception as e:
            organizzatore = Organizzatore.objects.get(email=organizzatore_email)
            return render(request, 'principale_organizzatore.html', {
                'organizzatore': organizzatore,
                'error_message': f'Errore durante la creazione dell\'evento: {str(e)}'
            })

    # If not POST, redirect to the main organizer page
    return redirect('principale_organizzatore')

def benvenuto(request):
    return render(request, 'Benvenuto.html')

def logout(request):
    # Clear the user session
    request.session.flush()
    # Redirect to the welcome page
    return redirect('benvenuto')

def lista_eventi(request):
    eventi = Evento.objects.all().order_by('nome')
    return render(request, 'eventi.html', {'evexenti': eventi})

def aggiungi_al_carrello(request):
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
            existing_cart = Carrello.objects.filter(utente=utente, evento=evento).first()
            if existing_cart:
                existing_cart.numero_biglietti += numero_biglietti
                existing_cart.save()
            else:
                Carrello.objects.create(
                    utente=utente,
                    evento=evento,
                    numero_biglietti=numero_biglietti
                )
            return redirect('carrello')
        except (Utente.DoesNotExist, Evento.DoesNotExist):
            return render(request, 'error.html', {'message': 'Evento o utente non trovato.'})

    return redirect('eventi')

def carrello(request):
    utente_email = request.session.get('utente_email')

    if not utente_email:
        return redirect('login')

    try:
        utente = Utente.objects.get(email=utente_email)
        Carrello_items = Carrello.objects.filter(utente=utente).select_related('evento')

        # Calculate subtotals for each item
        items_with_subtotals = []
        totale = 0

        for item in Carrello_items:
            subtotale = item.evento.prezzo * item.numero_biglietti
            totale += subtotale
            items_with_subtotals.append({
                'item': item,
                'subtotale': subtotale
            })

        context = {
            'carrello_items': items_with_subtotals,
            'totale': totale
        }

        return render(request, 'carrello.html', context)
    except Utente.DoesNotExist:
        return redirect('login')

def rimuovi_dal_carrello(request):
    if request.method == 'POST':
        evento_nome = request.POST.get('evento_nome')
        utente_email = request.session.get('utente_email')

        if not utente_email:
            return redirect('login')

        try:
            utente = Utente.objects.get(email=utente_email)
            evento = Evento.objects.get(nome=evento_nome)

            # Find and delete the cart item
            cart_item = get_object_or_404(Carrello, utente=utente, evento=evento)
            cart_item.delete()

            return redirect('carrello')
        except (Utente.DoesNotExist, Evento.DoesNotExist):
            return render(request, 'error.html', {'message': 'Evento o utente non trovato.'})

    return redirect('carrello')

# Area Personale Views
def area_personale(request):
    utente_email = request.session.get('utente_email')

    if not utente_email:
        return redirect('login')

    try:
        utente = Utente.objects.get(email=utente_email)

        # Get recent tickets
        biglietti_recenti = Prenotazione.objects.filter(utente=utente).order_by('-data_prenotazione')[:3]

        # Get saved events
        eventi_salvati = EventoSalvato.objects.filter(utente=utente).order_by('-data_salvataggio')[:3]

        # Get recent reviews
        recensioni_recenti = Recensione.objects.filter(utente=utente).order_by('-data_recensione')[:3]

        context = {
            'utente': utente,
            'biglietti_recenti': biglietti_recenti,
            'eventi_salvati': eventi_salvati,
            'recensioni_recenti': recensioni_recenti
        }

        return render(request, 'area_personale.html', context)
    except Utente.DoesNotExist:
        return redirect('login')

def biglietti(request):
    utente_email = request.session.get('utente_email')

    if not utente_email:
        return redirect('login')

    try:
        utente = Utente.objects.get(email=utente_email)
        biglietti_list = Prenotazione.objects.filter(utente=utente).order_by('-data_prenotazione')

        # Calculate total price for each ticket
        biglietti_with_totals = []
        for biglietto in biglietti_list:
            prezzo_totale = biglietto.evento.prezzo * biglietto.numero_biglietti
            biglietti_with_totals.append({
                'biglietto': biglietto,
                'prezzo_totale': prezzo_totale
            })

        context = {
            'utente': utente,
            'biglietti': biglietti_with_totals
        }

        return render(request, 'biglietti.html', context)
    except Utente.DoesNotExist:
        return redirect('login')

def rimborsa_biglietto(request):
    if request.method == 'POST':
        ticket_id = request.POST.get('ticket_id')
        utente_email = request.session.get('utente_email')

        if not utente_email:
            return redirect('login')

        try:
            utente = Utente.objects.get(email=utente_email)
            biglietto = Prenotazione.objects.get(ticket_id=ticket_id, utente=utente)

            # Check if the ticket is active (can only refund active tickets)
            if biglietto.stato == 'attivo':
                # Update ticket status to refunded
                biglietto.stato = 'rimborsato'
                biglietto.save()

                # Increase available tickets for the event
                evento = biglietto.evento
                evento.biglietti_disponibili += biglietto.numero_biglietti
                evento.save()

                messages.success(request, 'Biglietto rimborsato con successo.')
            else:
                messages.error(request, 'Solo i biglietti attivi possono essere rimborsati.')

            return redirect('biglietti')
        except Utente.DoesNotExist:
            return redirect('login')
        except Prenotazione.DoesNotExist:
            messages.error(request, 'Biglietto non trovato.')
            return redirect('biglietti')

    return redirect('biglietti')

def profilo(request):
    utente_email = request.session.get('utente_email')

    if not utente_email:
        return redirect('login')

    try:
        utente = Utente.objects.get(email=utente_email)

        if request.method == 'POST':
            # Update user profile
            utente.nome = request.POST.get('nome', utente.nome)
            utente.cognome = request.POST.get('cognome', utente.cognome)
            utente.telefono = request.POST.get('telefono', utente.telefono)

            # Handle password change
            current_password = request.POST.get('current_password')
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')

            if current_password and new_password and confirm_password:
                hashed_current = hashlib.md5(current_password.encode()).hexdigest()

                if hashed_current == utente.password:
                    if new_password == confirm_password:
                        utente.password = hashlib.md5(new_password.encode()).hexdigest()
                        messages.success(request, 'Password aggiornata con successo.')
                    else:
                        messages.error(request, 'Le nuove password non corrispondono.')
                else:
                    messages.error(request, 'Password attuale non corretta.')

            # Handle profile picture
            if 'foto_profilo' in request.FILES:
                utente.foto_profilo = request.FILES['foto_profilo']

            utente.save()
            messages.success(request, 'Profilo aggiornato con successo.')

        context = {
            'utente': utente
        }

        return render(request, 'profilo.html', context)
    except Utente.DoesNotExist:
        return redirect('login')

def storico_acquisti(request):
    utente_email = request.session.get('utente_email')

    if not utente_email:
        return redirect('login')

    try:
        utente = Utente.objects.get(email=utente_email)

        # Get filter parameters
        data_inizio = request.GET.get('data_inizio')
        data_fine = request.GET.get('data_fine')
        tipo_evento = request.GET.get('tipo_evento')
        location = request.GET.get('location')

        # Start with all user's bookings
        acquisti = Prenotazione.objects.filter(utente=utente)

        # Apply filters if provided
        if data_inizio:
            acquisti = acquisti.filter(data_prenotazione__gte=data_inizio)
        if data_fine:
            acquisti = acquisti.filter(data_prenotazione__lte=data_fine)
        if tipo_evento:
            acquisti = acquisti.filter(evento__nome__icontains=tipo_evento)
        if location:
            acquisti = acquisti.filter(evento__luogo__icontains=location)

        # Order by date (most recent first)
        acquisti = acquisti.order_by('-data_prenotazione')

        context = {
            'utente': utente,
            'acquisti': acquisti,
            'filtri': {
                'data_inizio': data_inizio,
                'data_fine': data_fine,
                'tipo_evento': tipo_evento,
                'location': location
            }
        }

        return render(request, 'storico_acquisti.html', context)
    except Utente.DoesNotExist:
        return redirect('login')

def recensioni(request):
    utente_email = request.session.get('utente_email')

    if not utente_email:
        return redirect('login')

    try:
        utente = Utente.objects.get(email=utente_email)

        # Get all user's bookings for past events (potential events to review)
        eventi_passati = Prenotazione.objects.filter(
            utente=utente,
            evento__data__lt=timezone.now().date()
        ).select_related('evento')

        # Get all user's reviews
        recensioni_utente = Recensione.objects.filter(utente=utente).order_by('-data_recensione')

        if request.method == 'POST':
            evento_nome = request.POST.get('evento_nome')
            valutazione = request.POST.get('valutazione')
            commento = request.POST.get('commento')

            if evento_nome and valutazione and commento:
                try:
                    evento = Evento.objects.get(nome=evento_nome)

                    # Check if user already reviewed this event
                    existing_review = Recensione.objects.filter(utente=utente, evento=evento).first()

                    if existing_review:
                        # Update existing review
                        existing_review.valutazione = valutazione
                        existing_review.commento = commento
                        existing_review.save()
                        messages.success(request, 'Recensione aggiornata con successo.')
                    else:
                        # Create new review
                        Recensione.objects.create(
                            utente=utente,
                            evento=evento,
                            valutazione=valutazione,
                            commento=commento
                        )
                        messages.success(request, 'Recensione inviata con successo.')

                    return redirect('recensioni')
                except Evento.DoesNotExist:
                    messages.error(request, 'Evento non trovato.')
            else:
                messages.error(request, 'Tutti i campi sono obbligatori.')

        context = {
            'utente': utente,
            'eventi_passati': eventi_passati,
            'recensioni': recensioni_utente
        }

        return render(request, 'recensioni.html', context)
    except Utente.DoesNotExist:
        return redirect('login')

def eventi_salvati(request):
    utente_email = request.session.get('utente_email')

    if not utente_email:
        return redirect('login')

    try:
        utente = Utente.objects.get(email=utente_email)

        # Get all saved events
        saved_events = EventoSalvato.objects.filter(utente=utente).select_related('evento').order_by('-data_salvataggio')

        if request.method == 'POST':
            action = request.POST.get('action')
            evento_nome = request.POST.get('evento_nome')

            if action and evento_nome:
                try:
                    evento = Evento.objects.get(nome=evento_nome)
                    saved_event = EventoSalvato.objects.filter(utente=utente, evento=evento).first()

                    if action == 'remove' and saved_event:
                        # Remove from saved events
                        saved_event.delete()
                        messages.success(request, 'Evento rimosso dai preferiti.')
                    elif action == 'toggle_notifications' and saved_event:
                        # Toggle notifications
                        saved_event.notifiche_attive = not saved_event.notifiche_attive
                        saved_event.save()
                        status = 'attivate' if saved_event.notifiche_attive else 'disattivate'
                        messages.success(request, f'Notifiche {status} per questo evento.')

                    return redirect('eventi_salvati')
                except Evento.DoesNotExist:
                    messages.error(request, 'Evento non trovato.')

        # Get current date for countdown
        today = timezone.now().date()

        context = {
            'utente': utente,
            'eventi_salvati': saved_events,
            'today': today
        }

        return render(request, 'eventi_salvati.html', context)
    except Utente.DoesNotExist:
        return redirect('login')

def salva_evento(request):
    if request.method == 'POST':
        evento_nome = request.POST.get('evento_nome')
        utente_email = request.session.get('utente_email')

        if not utente_email:
            return redirect('login')

        try:
            utente = Utente.objects.get(email=utente_email)
            evento = Evento.objects.get(nome=evento_nome)

            # Check if already saved
            existing = EventoSalvato.objects.filter(utente=utente, evento=evento).first()

            if not existing:
                EventoSalvato.objects.create(
                    utente=utente,
                    evento=evento
                )
                messages.success(request, 'Evento salvato nei preferiti.')
            else:
                messages.info(request, 'Evento già nei preferiti.')

            return redirect('eventi')
        except (Utente.DoesNotExist, Evento.DoesNotExist):
            return render(request, 'error.html', {'message': 'Evento o utente non trovato.'})

    return redirect('eventi')

def checkout(request):
    utente_email = request.session.get('utente_email')

    if not utente_email:
        return redirect('login')

    try:
        utente = Utente.objects.get(email=utente_email)
        carrello_items = Carrello.objects.filter(utente=utente).select_related('evento')

        if not carrello_items:
            messages.info(request, 'Il tuo carrello è vuoto.')
            return redirect('carrello')

        # Process each cart item
        for item in carrello_items:
            evento = item.evento
            numero_biglietti = item.numero_biglietti

            # Check if there are enough tickets available
            if evento.biglietti_disponibili < numero_biglietti:
                messages.error(request, f'Non ci sono abbastanza biglietti disponibili per {evento.nome}. Disponibili: {evento.biglietti_disponibili}')
                return redirect('carrello')

            # Create a new booking
            Prenotazione.objects.create(
                utente=utente,
                evento=evento,
                numero_biglietti=numero_biglietti,
                stato='attivo'
            )

            # Update available tickets
            evento.biglietti_disponibili -= numero_biglietti
            evento.save()

        # Clear the cart after successful purchase
        carrello_items.delete()

        messages.success(request, 'Acquisto completato con successo! Puoi vedere i tuoi biglietti nella sezione "Biglietti".')
        return redirect('biglietti')

    except Utente.DoesNotExist:
        return redirect('login')
    except Exception as e:
        messages.error(request, f'Si è verificato un errore durante l\'acquisto: {str(e)}')
        return redirect('carrello')

def lista_eventi(request):
    eventi = Evento.objects.all().order_by('nome')
    return render(request, 'eventi.html', {'eventi': eventi})
