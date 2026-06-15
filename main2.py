import time
import random

import pyttsx3
import speech_recognition as sr

from reachy_mini import ReachyMini
from emotions import rileva_emozione, gestisci_emozione


PAUSA_BREVE = 0.8    # pausa tra gesto e voce
PAUSA_LUNGA = 2.5    # pausa dopo una domanda diretta


engine = pyttsx3.init()
engine.setProperty('rate', 150)     # parole/minuto — NON secondi
engine.setProperty('volume', 1.0)


RECOGNIZER = sr.Recognizer()
MIC = sr.Microphone()


def parla(testo: str, pausa: float = PAUSA_BREVE) -> None:
    print(f"\n🤖  Reachy: \"{testo}\"")
    engine.say(testo)
    engine.runAndWait()
    pause(PAUSA_BREVE)


def ascolta_risposta() -> str: 
    print(f"\n👤  (in ascolto…)")
    with MIC as source:
        RECOGNIZER.adjust_for_ambient_noise(source, duration=0.5)
        try:
            audio = RECOGNIZER.listen(source, timeout=8, phrase_time_limit=10)
            testo = RECOGNIZER.recognize_google(audio, language="it-IT")
            print(f"👤  Utente: \"{testo}\"")
            return testo.lower().strip()
        except sr.UnknownValueError:
            # Audio captato ma non riconoscibile
            return ""
        except sr.WaitTimeoutError:
            # Nessun suono entro il timeout
            return ""
        except sr.RequestError:
            # Problema di rete con l'API Google
            print("    [WARN] Servizio di riconoscimento non disponibile")
            return ""


def non_capisco(reachy: ReachyMini, contesto: str = "la risposta",
                fraintendimenti: int = 1) -> str:

    match fraintendimenti:

        case 1:
            reachy.head.turn_right(6)
            time.sleep(PAUSA_BREVE)
            reachy.head.look_forward()
            parla("I miei circuiti sono un po' lenti oggi, scusi! "
                  "Può ripetere?", pausa=PAUSA_LUNGA)
            return ascolta_risposta()

        case 2:
            reachy.head.turn_right(6)
            time.sleep(PAUSA_BREVE)
            reachy.head.look_forward()
            parla(f"Scusi, oggi proprio non riesco a sentire bene. "
                  f"Potrebbe ripetere {contesto}? Voglio capire.", pausa=PAUSA_LUNGA)
            return ascolta_risposta()

        case 3:
            reachy.head.nod()
            time.sleep(PAUSA_BREVE)
            parla("Oggi proprio non riesco a funzionare bene, scusami. "
                  "Parliamo di qualcos'altro!")
            return ""   



def inizializza_robot() -> ReachyMini:
    print("⚙  Connessione a Reachy Mini (simulatore)...")
    reachy = ReachyMini(host="localhost")
    reachy.turn_on()
    print("✓  Robot attivo.\n")
    return reachy


def saluto(reachy: ReachyMini) -> None:
    # Avvicinamento graduale: pausa 4s prima di interagire
    time.sleep(4.0)

    # Gesto: wave con braccio destro
    reachy.head.look_forward()
    time.sleep(PAUSA_BREVE)
    reachy.right_arm.raise_up(30)
    time.sleep(0.4)
    reachy.right_arm.wave()
    time.sleep(0.5)
    reachy.right_arm.lower()
    time.sleep(PAUSA_BREVE)

    parla("Ciao! Sono Reachy. Come stai oggi?", pausa=PAUSA_LUNGA)


def presentazione(reachy: ReachyMini) -> None:
   

    parla("Faccio parte di questa RSA.")
    time.sleep(PAUSA_BREVE)
    parla("Il mio scopo è tenerti compagnia e aiutarti come posso.")
    time.sleep(PAUSA_BREVE)
    parla("Vuoi sapere di più su di me? Rispondi pure con sì o no.", pausa=PAUSA_LUNGA)

    fraintendimenti = 0

    while True:
        risposta = ascolta_risposta()

        if risposta == "":
            # Input non riconosciuto
            fraintendimenti += 1
            risposta = non_capisco(reachy, "la tua risposta", fraintendimenti)

        if "sì" in risposta or "si" in risposta:
            parla("Sono un robot sociale, costruito per fare compagnia.")
            time.sleep(PAUSA_BREVE)
            parla("Non sono umano, ma ci tengo davvero a stare bene con te.")
            time.sleep(PAUSA_BREVE)
            parla("Puoi parlarmi di tutto: musica, ricordi, notizie.")
            break

        elif "no" in risposta:
            parla("Va benissimo. Allora parliamo di altro!")
            break

        elif risposta == "":
            # non_capisco() ha esaurito i tentativi (ha restituito "")
            parla("Nessun problema, andiamo avanti!")
            break

        else:
            # Risposta ricevuta ma non classificabile come sì/no
            fraintendimenti += 1
            if fraintendimenti >= 3:
                parla("Non riesco a capire, mi dispiace. Andiamo avanti!")
                break
            risposta = non_capisco(reachy, "sì o no", fraintendimenti)



def scelta(reachy: ReachyMini) -> str:
    parla("Cosa vuoi fare oggi?")
    time.sleep(PAUSA_BREVE)
    parla("Vuoi ascoltare un po' di musica, sapere le ultime notizie, "
          "o preferisci che mi spenga?", pausa=PAUSA_LUNGA)

    fraintendimenti = 0

    while True:
        risposta = ascolta_risposta()

        if risposta == "":
            fraintendimenti += 1
            risposta = non_capisco(reachy, "la tua scelta", fraintendimenti)
            if risposta == "":
                # Tentativi esauriti: torna al menu
                parla("Non ho capito. Riproviamo!")
                fraintendimenti = 0
                continue

        match True:

            case _ if "musica" in risposta or "cantante" in risposta or "canzone" in risposta:
                return "musica"

            case _ if "notizie" in risposta or "meteo" in risposta or "sport" in risposta or "attualità" in risposta:
                return "notizie"

            case _ if "spegni" in risposta or "basta" in risposta or "arrivederci" in risposta:
                return "spegnimento"

            case _:
                # Risposta non classificata
                fraintendimenti += 1
                parla("Non ho capito bene. Vuoi la musica, le notizie, o vuoi che mi spenga?",
                      pausa=PAUSA_LUNGA)


def saluto_finale(reachy: ReachyMini) -> None:
    parla("È stato bello questo tempo passato insieme.")
    time.sleep(PAUSA_BREVE)
    parla("Ci rivediamo nei corridoi. Prenditi cura di te!")

    # Gesto di congedo: wave
    reachy.head.turn_left(5)
    time.sleep(PAUSA_BREVE)
    reachy.right_arm.wave()
    time.sleep(0.6)
    reachy.right_arm.lower()
    reachy.head.look_forward()


def spegnimento(reachy: ReachyMini) -> None:
    saluto_finale(reachy)
    time.sleep(PAUSA_BREVE)
    reachy.turn_off()
    print("\n✓  Robot spento.\n")


