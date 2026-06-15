import time
import random
import json
import pyttsx3
import speech_recognition as sr
import pygame 
from main import ReachyMini, VELOCITA_PARLATA, PAUSA_BREVE, PAUSA_LUNGA, engine, RECOGNIZER, MIC, ascolto_risposta, inizializza_robot

frasi_incoraggiamento = [
    "Quasi! Ma non è la risposta corretta. Riproviamo!",
    "non è questa ma ci sei andato vicino! Riparte la musica",
    "Non proprio, ma c'è ancora tempo per indovinare!",
    "Peccato! La risposta è sbagliata. Non mollare!",
    "Fuochino... ma non è questa!",
    "Bella canzone, ma non è il titolo giusto. Ritentiamo!",
    "Ah, non è questa! Ma sono sicuro che la prossima volta farete centro.",
    "Ottimo tentativo, ma dobbiamo riprovare!",
    "Non è questa, ma il ritmo è quello giusto! Riparte la musica",
    "Ci siete quasi! Ascoltiamola di nuovo! e riprovate",
    "Risposta non corretta, ma il gioco è ancora aperto!",
    "Putroppo non è questa! Ascoltiamo un altro pezzetto.",
    "La risposta è un'altra, ma apprezzo tantissimo il tentativo!",
    "Mmm, non è il titolo esatto. Chi vuole riprovare?",
    "Bella intuizione, ma non è il pezzo corretto!",
    "Purtroppo non è questo il titolo. Non preoccuparti, capita! La musica riparte.",
    "Ottimo coraggio, ma il titolo è un altro! Forza riproviamo!",
    "Non è questa, ma la prossima potrebbe essere quella buona!"
]

#----------------------INIZIALIZZAZIONE ----------------------
#variabili/dizionari/liste per gestire lo stato del gioco
giocatori_punteggi = {}
playlist = []
canzoni_giocate = []
canzone_corrente = None
gioco_terminato = False

def inizializza_gioco():
    inizializza_robot()
    ascolto_risposta()

    #musica 
    pygame.mixer.init()
    lista_canzoni = carica_playlist("canzoni.json")

    #stato gioco
    stato_gioco = {
    "giocatori_punteggi" : {},
    "playlist" : lista_canzoni,
    "canzoni_giocate" : [],
    "canzone_corrente" : None,
    "gioco_terminato" : False,
    }

    return stato_gioco

def carica_playlist(canzoni):
    with open(canzoni, 'r', encoding='utf-8') as file: #r serve per leggere il file, encoding serve per leggere i caratteri speciali
        playlist = json.load(file)
    return playlist

#----------------------FUNZIONI PER JUKBOXE----------------------
def presentazione_gioco(reachy: ReachyMini):
    engine.say("Benvenuti al gioco del Jukebox!")
    engine.pause(PAUSA_BREVE)
    engine.say("Io sono Reachy, e insieme all'animatrice, vi faremo ascoltare delle canzoni.")
    engine.pause(PAUSA_BREVE)
    engine.say("Il gioco è semplice: quando pensate di sapere il titolo della canzone alzate la mano.")
    engine.pause(PAUSA_BREVE)
    engine.say("L'animatrice fermerà la musica e vi chiederà la risposta")
    engine.pause(PAUSA_BREVE)
    engine.say("Se la risposta è corretta, guadagnerete un punto e passeremo alla canzone successiva.")
    engine.pause(PAUSA_BREVE)
    engine.say("Altrimenti se è sbagliata non vi preoccupate, la musica ricomincierà e potrete riprovare!")
    engine.pause(PAUSA_BREVE)
    engine.say("Dopo 15 canzoni, il gioco terminerà e vedremo chi è il vincitore!")
    engine.pause(PAUSA_BREVE)

