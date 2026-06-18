import json
import random
import pygame

from dialetto import ottieni_regione
from emozioni import rileva_emozione, gestisci_emozione, InterrompiFlussoException 
from audio_utils import parla, pausa_vocale
from reachy_mini_mock import ReachyMini
from microphone_utils import ascolto_risposta, ascolto_risposta_empatico
from puliziatesto import estrai_nome, interpreta_si_no
from utilities import spegnimento
from meteo import controlla_meteo
from news import leggi_notizie

VELOCITA_PARLATA = 1.4           # Secondi di pausa dopo ogni battuta. Rispettare i tempi di elaborazione di un utente anziano senza risultare incalzante
PAUSA_BREVE = 0.8                # Pausa breve tra azioni multimodali, per lasciare il tempo necessario per rispondere senza stress
PAUSA_LUNGA = 2.5                # Pausa lunga per lasciare rispondere

#variabili
nomi_pazienti=[]

def carica_playlist(canzoni):
    with open(canzoni, 'r', encoding='utf-8') as file: #r serve per leggere il file, encoding serve per leggere i caratteri speciali
        playlist = json.load(file)
    return playlist

lista_canzoni = carica_playlist("canzoni.json")

#----------------------FUNZIONI ESSENZIALI----------------------
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

def controlla_emozione_o_stop(risposta: str, reachy: ReachyMini) -> bool:
    """
    Controlla se nella risposta c'è un'emozione negativa/spiacevole.
    Se l'utente vuole l'assistente → spegne il robot e restituisce False.
    Altrimenti restituisce True (continua).
    """
    emozione = rileva_emozione(risposta)
    if emozione and emozione != "felice":
        continua = gestisci_emozione(emozione, reachy)
        if not continua:
            spegnimento(reachy)
            return False
    return True
    
    
def non_capisco(contesto: str = "risposta", fraintendimento: int = 0) -> str:
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
    print("DEBUG: dentro la funzione del saluto!")
    parla("Ciao, sono Reachy. Come stai?")


def presentazione(reachy: ReachyMini):
    # il robot deve presentarsi e spiegare il suo scopo
    parla("Faccio parte di questa RSA.")
    pausa_vocale(PAUSA_BREVE)

    parla("Il mio compito è quello di farti compagnia e aiutare come posso")
    pausa_vocale(PAUSA_BREVE)

    # Inizializziamo il contatore localmente a 0 per questa interazione
    fraintendimento = 0
    ha_capito = False

    # --- DOMANDA 1: Vuoi sapere di più? ---
    while fraintendimento < 3 and not ha_capito:
        parla("Vuoi sapere di più su di me? Rispondi con Sì o No")
        pausa_vocale(PAUSA_LUNGA)
        
        risposta, continua = ascolto_risposta_empatico(reachy)
        if not continua:
            raise InterrompiFlussoException() 
            
        if risposta == "RIPETI":
            continue  

       #Se rileva un'emozione negativa/spiacevole, salta il resto e rifà la domanda
        emozione_rilevata = rileva_emozione(risposta)
        if emozione_rilevata and emozione_rilevata != "felice":
            continue
        
        scelta = interpreta_si_no(risposta)
        if scelta == "si":
            parla("Mi piace stare in compagnia e adoro chiaccherare.")
            pausa_vocale(PAUSA_BREVE)
            parla("Ovviamente mi piace anche la tecnologia, ma ancora di più la musica")
            pausa_vocale(PAUSA_BREVE)
            parla("Non sono qui per sostituire le bravissime assistenti umane, ma per essere d'aiuto nelle attività quotidiane")
            pausa_vocale(PAUSA_BREVE)
            ha_capito = True
        elif scelta == "no":
            parla("Ok, allora parliamo di altro")
            ha_capito = True
        else:
            fraintendimento += 1
            if fraintendimento < 3:
        
                risposta = non_capisco("se vuoi sapere di più su di me", fraintendimento)
                
                # Controllo emozione anche dopo il recupero del "non capisco"
                if not controlla_emozione_o_stop(risposta, reachy):
                    return  
                
                # Rivalutiamo la nuova risposta ottenuta da non_capisco
                scelta = interpreta_si_no(risposta)
                if scelta == "si":
                    parla("Mi piace stare in compagnia e adoro chiaccherare.")
                    pausa_vocale(PAUSA_BREVE)
                    parla("Ovviamente mi piace anche la tecnologia, ma ancora di più la musica")
                    pausa_vocale(PAUSA_BREVE)
                    parla("Non sono qui per sostituire le bravissime assistenti umane, ma per essere d'aiuto nelle attività quotidiane")
                    pausa_vocale(PAUSA_BREVE)
                    ha_capito = True
                elif scelta == "no":
                    parla("Ok, allora parliamo di altro")
                    ha_capito = True
            else:
                parla("Oggi proprio non riesco a funzionare, scusami. Parliamo di altro")
                break

    pausa_vocale(PAUSA_BREVE)

    # --- DOMANDA 2: Come ti chiami? ---
    while True:
        parla("Lei come si chiama? Risponda con il suo nome")
        pausa_vocale(PAUSA_LUNGA)
        
        risposta, continua = ascolto_risposta_empatico(reachy)
        if not continua:
            raise InterrompiFlussoException() 
            
        if risposta == "RIPETI":
            continue   

        emozione_rilevata = rileva_emozione(risposta)
        if emozione_rilevata and emozione_rilevata != "felice":
            continue
        
        nome = estrai_nome(risposta)
        if nome and nome != "non ho capito":
            nomi_pazienti.append(nome)
            parla(f"Piacere di conoscerla {nome}")
            break
        else:
            parla("Scusami, non ho capito bene il tuo nome.")
            pausa_vocale(PAUSA_BREVE)

     # --- DOMANDA 3: Da che regione vieni? ---
    while True:
        parla("Da che regione viene?")
        pausa_vocale(PAUSA_LUNGA)
        
        luogo, continua = ascolto_risposta_empatico(reachy)
        if not continua:
            raise InterrompiFlussoException() 
                
        if luogo == "RIPETI":
            continue

        emozione_rilevata = rileva_emozione(luogo)
        if emozione_rilevata and emozione_rilevata != "felice":
            continue  

        risposta_dialetto = ottieni_regione(luogo)
        parla(f"{risposta_dialetto}")
        pausa_vocale(PAUSA_BREVE)
        parla("Ho imparato qualche frase in dialetto, anche se sicuramente non ho la giusta pronuncia")

