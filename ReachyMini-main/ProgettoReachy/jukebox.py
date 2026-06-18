import random
import time
import speech_recognition as sr
from audio_utils import parla, pausa_vocale
import pygame 
from main import PAUSA_BREVE, PAUSA_LUNGA, inizializza_robot, lista_canzoni
from reachy_mini_mock import ReachyMini
from microphone_utils import ascolto_risposta

#dizionario frasi di incoraggiamento da estrarre quando risposta è sbagliata 
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

#funzione di inizializzazione del gioco
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
#1. presentazione e spiegazioen delle regole del gicoo
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
#2. vengono chiesti i nomi dei giocatori (uno a uno, con possibilità di correggere il nome se sbagliato )
def inizializza_giocatori(stato_gioco):
    parla("Prima di iniziare, registriamo i nomi dei giocatori.")
    pausa_vocale(PAUSA_BREVE)
    parla("Animatrice, per favore, dimmi un nome alla volta. Quando hai finito, dì 'fine'.")
    
    ultimo_nome_registrato = None

    while True:
        nome_giocatore = ascolto_risposta()
        #comando per terminare registrazione dei giocatori
        if nome_giocatore in ["fine", "terminato", "stop", "basta", "finito"]:
            parla("Grazie! Ora siamo pronti per iniziare il gioco.")
            break
        #per correggere il nome (rimuove l'ultimo detto, richiede all'animatrice il nome, registra nome corretto)
        elif nome_giocatore in ["no", "no ho sbagliato", "sbagliato", "non", "errore", "cambia"]:
            if ultimo_nome_registrato is not None:
                del stato_gioco["giocatori_punteggi"][ultimo_nome_registrato]
                parla(f"Ok, ho rimosso {ultimo_nome_registrato}. Mi ripeti il nome?")
                ultimo_nome_registrato = None
            #nel caso dicesse subito "no", "no ho sbagliato", ... prima di aver detto il nome
            else:
                parla("Non ho ancora registrato nessun nome da correggere. Dimmi il nome.")
            continue
        #se dice il nome -> registra -> feedback conferma 
        else:
            stato_gioco["giocatori_punteggi"][nome_giocatore] = 0
            ultimo_nome_registrato = nome_giocatore
            parla(f"{nome_giocatore} registrato!")

    return stato_gioco["giocatori_punteggi"]
#3. estrae la canzone dalla lista inizializzata all'inizio
def estrai_canzone(stato_gioco):
    canzoni_disponibili = []
    for canzone in stato_gioco["playlist"]: 
        if canzone not in stato_gioco["canzoni_giocate"]: #la canzone non deve essere stata già giocata 
            canzoni_disponibili.append(canzone)
    if not canzoni_disponibili: #controllo di sicurezza (numero canzoni > numero delle canzoni giocate in una sola sessione)
        return None
    canzone_corrente = random.choice(canzoni_disponibili)
    stato_gioco["canzone_corrente"] = canzone_corrente #registra e restituisce la canzone che si sta suonando 
    return canzone_corrente

#4. classifica + termine del gioco 
def fine_gioco(stato_gioco):
    stato_gioco["gioco_terminato"] = True
    #si oridnano i giocatori in maniera decrescente in base al punteggio
    classifica_finale = sorted(stato_gioco["giocatori_punteggi"].items(), key=lambda x: x[1], reverse=True)
    punteggio_max = classifica_finale[0][1]
    
    #caso di un solo vincitore (il punteggio massimo deve essere maggiore di 0, altrimenti significa che non si è giocata nessuna canzone)
    if punteggio_max != classifica_finale[1][1] and punteggio_max > 0:
        nome_vincitore, punteggio_vincitore = classifica_finale[0]
        parla("Il vincitore è ...")
        pausa_vocale(PAUSA_LUNGA)
        parla(f"{nome_vincitore} con {punteggio_vincitore} punti! Complimenti!")

    #caso in cui c'è un pareggio -> devono essere elencati tutti i nomi dei vincitori 
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
    #caso in cui nessuno gha accumulato almeno un punto 
    else:
        parla("Non ci sono vincitori siccome nessuno ha realizzato almeno un punto.")
    
    #saluto finale 
    pausa_vocale(PAUSA_BREVE)
    parla("Grazie a tutti per aver partecipato! È stato bello giocare con voi!")

#funzione per riprendere la musica dal punto da cui di è fermata con comando "interrompi"(stop_gioco) o "ferma"(ferma_musica)
def riprendi_musica(canzone_corrente, tempo_accumulato_ms):
    # Converte i millisecondi accumulati in secondi (richiesti da play)
    secondi_inizio = tempo_accumulato_ms / 1000.0
    # Ricarica e fa il play partendo dal punto esatto
    pygame.mixer.music.load(canzone_corrente["file_path"])
    pygame.mixer.music.play(start=secondi_inizio)

#----------------------COMANDI ANIMATRICE----------------------
#per far partire il gioco dopo inizializzazione dei giocatori
def start_gioco(reachy, comando):
    parla("Se siamo tutti pronti, animatrice dimmi 'pronti via'!")
    pausa_vocale(PAUSA_BREVE)
    risposta = ascolto_risposta()
    if risposta == "pronti via":
        parla("Perfetto! Iniziamo il gioco!")
    else:
        parla("Non ho capito, ripetilo per favore.")
        start_gioco(reachy, comando)

