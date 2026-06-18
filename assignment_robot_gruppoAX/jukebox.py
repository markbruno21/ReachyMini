import random
import time
import speech_recognition as sr
from audio_utils import parla, pausa_vocale
import pygame 
from main import PAUSA_BREVE, PAUSA_LUNGA, inizializza_robot, lista_canzoni
from reachy_mini_mock import ReachyMini
from microphone_utils import ascolto_risposta

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
canzoni_giocate = []
canzone_corrente = None
gioco_terminato = False

pygame.mixer.init()

def inizializza_gioco():
    inizializza_robot()

    #stato gioco
    stato_gioco = {
        "giocatori_punteggi": {},
        "playlist": lista_canzoni,
        "canzoni_giocate": [],
        "canzone_corrente": None,
        "gioco_terminato": False,
    }

    return stato_gioco


#----------------------FUNZIONI PER JUKBOXE----------------------
def presentazione_gioco(reachy: ReachyMini):
    parla("Benvenuti al gioco del Jukebox!")
    pausa_vocale(PAUSA_BREVE)
    parla("Io sono Reachy, e insieme all'animatrice, vi faremo ascoltare delle canzoni.")
    pausa_vocale(PAUSA_BREVE)
    parla("Il gioco è semplice: quando pensate di sapere il titolo della canzone alzate la mano.")
    pausa_vocale(PAUSA_BREVE)
    parla("L'animatrice fermerà la musica e vi chiederà la risposta")
    pausa_vocale(PAUSA_BREVE)
    parla("Se la risposta è corretta, guadagnerete un punto e passeremo alla canzone successiva.")
    pausa_vocale(PAUSA_BREVE)
    parla("Altrimenti se è sbagliata non vi preoccupate, la musica ricomincerà e potrete riprovare!")
    pausa_vocale(PAUSA_BREVE)
    parla("Dopo 15 canzoni, il gioco terminerà e vedremo chi è il vincitore!")
    pausa_vocale(PAUSA_BREVE)

def inizializza_giocatori(stato_gioco):
    parla("Prima di iniziare, registriamo i nomi dei giocatori.")
    pausa_vocale(PAUSA_BREVE)
    parla("Animatrice, per favore, dimmi un nome alla volta. Quando hai finito, dì 'fine'.")
    
    ultimo_nome_registrato = None

    while True:
        nome_giocatore = ascolto_risposta()
       
        if nome_giocatore in ["fine", "terminato", "stop", "basta", "finito"]:
            parla("Grazie! Ora siamo pronti per iniziare il gioco.")
            break
        elif nome_giocatore in ["no", "no ho sbagliato", "sbagliato", "non", "errore", "cambia"]:
            if ultimo_nome_registrato is not None:
                del stato_gioco["giocatori_punteggi"][ultimo_nome_registrato]
                parla(f"Ok, ho rimosso {ultimo_nome_registrato}. Mi ripeti il nome?")
                ultimo_nome_registrato = None
            else:
                parla("Non ho ancora registrato nessun nome da correggere. Dimmi il nome.")
            continue
        else:
            stato_gioco["giocatori_punteggi"][nome_giocatore] = 0
            ultimo_nome_registrato = nome_giocatore
            parla(f"{nome_giocatore} registrato!")

    return stato_gioco["giocatori_punteggi"]

def estrai_canzone(stato_gioco):
    canzoni_disponibili = []
    for canzone in stato_gioco["playlist"]: 
        if canzone not in stato_gioco["canzoni_giocate"]:
            canzoni_disponibili.append(canzone)
    if not canzoni_disponibili:
        return None
    canzone_corrente = random.choice(canzoni_disponibili)
    stato_gioco["canzone_corrente"] = canzone_corrente
    return canzone_corrente

def fine_gioco(stato_gioco):
    stato_gioco["gioco_terminato"] = True
    classifica_finale = sorted(stato_gioco["giocatori_punteggi"].items(), key=lambda x: x[1], reverse=True)
    punteggio_max = classifica_finale[0][1]
    
    if punteggio_max != classifica_finale[1][1] and punteggio_max > 0:
        nome_vincitore, punteggio_vincitore = classifica_finale[0]
        parla("Il vincitore è ...")
        pausa_vocale(PAUSA_LUNGA)
        parla(f"{nome_vincitore} con {punteggio_vincitore} punti! Complimenti!")

    elif punteggio_max == classifica_finale[1][1] and punteggio_max > 0:
        vincitori = []
        i = 0
        while i < len(classifica_finale) and punteggio_max == classifica_finale[i][1]:
            vincitori.append(classifica_finale[i][0])
            i += 1
        parla("Aspettate, abbiamo un pareggio!")
        pausa_vocale(PAUSA_LUNGA)
        parla("I vincitori sono:")
        for nome in vincitori:
            pausa_vocale(PAUSA_BREVE)
            parla(f"{nome} con {punteggio_max} punti!")
    else:
        parla("Non ci sono vincitori siccome nessuno ha realizzato almeno un punto.")
            
    pausa_vocale(PAUSA_BREVE)
    parla("Grazie a tutti per aver partecipato! È stato bello giocare con voi!")

def riprendi_musica(canzone_corrente, tempo_accumulato_ms):
    # Converte i millisecondi accumulati in secondi (richiesti da play)
    secondi_inizio = tempo_accumulato_ms / 1000.0
    # Ricarica e fa il play partendo dal punto esatto
    pygame.mixer.music.load(canzone_corrente["file_path"])
    pygame.mixer.music.play(start=secondi_inizio)