def scelta(reachy: ReachyMini): 
    # --- DOMANDA 4: Cosa vuoi fare oggi? ---
    while True:
        parla("Cosa vuole fare oggi?")
        pausa_vocale(PAUSA_BREVE)
        parla("Vuoi ascoltare una canzone, sapere le ultime notizie o vuoi che ti dica il meteo? Rispondi con 'canzone' o 'notizie' oppure 'meteo'. Per uscire dica No!")
        
        risposta, continua = ascolto_risposta_empatico(reachy)
        if not continua:
            raise InterrompiFlussoException() 
                
        if risposta == "RIPETI":
            continue  
        
        emozione_rilevata = rileva_emozione(risposta)
        if emozione_rilevata and emozione_rilevata != "felice":
            continue
        
        if risposta == "canzone":
            canzone = random.choice(lista_canzoni)
            pygame.mixer.init()
            pygame.mixer.music.load(canzone["file_path"])
            pygame.mixer.music.play()  
            
            while pygame.mixer.music.get_busy():
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
            
        elif risposta == "meteo":
            parla("Vuole sapere se deve portare l'ombrello? Ora le dico le previsioni!")
            controlla_meteo()
            
        elif risposta == "no":
            parla("okay, va bene!")
        else: 
            parla("Non ho capito")


def saluto_finale(reachy: ReachyMini):
    parla("È stato bello questo tempo speso insieme")
    pausa_vocale(PAUSA_BREVE)
    parla ("Ci rivediamo nei corridoi")


#----------------------FLUSSO DELL'INTERAZIONE----------------------
def main(reachy: ReachyMini):
    try:
        print("DEBUG: saluto")
        saluto(reachy)
        pausa_vocale(PAUSA_BREVE)

        print("DEBUG: presentazione")
        presentazione(reachy)
        pausa_vocale(PAUSA_BREVE)

        print("DEBUG: scelta")
        scelta(reachy) # notizie/meteo/canzone 
        pausa_vocale(PAUSA_BREVE)

        print("DEBUG: saluto finale")
        saluto_finale(reachy)
        
    #ogni volta che si chiama assistente     
    except InterrompiFlussoException:
        print("\n[STOP] Rilevata richiesta assistente. Interruzione totale del flusso.")
        # Centralizziamo qui lo spegnimento di sicurezza del robot
        spegnimento(reachy)


if __name__ == "__main__":
    # 1. Crea l'istanza del robot usando la funzione che hai già preparato
    mio_robot = inizializza_robot()    
    # 2. Avvia il flusso dell'interazione passando il robot al main
    main(mio_robot)
