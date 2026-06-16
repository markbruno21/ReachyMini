import json
import random
import pygame

from dialetto import ottieni_regione
from emozioni import rileva_emozione, gestisci_emozione
from audio_utils import parla, pausa_vocale
from reachy_mini_mock import ReachyMini
from microphone_utils import ascolto_risposta, ascolto_risposta_empatico

VELOCITA_PARLATA = 1.4           # Secondi di pausa dopo ogni battuta. Rispettare i tempi di elaborazione di un utente anziano senza risultare incalzante
PAUSA_BREVE = 0.8                # Pausa breve tra azioni multimodali, per lasciare il tempo necessario per rispondere senza stress
PAUSA_LUNGA = 2.5                # Pausa lunga per lasciare rispondere

from meteo import controlla_meteo
##TODO  1) modify the function for reading news
from news import leggi_notizie


#variabili
fraintendimento = 0
nomi_pazienti=[]

def carica_playlist(canzoni):
    with open(canzoni, 'r', encoding='utf-8') as file: #r serve per leggere il file, encoding serve per leggere i caratteri speciali
        playlist = json.load(file)
    return playlist
# lista canzoni
lista_canzoni = carica_playlist("canzoni.json")

#----------------------FUNZIONI ESSENZIALI----------------------
# temp fix: importata la classe
def inizializza_robot() -> ReachyMini:
    """
    Stabilisce la connessione con il simulatore di Reachy Mini.
    Restituisce l'istanza del robot pronta all'uso.
    """
    print("⚙  Connessione a Reachy Mini (simulatore)...")
    reachy = ReachyMini(host="localhost")
    reachy.turn_on()
    print("✓  Robot attivo.\n")
    return reachy


    
    
def non_capisco(reachy: ReachyMini, contesto: str = "risposta", fraintendimento: int = 0) -> str:
    print("DEBUG: funzione non capisco, counter: {fraintendimento}")
    if fraintendimento==1:
        pausa_vocale(PAUSA_BREVE)
        #movimento robot 
        parla("I miei circuiti sono lenti, scusami, può ripetere?")
        return ascolto_risposta()
    elif fraintendimento == 2:
        parla( "Scusi, oggi non riesco a sentire bene"
        f"Potrebbe ripetere {contesto}? Voglio capire bene.")
        return ascolto_risposta()
    elif fraintendimento == 3:
        parla("oggi proprio non riesco a funzionare, scusami. Parliamo di altro")
        return 
    

#----------------------FUNZIONI PER L'INTERAZIONE----------------------
def saluto(reachy: ReachyMini):
    #il robot deve avvicinarsi a Carmela e fare un saluto con la mano
    #reachy.arm.right.raise_up(30)
    #reachy.arm.right.wave()
    #reachy.arm.right.lower()
    print("DEBUG: dentro la funzion del saluto!")
    parla("Ciao, sono Reachy. Come stai?")