def inizializza_giocatori(stato_gioco):
    engine.say("Prima di iniziare, registriamo i nomi dei giocatori.")
    engine.pause(PAUSA_BREVE)
    engine.say("Animatrice, per favore, dimmi un nome alla volta. Quando hai finito, dì 'fine'.")
   
    while True:
        nome_giocatore = ascolto_risposta()
        if nome_giocatore in ["fine", "terminato", "stop", "basta", "finito"]:
            engine.say("Grazie! Ora siamo pronti per iniziare il gioco.")
            break
        else:
            stato_gioco["giocatori_punteggi"][nome_giocatore] = 0 #inizializza punteggio a 0 per ogni nome    
            engine.say(f"{nome_giocatore} registrato!")

    return stato_gioco["giocatori_punteggi"]

def estrai_canzone(stato_gioco):
    canzoni_disponibili = []
    for canzone in stato_gioco["playlist"]: 
        if canzone not in stato_gioco["canzoni_giocate"]:
            canzoni_disponibili.append(canzone)
    if not canzoni_disponibili:
        return None  # controllo aggiuntivo ->Tutte le canzoni sono state giocate
    canzone_estratta = random.choice(canzoni_disponibili)
    stato_gioco["canzone_corrente"] = canzone_estratta
    stato_gioco["canzoni_giocate"].append(canzone_estratta)
    return canzone_estratta

#classifica_finale[0]      → ("Mario", 5)   intera tupla
#classifica_finale[0][0]   → "Mario"         nome
#classifica_finale[0][1]   → 5               punteggio
def fine_gioco(stato_gioco):
    stato_gioco["gioco_terminato"] = True
    classifica_finale = sorted(stato_gioco["giocatori_punteggi"].items(),key=lambda x: x[1], reverse=True)
    punteggio_max=  0
    punteggio_max= classifica_finale[0][1] #per prendere solo il punteggio 
    #ciclo per vedere se ci sono pareggi 
    if punteggio_max != classifica_finale[1][1]:
        nome_vincitore, punteggio_vincitore = classifica_finale[0]
        engine.say(f"{nome_vincitore} con {punteggio_vincitore} punti! Complimenti!")

    elif punteggio_max == classifica_finale[1][1]:
        vincitori=[]
        i=0
        while i<len(classifica_finale) and punteggio_max==classifica_finale[i][0]:
            vincitori.append(classifica_finale[i][0])
            i+=1
        engine.say("Aspettate, abbiamo un pareggio!")
        engine.pause(PAUSA_BREVE)
        engine.say("I vincitori sono...")
        engine.say(PAUSA_LUNGA)
        engine.say("I vincitori sono:")
        for nome in vincitori:
            engine.pause(PAUSA_BREVE)
            engine.say(f"{nome} con {punteggio_max} punti!")

    #saluti finali        
    engine.pause(PAUSA_BREVE)
    engine.say("Grazie a tutti per aver partecipato! È stato bello giocare con voi!")


#----------------------COMANDI ANIMATRICE----------------------
#stop al gioco in qualsiasi momento nel caso di emergenza
def start_gioco(reachy, comando):
    #"inizia il gioco" 
    engine.say("Se siamo tutti ponti, animatrice dimmi 'via'!")
    engine.pause(PAUSA_BREVE)
    risposta = ascolto_risposta()
    if risposta == "via":
        engine.say("Perfetto! Iniziamo il gioco!")
        #inizia il gioco
    else:
        engine.say("Non ho capito, ripetilo per favore.")
        start_gioco(reachy, comando)

def stop_gioco(stato_gioco, comando):
    #"interrompi il gioco" in caso di emergenzaa 
    pygame.mixer.music.pause()
    engine.say("Il gioco è stato momentaneamente interrotto")
    engine.pause(PAUSA_LUNGA)
    engine.say("Animatrice, vuoi riprendere il gioco? dimmi si o no")
    risposta = ascolto_risposta()
    if risposta == "si":
        engine.say("Perfetto! Riprendiamo il gioco!")
        pygame.mixer.music.unpause()
        return True
    elif risposta == "no":
        engine.say("Va bene, il gioco termina qui. Grazie a tutti per aver partecipato! È stato bello giocare con voi!")
        stato_gioco["gioco_terminato"] = True
        return False
    else:
        engine.say("Non ho capito, ripetilo per favore.")
    
     