#per interrompere il gicoo nel caso in cui ci fosse un'emergenza tra gli anziani
def stop_gioco(stato_gioco, canzone_corrente, tempo_accumulato):
    pygame.mixer.music.pause() #musica viene stoppata 
    parla("Il gioco è stato momentaneamente interrotto")
    pausa_vocale(PAUSA_LUNGA)
    #possibilita di riprendere o terminare il gioco
    parla("Animatrice, vuoi riprendere il gioco? dimmi riprendi o interrompi")
    risposta = ascolto_risposta()
    #se riprende -> riparte la musica dal punto in cui si è interrotta
    if risposta == "riprendi":
        parla("Perfetto! Riprendiamo il gioco!")
        riprendi_musica(canzone_corrente, tempo_accumulato)
        return True
    #se interrompe -> gioco termina 
    elif risposta == "interrompi":
        parla("Va bene, il gioco termina qui.")
        stato_gioco["gioco_terminato"] = True
        return False
    #se non capisce -> ripetere comando 
    else:
        parla("Non ho capito, ripetilo per favore.")
        # Se non capisce, riprova
        return stop_gioco(stato_gioco, canzone_corrente, tempo_accumulato)

#per fermare la musica e dare titolo corretto 
def ferma_musica(stato_gioco, canzone_corrente, tempo_accumulato):
    pygame.mixer.music.pause() #musica si stoppa
    parla("Animatrice, per favore, chiedi al giocatore il titolo della canzone.")
    titolo_risposta = ascolto_risposta()
    
    #se il titolo è giusto -> assegna un punto al giocatore -> assegna la canzone a quelle gia suonate 
    if titolo_risposta == canzone_corrente["titolo"]:
        pygame.mixer.music.stop()
        parla("Risposta corretta! A chi assegno il punto?")
        giocatore = ascolto_risposta()
        stato_gioco["giocatori_punteggi"][giocatore] += 1
        parla(f"Perfetto! {giocatore} ha guadagnato un punto!")
        stato_gioco["canzoni_giocate"].append(canzone_corrente)
        return True
    #se titolo è sbagliato -> frase incoraggiamento -> canzone riprende 
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

    #numero delle canzoni che vogliono essere giocate (idealemnte 15, abbiamo messo 4 per i test)
    while len(stato_gioco["canzoni_giocate"]) < 4:
        canzone_corrente = estrai_canzone(stato_gioco) #estrae la canzone
       
        #controllo di sicurezza 
        if canzone_corrente is None: 
            parla("Tutte le canzoni sono state giocate. Il gioco termina qui.")
            break

        #attraverso libreria pygame la musica viene caricata (in base a file path) e suonata 
        pygame.mixer.music.load(canzone_corrente["file_path"])
        pygame.mixer.music.play()

        # variabili locali per gestire condizioni 
        indizio_dato = False
        tempo_accumulato=0  #registra millisecondi già ascoltati nelle sessioni precedenti (prima di stoppare la musica)

        while True:
            tempo_corrente_sessione = pygame.mixer.music.get_pos() #per sapere poi da dove riprendere la musica (millisecondi ascoltati nella sessione in corso)
            if tempo_corrente_sessione == -1: 
                tempo_corrente_sessione = 0 #si azzera a ogni riavvio

            tempo_totale_canzone = tempo_accumulato + tempo_corrente_sessione        
            comando = ascolto_risposta()
            
            #intercetta comando di fermare la musica per dare la risposta 
            if comando == "ferma la musica":
                tempo_accumulato=tempo_totale_canzone #registra quanto tempo si è ascoltata quella canzone 
                controllo_risposta = ferma_musica(stato_gioco, canzone_corrente, tempo_accumulato)
                #se la risposta è giusta -> esce dal ciclo e controlla se si è gia arrivati al numero massimo di canzoni da giocare
                if controllo_risposta == True:
                    break
                #se la risposta è sbagliata -> continua con il ciclo riprendendo la canzone 
                else:
                    continue
            
            #intercetta comando di fermare la musica per dare la risposta 
            if comando == "interrompi il gioco":
                tempo_accumulato=tempo_totale_canzone
                controllo_risposta = stop_gioco(stato_gioco, canzone_corrente, tempo_accumulato)
                #se gli dice di riprendere -> continua gioco
                if controllo_risposta == True:
                    continue
                #se dice di interrompere -> gioco termina
                else:
                    fine_gioco(stato_gioco)
                    return

            # per dare indizio dopo 30 secondi
            if tempo_totale_canzone > 30000 and not indizio_dato:
                tempo_accumulato=tempo_totale_canzone
                pygame.mixer.music.pause() 
                parla(f"Indizio: il cantante di questa canzone è {canzone_corrente['artista']}")
                pausa_vocale(PAUSA_BREVE)
                parla("Ora riparte la musica!")
                riprendi_musica(canzone_corrente, tempo_accumulato)
                indizio_dato = True
            
            # la canzone viene skippata dopo 60 secondi in cui nessuno ha dato risposta 
            if tempo_totale_canzone > 60000 and indizio_dato:
                pygame.mixer.music.stop()
                parla("Mannaggia, questa era difficile!")
                pausa_vocale(PAUSA_BREVE)
                parla(f"Il titolo di questa canzone è {canzone_corrente['titolo']}. Ascoltiamo un'altra canzone!")
                stato_gioco["canzoni_giocate"].append(canzone_corrente) #canzone gia suonata
                break
    
    fine_gioco(stato_gioco)
            
#----------------------TEST / MAIN----------------------
if __name__ == "__main__":
    reachy = ReachyMini()
    jukebox(reachy, "")