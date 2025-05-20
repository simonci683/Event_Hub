from django.db import models

class Utente(models.Model):
    nome = models.CharField(max_length=30)
    cognome = models.CharField(max_length=30)
    data_nascita = models.DateField()
    email = models.EmailField(unique=True, primary_key=True)
    password = models.CharField(max_length=128)

class Organizzatore(models.Model):
    nome = models.CharField(max_length=30)
    cognome = models.CharField(max_length=30)
    email = models.EmailField(unique=True, primary_key=True)
    password = models.CharField(max_length=128)

class Evento(models.Model):
    nome = models.CharField(max_length=100, primary_key=True)
    data = models.DateField()
    ora_inizio = models.TimeField()
    ora_fine = models.TimeField()
    luogo = models.CharField(max_length=100)
    descrizione = models.TextField()
    organizzatore = models.ForeignKey(Organizzatore, on_delete=models.CASCADE)
    biglietti_disponibili = models.IntegerField()

class Prenotazione(models.Model):
    ticket_id = models.AutoField(primary_key=True)
    utente = models.ForeignKey(Utente, on_delete=models.CASCADE)
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE)
    numero_biglietti = models.IntegerField()
    data_prenotazione = models.DateField(auto_now_add=True)

class Recensione(models.Model):
    id = models.AutoField(primary_key=True)
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE)
    utente = models.ForeignKey(Utente, on_delete=models.CASCADE)
    valutazione = models.IntegerField()
    commento = models.TextField()
    data_recensione = models.DateField(auto_now_add=True)