#ferma la musica (per far dire titolo della canzone)
def ferma_musica(stato_gioco, canzone_corrente):
    pygame.mixer.music.pause()
    engine.say("Animatrice, per favore, chiedi al giocatore il titolo della canzone.")
    titolo_risposta = ascolto_risposta()
    #se risposta giusta -> assegna punto 
    if titolo_risposta == canzone_corrente["titolo"]:
        pygame.mixer.music.stop()
        engine.say("Risposta corretta! A chi assegno il punto?")
        giocatore=ascolto_risposta()
        stato_gioco["giocatori_punteggi"][giocatore] += 1
        engine.say(f"Perfetto! {giocatore} ha guadagnato un punto!")
        return True
    #se risposta sbagliata -> nessun punto -> riprende la stessa canzone
    elif titolo_risposta != canzone_corrente["titolo"]:
        engine.say(random.choice(frasi_incoraggiamento))
        engine.pause(PAUSA_BREVE)
        pygame.mixer.music.unpause()
        return False




#----------------------FLUSSO DEL GIOCO----------------------
def jukebox(reachy: ReachyMini, comando: str):
    stato_gioco = inizializza_gioco()
    presentazione_gioco(reachy)
    inizializza_giocatori(stato_gioco)
    start_gioco(reachy, "via")

    while len(stato_gioco["canzoni_giocate"]) < 15:
        canzone_corrente = estrai_canzone(stato_gioco)
       
        if canzone_corrente is None:
            engine.say("Tutte le canzoni sono state giocate. Il gioco termina qui.")
            break

        pygame.mixer.music.load(canzone_corrente["file_path"])
        pygame.mixer.music.play()

        #aspetta che animatrice ferma la musica
        while True:
            comando = ascolto_risposta()
            if comando == "ferma la musica":
                controllo_risposta = ferma_musica(stato_gioco, canzone_corrente)
                if controllo_risposta == True: #se risposta corretta -> sorteggia altra canzone 
                    break #riprende da riga 182 
                elif controllo_risposta == False: #se risposta errata -> nessun punto -> riprende la stessa canzone
                    continue

            if comando == "interrompi il gioco":
                controllo_risposta=stop_gioco(stato_gioco, comando)
                if controllo_risposta == True: #gioco è stato interrotto e riprende
                    continue
                elif controllo_risposta == False: #gioco è stato interrotto e termina
                    termina_gioco(stato_gioco)
                    break

            #dare indizio se trascorso piu di 1 minuto senza risposte
            tempo_trascorso = pygame.mixer.music.get_pos()
            if tempo_trascorso > 60000: #1 minuto
                pygame.mixer.music.pause() #pausa la musica per dare l'indizio
                engine.say(f"Indizio: il cantante di questa canzone è {canzone_corrente['artista']}")
                engine.pause(PAUSA_BREVE)
                engine.say("Ora riparte la musica!")
                pygame.mixer.music.unpause() #riprende la musica dopo l'indizio
            #aspettare altri 30 secondi -> se nessuno indovina -> dire il titolo e cambiare canzone
            while True:
                if comando == "ferma la musica":
                    controllo_risposta = ferma_musica(stato_gioco, canzone_corrente)
                    if controllo_risposta == True: #se risposta corretta -> sorteggia altra canzone 
                        break #riprende da riga 182 
                    elif controllo_risposta == False: #se risposta errata -> nessun punto -> riprende la stessa canzone
                        continue
                if tempo_trascorso > 90000: #1 minuto + 30 secondi
                    pygame.mixer.music.stop() #ferma la musica
                    engine.say("Mannaggia, questa era difficile!")
                    engine.pause(PAUSA_BREVE)
                    engine.say(f"Il titolo di questa canzone è {canzone_corrente['titolo']}. Ascoltiamo un'altra canzone!")
                    break #riprende da riga 182
    
    fine_gioco(stato_gioco)
            