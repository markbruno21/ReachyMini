import time
import random
import pyttsx3
import speech_recognition as sr

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
    #gestire lingue straniere




def presentazione(reachy: ReachyMini):
    #il robot deve presentarsi e spiegare il suo scopo
    engine.say("Faccio parte di questa RSA.")
    pause(PAUSA_BREVE)
    engine.say("Il mio scopo è quello di farti compagnia e aiutare come posso")
    pause(PAUSA_BREVE)
    engine.say("Vuoi sapere di più su di me? Rispondi con 'si' o 'no'")
    pause(PAUSA_LUNGA)
    risposta = ascolto_risposta()
    while fraintendimento < 3:
    risposta = ascolto_risposta()
    if risposta == "si":
        engine.say("??")
        pause(PAUSA_BREVE)
        engine.say("??")
        pause(PAUSA_BREVE)
        engine.say("??")
        pause(PAUSA_BREVE)
        break
    elif risposta == "no":
        engine.say("Ok, allora parliamo di altro")
        break
    else:
        fraintedimento += fraintedimento+1
        non_capisco(reachy, "risposta", fraintendimento)



        
    
    #input vocale utente 

def non_capisco(reachy: ReachyMini, contesto: str = "risposta", fraintendimento: int = 0) -> str:
    
    match 
     case 1 
     fraintendimento == 1 
     pause(PAUSA_BREVE)
        #movimento robot 
        engine.say("I miei circuiti sono lenti, scusami, può ripetere?")
        return ascolto_risposta()

    case 2 
    fraintendimento == 2 
        engine.say( "Scusi, oggi non riesco a sentire bene"
        f"Potrebbe ripetere {contesto}? Voglio capire bene.")
        return ascolto_risposta()
    case 3 
    fraintendimento == 3 
        engine.say("oggi proprio non riesco a funzionare, scusami. Parliamo di altro")
        return 

    
    """
    Fase 0 di recupero XAI: il robot ammette di non aver capito
    usando un linguaggio autoironico e rassicurante, poi chiede
    di ripetere. Evita il "fallimento silenzioso" dell'interazione.
 
    Principio HRI applicato: trasparenza (XAI) aumenta la fiducia
    dell'utente anziano, che non si sente giudicato ma capisce
    che il limite è del robot, non suo.
 
    Args:
        reachy:   istanza del robot.
        contesto: stringa opzionale per personalizzare la richiesta
                  (es. "la parola" / "la sua risposta").
 
    Returns:
        La nuova risposta dell'utente, normalizzata.
    """
    # Gesto: testa inclinata (imbarazzo gentile) + look_forward di recupero
    reachy.head.turn_right(6)
    time.sleep(PAUSA_BREVE)
    parla(
        "Scusi, Carmela, i miei circuiti sono un po' lenti oggi! "
        f"Potrebbe ripetere {contesto}? Voglio capire bene.",
        pausa=PAUSA_LUNGA
    )
    reachy.head.look_forward()
    time.sleep(PAUSA_BREVE)  # gesto completato prima del prossimo turno
    return ascolta_risposta()


def scelta(reachy: ReachyMini): 
    engine.say("Cosa vuole fare oggi?")
    pause(PAUSA_BREVE)
    engine.say("Vuoi ascoltare un po' di musica o sapere le ultime notizie?")
    risposta = ascolto_risposta()
    match 
    case 1
    risposta == "Musica"
    engine.say("Qual è il suo cantante preferito?")
    cantante = ascolto_risposta()
    #fai partire la musica in base al cantante scelto 
    case 2 
    risposta == "Notizie"
    engine.say("Cosa le interessa? Il meteo, l'attualità o lo sport?")
    notizie = ascolto_risposta ()
    #fai partire le notizie in base alla scelta 
    case 3 
    #invocare funzione spegnimento


def saluto_finale(reachy: ReachyMini)
    engine.say("è stato bello questo tempo speso insieme")
    pause(PAUSA_BREVE)
    engine.say ("ci rivediamo nei corridoi")
    #movimento mano 



def saluto(reachy: ReachyMini):
    #il robot deve avvicinarsi a Carmela e fare un saluto con la mano
    reachy.arm.right.raise_up(30)
    reachy.arm.right.wave()
    reachy.arm.right.lower()
    engine.say("Ciao, sono Reachy. Come stai?")

def main(reachy: ReachyMini):
    saluto(reachy)
    pause(PAUSA_BREVE)
    presentazione(reachy)
    pause(PAUSA_BREVE)
    scelta(reachy)
    saluto_finale(reachy)



   chiacchierata_iniziale(reachy)
   notizie(reachy)
   musica(reachy)
   spegnimento(reachy)
    
def chiacchierata_iniziale(reachy: ReachyMini):

def notizie(reachy: ReachyMini):

def musica(reachy: ReachyMini):

def spegnimento(reachy: ReachyMini):