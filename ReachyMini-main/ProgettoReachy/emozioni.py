import pyttsx3
from audio_utils import parla, pausa_vocale
VELOCITA_PARLATA = 1.4           # Secondi di pausa dopo ogni battuta. Rispettare i tempi di elaborazione di un utente anziano senza risultare incalzante
PAUSA_BREVE = 0.8                # Pausa breve tra azioni multimodali, per lasciare il tempo necessario per rispondere senza stress
PAUSA_LUNGA = 2.5   

KEYWORD_EMOZIONI = {
    "felice": [
        "felice", "contenta", "contento", "bene", "benissimo", "bellissimo",
        "meraviglioso", "che bello", "sono felice", "sto bene", "ottimo",
        "fantastico", "gioia", "sorrido", "ride", "ridere", "allegra", "allegro",
    ],
    "nostalgico": [
        "manca", "mancano", "nostalgia", "ricordo", "ricordi", "mi ricorda",
        "quando ero", "da giovane", "da bambina", "da bambino", "una volta",
        "ai miei tempi", "mi fa pensare", "ho perso", "non c'e piu", "se ne andato",
        "se ne andata", "quei tempi", "passato", "anni fa",
    ],
    "triste": [
        "triste", "tristezza", "piango", "piangere", "lacrime", "mi fa piangere",
        "sono giu", "non sto bene", "mi sento male", "male", "dolore", "soffro",
        "soffrire", "dispiaciuta", "dispiaciuto", "cuore spezzato", "sola", "solo",
        "nessuno", "abbandonata", "abbandonato",
    ],
    "arrabbiato": [
        "arrabbiata", "arrabbiato", "rabbia", "incazzata", "incazzato", "furiosa",
        "furioso", "non mi piace", "odio", "detesto", "basta", "non ne posso piu",
        "stufa", "stufo", "che schifo", "mi fa arrabbiare", "nervosa", "nervoso",
        "irritata", "irritato",
    ],
    "impaurito": [
        "paura", "ho paura", "spavento", "spaventata", "spaventato", "mi spaventa",
        "temo", "temere", "non voglio", "mi fa paura", "brutto", "pericolo",
        "ansia", "ansiosa", "ansioso", "preoccupata", "preoccupato", "mi preoccupa",
        "agitata", "agitato",
    ],
    "confuso": [
        "confusa", "confuso", "non capisco", "non ho capito", "non so",
        "non ricordo", "mi sono persa", "mi sono perso", "cosa hai detto",
        "ripeti", "puo ripetere", "strana", "strano", "non ci capisco niente",
        "non seguo", "disorientata", "disorientato",
    ],
    "disgustato": [
        "schifo", "che schifo", "disgustata", "disgustato", "fa schifo",
        "orribile", "bruttissimo", "non mi piace per niente", "stomaco",
        "nausea", "mi nausea", "ripugnante", "non lo sopporto",
    ],
}

emozioni_negative = ["triste", "arrabbiato", "impaurito", "disgustato"]
emozioni_spiacevoli = ["nostalgico", "confuso"]

### temporary fix:###############################################################################
import speech_recognition as sr

#parametri
RECOGNIZER = sr.Recognizer()
MIC = sr.Microphone()
# 1) 
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
####################################################################################        

def rileva_emozione(risposta):
    testo = risposta
    punteggi = {emozione: 0 for emozione in KEYWORD_EMOZIONI}  # inizializza tutte le emozioni a 0
    
    for emozione, parole in KEYWORD_EMOZIONI.items():
        for parola in parole:
            if parola in testo:
                punteggi[emozione] += 1
    
    # prende l'emozione col punteggio più alto
    emozione_principale = max(punteggi, key=lambda x: punteggi[x])
    
    # se tutti i punteggi sono 0 non ha rilevato nulla
    if punteggi[emozione_principale] == 0:
        return None
    
    return emozione_principale
    