#----------------------COMANDI ANIMATRICE----------------------
def start_gioco(reachy, comando):
    parla("Se siamo tutti pronti, animatrice dimmi 'pronti via'!")
    pausa_vocale(PAUSA_BREVE)
    risposta = ascolto_risposta()
    if risposta == "pronti via":
        parla("Perfetto! Iniziamo il gioco!")
    else:
        parla("Non ho capito, ripetilo per favore.")
        start_gioco(reachy, comando)

def stop_gioco(stato_gioco, canzone_corrente, tempo_accumulato):
    """
    Interrompe il gioco in caso di emergenza.
    tempo_inizio_ref: lista con un elemento [time.time()] per poterlo modificare
    """
    pygame.mixer.music.pause()
    parla("Il gioco è stato momentaneamente interrotto")
    pausa_vocale(PAUSA_LUNGA)
    parla("Animatrice, vuoi riprendere il gioco? dimmi riprendi o interrompi")
    risposta = ascolto_risposta()
    if risposta == "riprendi":
        parla("Perfetto! Riprendiamo il gioco!")
        riprendi_musica(canzone_corrente, tempo_accumulato)
        return True
    elif risposta == "interrompi":
        parla("Va bene, il gioco termina qui.")
        stato_gioco["gioco_terminato"] = True
        return False
    else:
        parla("Non ho capito, ripetilo per favore.")
        # Se non capisce, riprova
        return stop_gioco(stato_gioco, canzone_corrente, tempo_accumulato)

def ferma_musica(stato_gioco, canzone_corrente, tempo_accumulato):
    """
    Ferma la musica per far dire il titolo della canzone.
    tempo_inizio_ref: lista con un elemento [time.time()] per poterlo modificare
    """
    pygame.mixer.music.pause()
    parla("Animatrice, per favore, chiedi al giocatore il titolo della canzone.")
    titolo_risposta = ascolto_risposta()
    
    if titolo_risposta == canzone_corrente["titolo"]:
        pygame.mixer.music.stop()
        parla("Risposta corretta! A chi assegno il punto?")
        giocatore = ascolto_risposta()
        stato_gioco["giocatori_punteggi"][giocatore] += 1
        parla(f"Perfetto! {giocatore} ha guadagnato un punto!")
        stato_gioco["canzoni_giocate"].append(canzone_corrente)
        return True
    else:
        parla(random.choice(frasi_incoraggiamento))
        pausa_vocale(PAUSA_BREVE)
        riprendi_musica(canzone_corrente, tempo_accumulato)
        return False


#----------------------FLUSSO DEL GIOCO----------------------
def jukebox(reachy: ReachyMini, comando: str):
    stato_gioco = inizializza_gioco()
    presentazione_gioco(reachy)
    inizializza_giocatori(stato_gioco)
    start_gioco(reachy, "via")

    while len(stato_gioco["canzoni_giocate"]) < 4:
        canzone_corrente = estrai_canzone(stato_gioco)
       
        if canzone_corrente is None:
            parla("Tutte le canzoni sono state giocate. Il gioco termina qui.")
            break

        pygame.mixer.music.load(canzone_corrente["file_path"])
        pygame.mixer.music.play()

        # VARIABILI LOCALI ALLA CANZONE 
        indizio_dato = False
        tempo_accumulato=0

        while True:
            tempo_corrente_sessione = pygame.mixer.music.get_pos()
            if tempo_corrente_sessione == -1: 
                tempo_corrente_sessione = 0

            tempo_totale_canzone = tempo_accumulato + tempo_corrente_sessione            
            comando = ascolto_risposta()
            
            if comando == "ferma la musica":
                tempo_accumulato=tempo_totale_canzone
                controllo_risposta = ferma_musica(stato_gioco, canzone_corrente, tempo_accumulato)
                if controllo_risposta == True:
                    break
                else:
                    continue

            if comando == "interrompi il gioco":
                tempo_accumulato=tempo_totale_canzone
                controllo_risposta = stop_gioco(stato_gioco, canzone_corrente, tempo_accumulato)
                if controllo_risposta == True:
                    continue
                else:
                    fine_gioco(stato_gioco)
                    return

            # dare indizio dopo 30 secondi
            if tempo_totale_canzone > 30000 and not indizio_dato:
                tempo_accumulato=tempo_totale_canzone
                pygame.mixer.music.pause()
                parla(f"Indizio: il cantante di questa canzone è {canzone_corrente['artista']}")
                pausa_vocale(PAUSA_BREVE)
                parla("Ora riparte la musica!")
                riprendi_musica(canzone_corrente, tempo_accumulato)
                indizio_dato = True
            
            # skip dopo 60 secondi totali
            if tempo_totale_canzone > 60000 and indizio_dato:
                pygame.mixer.music.stop()
                parla("Mannaggia, questa era difficile!")
                pausa_vocale(PAUSA_BREVE)
                parla(f"Il titolo di questa canzone è {canzone_corrente['titolo']}. Ascoltiamo un'altra canzone!")
                stato_gioco["canzoni_giocate"].append(canzone_corrente)
                break
    
    fine_gioco(stato_gioco)
            
#----------------------TEST / MAIN----------------------
if __name__ == "__main__":
    reachy = ReachyMini()
    jukebox(reachy, "")