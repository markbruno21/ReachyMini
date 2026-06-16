import time
import random
import pyttsx3
import pygame
import speech_recognition as sr
from dialetto import ottieni_regione, DIALETTI
from jukebox import lista_canzoni
from emozioni import rileva_emozione


VELOCITA_PARLATA = 1.4           # Secondi di pausa dopo ogni battuta. Rispettare i tempi di elaborazione di un utente anziano senza risultare incalzante
PAUSA_BREVE = 0.8                # Pausa breve tra azioni multimodali, per lasciare il tempo necessario per rispondere senza stress
PAUSA_LUNGA = 2.5                # Pausa lunga per lasciare rispondere

engine = pyttsx3.init()
engine.setProperty('rate', VELOCITA_PARLATA) 
engine.setProperty('pause', PAUSA_BREVE)
engine.setProperty('pauseLong', PAUSA_LUNGA)

#parametri
RECOGNIZER = sr.Recognizer()
MIC = sr.Microphone()

#variabili
fraintendimento = 0
nomi_pazienti=[]

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

def ascolto_risposta() -> str:
    with MIC as source:
        RECOGNIZER.adjust_for_ambient_noise(source)
        risposta_utente = RECOGNIZER.listen(source)
        try:
            return RECOGNIZER.recognize_google(risposta_utente, language="it-IT")
        except sr.UnknownValueError:
            return "Non ho capito"
        except sr.RequestError:
            return "Errore nel sistema"
        
def ascolto_risposta_empatico():
    risposta = ascolto_risposta()
    rileva_emozione(risposta)
    return risposta
    
    
def non_capisco(reachy: ReachyMini, contesto: str = "risposta", fraintendimento: int = 0) -> str:
    match fraintendimento:
        case 1:
            fraintendimento == 1 
            engine.pause(PAUSA_BREVE)
            #movimento robot 
            engine.say("I miei circuiti sono lenti, scusami, può ripetere?")
            return ascolto_risposta()
        case 2:
            fraintendimento == 2 
            engine.say( "Scusi, oggi non riesco a sentire bene"
            f"Potrebbe ripetere {contesto}? Voglio capire bene.")
            return ascolto_risposta()
        case 3:
            fraintendimento == 3 
            engine.say("oggi proprio non riesco a funzionare, scusami. Parliamo di altro")
            return 

#----------------------FUNZIONI PER L'INTERAZIONE----------------------
def saluto(reachy: ReachyMini):
    #il robot deve avvicinarsi a Carmela e fare un saluto con la mano
    reachy.arm.right.raise_up(30)
    reachy.arm.right.wave()
    reachy.arm.right.lower()
    engine.say("Ciao, sono Reachy. Come stai?")


def presentazione(reachy: ReachyMini):
    #il robot deve presentarsi e spiegare il suo scopo
    engine.say("Faccio parte di questa RSA.")
    engine.pause(PAUSA_BREVE)

    engine.say("Il mio compito è quello di farti compagnia e aiutare come posso")
    engine.pause(PAUSA_BREVE)

    engine.say("Vuoi sapere di più su di me? Rispondi con 'si' o 'no'")
    engine.pause(PAUSA_LUNGA)

    risposta = ascolto_risposta()
    while fraintendimento < 3:
        risposta = ascolto_risposta()
        if risposta == "si":
            engine.say("Mi piace stare in compagnia e adoro chiaccherare.")
            engine.pause(PAUSA_BREVE)
            engine.say("Ovviamente mi piace anche la tecnologia, ma ancora di più la musica")
            engine.pause(PAUSA_BREVE)
            engine.say("Non sono qui per sostituire le bravissime assistenti umane, ma per essere d'aiuto nelle attività quotidiane")
            engine.pause(PAUSA_BREVE)
        elif risposta == "no":
            engine.say("Ok, allora parliamo di altro")
        else:
            fraintedimento += fraintedimento+1
            non_capisco(reachy, "risposta", fraintendimento)

    engine.pause(PAUSA_BREVE)
    engine.say("Lei come si chiama? Risponda con il suo nome")
    engine.pause(PAUSA_LUNGA)
    nome = ascolto_risposta()
    nomi_pazienti.append(nome)

    engine.say(f"Piacere di conoscerla {nome}")
    engine.pause(PAUSA_BREVE)

    engine.say("Da che regione viene?")
    engine.pause(PAUSA_LUNGA)
    luogo = ascolto_risposta()
    risposta_dialetto=ottieni_regione(luogo)
    engine.say(f"{risposta_dialetto}")
    engine.pause(PAUSA_BREVE)
    engine.say("Ho imparato qualche frase in dialetto, anche se sicuramnete non ho la giusta pronuncia")



def scelta(reachy: ReachyMini): 
    engine.say("Cosa vuole fare oggi?")
    engine.pause(PAUSA_BREVE)
    engine.say("Vuoi ascoltare una canzone o sapere le ultime notizie? Rispondi con 'canzone' o 'notizie' oppure 'no'")
    risposta = ascolto_risposta()
    match scelta:
        case 1:
            risposta == "canzone"
            canzone=random.choice(lista_canzoni)
            pygame.mixer.init()
            pygame.mixer.music.load(canzone["file_path"])
            pygame.mixer.music.play()
            engine.pause(PAUSA_BREVE)
            engine.say("Spero le sia piaciuta.")

        case 2:
            risposta == "Notizie"
            engine.say("Cosa le interessa? Il meteo, l'attualità o lo sport?")
            notizie = ascolto_risposta ()
            #fai partire le notizie in base alla scelta 
        case 3:
            risposta == "no"
            #invocare funzione spegnimento
    return 

def saluto_finale(reachy: ReachyMini)
    engine.say("È stato bello questo tempo speso insieme")
    engine.pause(PAUSA_BREVE)
    engine.say ("ci rivediamo nei corridoi")
    reachy.arm.right.raise_up(30)
    reachy.arm.right.wave()
    reachy.arm.right.lower()
    #movimento mano


#----------------------FLUSSO DELL'INTERAZIONE----------------------
def main(reachy: ReachyMini):
    saluto(reachy)
    engine.pause(PAUSA_BREVE)

    presentazione(reachy)
    engine.pause(PAUSA_BREVE)

    scelta(reachy) #notizie o musica 
    engine.pause(PAUSA_BREVE)


    saluto_finale(reachy)


    



def notizie(reachy: ReachyMini):

def musica(reachy: ReachyMini):

def spegnimento(reachy: ReachyMini):