def gestisci_emozione(emozione, reachy):
    
    if emozione in emozioni_negative:
        parla("Mi dipsiace sentirti dire queste parole")
        pausa_vocale(PAUSA_BREVE)
        parla("Vuoi che chiami un assistente che possa aiutarti? rispondi con 'si' o 'no'")
        conferma=ascolto_risposta()
        if conferma == "si":
            parla("Chiamo subito un assistente per te.")
            return None
        else:
            parla("Dai, allora cambiamo argomento")

    elif emozione in emozioni_spiacevoli:
        parla("Va tutto bene? rispondi con 'si' o 'no'")
        conferma=ascolto_risposta()
        if conferma == "no":
            parla("Vuoi che chiami un assistente che possa aiutarti? rispondi con 'si' o 'no'")
            conferma=ascolto_risposta()
            if conferma == "si":
                parla("Chiamo subito un assistente per te.")
                return None
            else:
                parla("Dai, allora cambiamo argomento")
        else:
            parla("Okay, volevo assicurarmi che stessi bene.")
            pausa_vocale(PAUSA_BREVE)
    else:
        parla("è bello vederti felice")
    
    
    """ match emozione:
 
        case "felice":
            reachy.head.look_forward()
            time.sleep(PAUSA_BREVE)
            reachy.right_arm.raise_up(30)
            time.sleep(0.4)
            reachy.right_arm.lower()
            reachy.head.nod()
            time.sleep(PAUSA_BREVE)
            parla("Che bello vederti così! La tua gioia mi fa felice anch'io!")
            time.sleep(PAUSA_BREVE)
            parla("Hai voglia di raccontarmi qualcosa di bello che ti è successo?",
                  pausa=PAUSA_LUNGA)
            return True
 
        case "nostalgico":
            reachy.head.turn_left(10)
            time.sleep(PAUSA_BREVE)
            parla("Capisco perfettamente… certi ricordi sono preziosi.")
            time.sleep(2.5)  
            parla("Vuoi raccontarmi qualcosa? Sono qui ad ascoltarti.",
                  pausa=PAUSA_LUNGA)
            reachy.head.look_forward()
            return True
 
        case "triste":
            reachy.head.nod()
            time.sleep(PAUSA_BREVE)
            parla("Mi dispiace tanto. Non devi sentirti sola — sono qui con te.")
            time.sleep(PAUSA_BREVE)
            reachy.head.turn_left(10)   # postura di ascolto
            time.sleep(2.5)
            parla("Se vuoi parlare, io ascolto. "
                  "Se preferisci stare in silenzio, resto qui vicino a te.",
                  pausa=PAUSA_LUNGA)
            reachy.head.look_forward()
            return True
 
        case "arrabbiato":
                reachy.head.turn_left(5)
                time.sleep(PAUSA_BREVE)
                parla("Capisco che sei arrabbiata. Hai tutto il diritto di esserlo.")
                time.sleep(PAUSA_BREVE)
                parla("Vuoi dirmi cosa è successo? A volte aiuta parlarne.",
                      pausa=PAUSA_LUNGA)
                reachy.head.look_forward()
                return True
 
        case "impaurito":
            # Gesto: allontanamento fisico del carrello + incoraggiamento
            parla("Non preoccuparti, sono qui per aiutarti.")
            time.sleep(PAUSA_BREVE)
            print("    [ROBOT] → si allontana leggermente (carrello indietro)")
            time.sleep(1.0)
            # Gesto incoraggiamento: testa a destra poi nod
            reachy.head.turn_right(8)
            time.sleep(PAUSA_BREVE)
            reachy.head.nod()
            time.sleep(0.3)
            reachy.head.look_forward()
            time.sleep(PAUSA_BREVE)
            parla("Puoi dirmi cosa ti spaventa? Voglio capire come aiutarti.",
                  pausa=PAUSA_LUNGA)
            return True
 
        case "confuso":
            reachy.head.turn_right(6)
            time.sleep(PAUSA_BREVE)
            parla("Scusami, forse mi sono spiegato male — è colpa mia, non tua!")
            reachy.head.look_forward()
            time.sleep(PAUSA_BREVE)
            parla("Ti rispiego tutto con parole più semplici. "
                  "Dimmi pure se qualcosa non è chiaro.", pausa=PAUSA_LUNGA)
            return True
 
        case "disgustato":
            reachy.head.nod()
            time.sleep(PAUSA_BREVE)
            parla("Capisco, non è di tuo gusto e va benissimo così.")
            time.sleep(PAUSA_BREVE)
            parla("Cambiamo argomento! C'è qualcosa che ti fa stare bene?",
                  pausa=PAUSA_LUNGA)
            return True

        case _:
            # Case di default
            parla("Sono qui con te, qualunque cosa tu stia sentendo.")
            return True """