def presentazione(reachy: ReachyMini):
    #il robot deve presentarsi e spiegare il suo scopo
    # usare keyword global
    global fraintendimento
    parla("Faccio parte di questa RSA.")
    pausa_vocale(PAUSA_BREVE)

    parla("Il mio compito è quello di farti compagnia e aiutare come posso")
    pausa_vocale(PAUSA_BREVE)

    parla("Vuoi sapere di più su di me? Rispondi con Sì o No'")
    pausa_vocale(PAUSA_LUNGA)

    risposta = ascolto_risposta()
    
	## 1) funzione che capisce se si o no dalla stringa trascritta...
    
    # risposta = classifica_risposte(risposta)
    while fraintendimento < 3:
        if risposta == "sì":
            parla("Mi piace stare in compagnia e adoro chiaccherare.")
            pausa_vocale(PAUSA_BREVE)
            parla("Ovviamente mi piace anche la tecnologia, ma ancora di più la musica")
            pausa_vocale(PAUSA_BREVE)
            parla("Non sono qui per sostituire le bravissime assistenti umane, ma per essere d'aiuto nelle attività quotidiane")
            pausa_vocale(PAUSA_BREVE)
            break
        elif risposta == "no":
            parla("Ok, allora parliamo di altro")
        else:
            fraintendimento = fraintendimento+1
            non_capisco(reachy, "risposta", fraintendimento)

    pausa_vocale(PAUSA_BREVE)
    parla("Lei come si chiama? Risponda con il suo nome")
    pausa_vocale(PAUSA_LUNGA)
    
	## 2) funzione che estrare il nome proprio di persona dalla stringa trascritta 
    
    nome = ascolto_risposta_empatico()
    nomi_pazienti.append(nome)

    parla(f"Piacere di conoscerla {nome}")
    pausa_vocale(PAUSA_BREVE)

    parla("Da che regione viene?")
    pausa_vocale(PAUSA_LUNGA)
    
	## 3) funzione che estrae la regione italiana dalla stringa
    
    luogo = ascolto_risposta_empatico()
    risposta_dialetto=ottieni_regione(luogo)
    parla(f"{risposta_dialetto}")
    pausa_vocale(PAUSA_BREVE)
    parla("Ho imparato qualche frase in dialetto, anche se sicuramente non ho la giusta pronuncia")



def scelta(reachy: ReachyMini): 
    parla("Cosa vuole fare oggi?")
    pausa_vocale(PAUSA_BREVE)
    parla("Vuoi ascoltare una canzone, sapere le ultime notizie o vuoi che ti dica il meteo? Rispondi con 'canzone' o 'notizie' oppure 'meteo'. Per uscire dica No!")
    risposta = ascolto_risposta_empatico()
    if risposta == "canzone":
        canzone=random.choice(lista_canzoni)
        pygame.mixer.init()
        pygame.mixer.music.load(canzone["file_path"])
        pygame.mixer.music.play()  
        # controllo per capire se funziona in modo asyncrono...
        while pygame.mixer.music.get_busy():  # finché la musica sta suonando
            comando = ascolto_risposta()
            if comando in ["stop", "basta", "fermo", "ferma", "fermati", "smetti"]:
                pygame.mixer.music.stop()
                parla("Ok, ho fermato la canzone.")
                break

        pausa_vocale(PAUSA_BREVE)
        parla("Spero le sia piaciuta.")

    elif risposta == "notizie":
        parla("Perfetto! Ora le dico un po' di notizie interessanti!")
        leggi_notizie() 
		## TODO 1 IMPLENETARE chiamata al news.py, leggi notizie deve iniziare l'inteazione da li
    elif risposta == "meteo":
        parla("Vuole sapere se deve portare l'ombrello? Ora le dico le previsioni!")
        controlla_meteo()
        ## TODO: 2 IMPLEMENTARE chiamata al meteo.py, controlla meteo deve iniziare linterazione da li
    elif risposta == "no":
        parla("okay, va bene!")
    else: 
        parla("Non ho capito")
    return 

def saluto_finale(reachy: ReachyMini):
    parla("È stato bello questo tempo speso insieme")
    pausa_vocale(PAUSA_BREVE)
    parla ("ci rivediamo nei corridoi")
    reachy.arm.right.raise_up(30)
    reachy.arm.right.wave()
    reachy.arm.right.lower()
    #movimento mano


#----------------------FLUSSO DELL'INTERAZIONE----------------------
def main(reachy: ReachyMini):
    print("DEBUG: saluto")
    saluto(reachy)
    pausa_vocale(PAUSA_BREVE)
    print("DEBUG: presentazione")
    presentazione(reachy)
    pausa_vocale(PAUSA_BREVE)
    print("DEBUG: scelta")
    scelta(reachy) #notizie o musica 
    pausa_vocale(PAUSA_BREVE)
    print("DEBUG: saluto finale")
    saluto_finale(reachy)


if __name__ == "__main__":
    # 1. Crea l'istanza del robot usando la funzione che hai già preparato
    mio_robot = inizializza_robot()    
    # 2. Avvia il flusso dell'interazione passando il robot al main
    main(mio_robot)
