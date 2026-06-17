import random
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
    # ascolto_risposta()

    

    #stato gioco
    stato_gioco = {
    "giocatori_punteggi" : {},
    "playlist" : lista_canzoni,
    "canzoni_giocate" : [],
    "canzone_corrente" : None,
    "gioco_terminato" : False,
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
    parla("Altrimenti se è sbagliata non vi preoccupate, la musica ricomincierà e potrete riprovare!")
    pausa_vocale(PAUSA_BREVE)
    parla("Dopo 15 canzoni, il gioco terminerà e vedremo chi è il vincitore!")
    pausa_vocale(PAUSA_BREVE)

def inizializza_giocatori(stato_gioco):
    parla("Prima di iniziare, registriamo i nomi dei giocatori.")
    pausa_vocale(PAUSA_BREVE)
    parla("Animatrice, per favore, dimmi un nome alla volta. Quando hai finito, dì 'fine'.")
   
    while True:
        nome_giocatore = ascolto_risposta()
        if nome_giocatore in ["fine", "terminato", "stop", "basta", "finito"]:
            parla("Grazie! Ora siamo pronti per iniziare il gioco.")
            break
        elif nome_giocatore in ["no","no ho sbagliato", "sbagliato", "non", "errore", "cambia"]:
            if ultimo_nome_registrato is not None:
                del stato_gioco["giocatori_punteggi"][ultimo_nome_registrato]
                parla(f"Ok, ho rimosso {ultimo_nome_registrato}. Mi ripeti il nome?")
                ultimo_nome_registrato = None
            else:
                parla("Non ho ancora registrato nessun nome da correggere. Dimmi il nome.")
            continue
        else:
            stato_gioco["giocatori_punteggi"][nome_giocatore] = 0 #inizializza punteggio a 0 per ogni nome
            ultimo_nome_registrato = nome_giocatore
            parla(f"{nome_giocatore} registrato!")

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

#classifica_finale[0]      → ("Mario":5)   intera tupla
#classifica_finale[0][0]   → "Mario"         nome
#classifica_finale[0][1]   → 5               punteggio
def fine_gioco(stato_gioco):
    stato_gioco["gioco_terminato"] = True
    classifica_finale = sorted(stato_gioco["giocatori_punteggi"].items(),key=lambda x: x[1], reverse=True)
    punteggio_max=  0 
    punteggio_max= classifica_finale[0][1] #per prendere solo il punteggio 
    #ciclo per vedere se ci sono pareggi 
    if punteggio_max != classifica_finale[1][1] and punteggio_max>0:
        nome_vincitore, punteggio_vincitore = classifica_finale[0]
        parla("Il vincitore è ...")
        pausa_vocale(PAUSA_LUNGA)
        parla(f"{nome_vincitore} con {punteggio_vincitore} punti! Complimenti!")

    elif punteggio_max == classifica_finale[1][1] and punteggio_max>0:
        vincitori=[]
        i=0
        while i<len(classifica_finale) and punteggio_max==classifica_finale[i][1]:
            vincitori.append(classifica_finale[i][0])
            i+=1
        parla("Aspettate, abbiamo un pareggio!")
        pausa_vocale(PAUSA_BREVE)
        parla("I vincitori sono...")
        pausa_vocale(PAUSA_LUNGA)
        parla("I vincitori sono:")
        for nome in vincitori:
            pausa_vocale(PAUSA_BREVE)
            parla(f"{nome} con {punteggio_max} punti!")
    else : parla("Non ci sono vincitori siccome nessuno ha realizzato almeno un punto.")
    #saluti finali        
    pausa_vocale(PAUSA_BREVE)
    parla("Grazie a tutti per aver partecipato! È stato bello giocare con voi!")


#----------------------COMANDI ANIMATRICE----------------------
#stop al gioco in qualsiasi momento nel caso di emergenza
def start_gioco(reachy, comando):
    #"inizia il gioco" 
    parla("Se siamo tutti pronti, animatrice dimmi 'pronti via'!")
    pausa_vocale(PAUSA_BREVE)
    risposta = ascolto_risposta()
    if risposta == " pronti via":
        parla("Perfetto! Iniziamo il gioco!")              #condizione per gestire il no mglio
        #inizia il gioco
        return
    else:
        parla("Non ho capito, ripetilo per favore.")
        start_gioco(reachy, comando)

def stop_gioco(stato_gioco):
    #"interrompi il gioco" in caso di emergenzaa 
    pygame.mixer.music.pause()
    parla("Il gioco è stato momentaneamente interrotto")
    pausa_vocale(PAUSA_LUNGA)
    parla("Animatrice, vuoi riprendere il gioco? dimmi si o no")
    risposta = ascolto_risposta()
    if risposta == "si":
        parla("Perfetto! Riprendiamo il gioco!")
        pygame.mixer.music.unpause()
        return True
    elif risposta == "no":
        parla("Va bene, il gioco termina qui. Grazie a tutti per aver partecipato! È stato bello giocare con voi!")
        stato_gioco["gioco_terminato"] = True
        return False
    else:
        parla("Non ho capito, ripetilo per favore.")
    
     
#ferma la musica (per far dire titolo della canzone)
def ferma_musica(stato_gioco, canzone_corrente):
    pygame.mixer.music.pause()
    parla("Animatrice, per favore, chiedi al giocatore il titolo della canzone.")
    titolo_risposta = ascolto_risposta()
    #se risposta giusta -> assegna punto 
    if titolo_risposta == canzone_corrente["titolo"]:
        pygame.mixer.music.stop()
        parla("Risposta corretta! A chi assegno il punto?")
        giocatore=ascolto_risposta()
        stato_gioco["giocatori_punteggi"][giocatore] += 1
        parla(f"Perfetto! {giocatore} ha guadagnato un punto!")
        return True
    #se risposta sbagliata -> nessun punto -> riprende la stessa canzone
    elif titolo_risposta != canzone_corrente["titolo"]:
        parla(random.choice(frasi_incoraggiamento))
        pausa_vocale(PAUSA_BREVE)
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
            parla("Tutte le canzoni sono state giocate. Il gioco termina qui.")
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
                    fine_gioco(stato_gioco)
                    break

            #dare indizio se trascorso piu di 1 minuto senza risposte
            tempo_trascorso = pygame.mixer.music.get_pos()
            if tempo_trascorso > 60000: #1 minuto
                pygame.mixer.music.pause() #pausa la musica per dare l'indizio
                parla(f"Indizio: il cantante di questa canzone è {canzone_corrente['artista']}")
                pausa_vocale(PAUSA_BREVE)
                parla("Ora riparte la musica!")
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
                    parla("Mannaggia, questa era difficile!")
                    pausa_vocale(PAUSA_BREVE)
                    parla(f"Il titolo di questa canzone è {canzone_corrente['titolo']}. Ascoltiamo un'altra canzone!")
                    break #riprende da riga 182
    
    fine_gioco(stato_gioco)
            
#----------------------TEST / MAIN----------------------
#----------------------TEST / MAIN----------------------
#----------------------TEST / MAIN----------------------
if __name__ == "__main__":
    reachy = ReachyMini()
    jukebox(reachy, "")