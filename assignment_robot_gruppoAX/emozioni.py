import pyttsx3
import speech_recognition as sr
import numpy as np
import pygame

from audio_utils import parla, pausa_vocale
#from vosk import Model, KaldiRecognizer 



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

class InterrompiFlussoException(Exception):
#eccezione personalizzata per interrompere flusso del main nel caso si chiami assistente 
    pass

####################################################################################        

def rileva_emozione(risposta):
    testo = risposta
    punteggi = {emozione: 0 for emozione in KEYWORD_EMOZIONI}  # Inizializza tutte le emozioni a 0
    
    for emozione, parole in KEYWORD_EMOZIONI.items():
        for parola in parole:
            if parola in testo:
                punteggi[emozione] += 1
    
    # Prende l'emozione col punteggio più alto
    emozione_principale = max(punteggi, key=lambda x: punteggi[x])
    
    # Se tutti i punteggi sono 0 non ha rilevato nulla
    if punteggi[emozione_principale] == 0:
        return None
    
    return emozione_principale
    

def gestisci_emozione(emozione, reachy):
    """
    Restituisce:
        - False -> l'utente vuole chiamare l'assistente (STOP interazione)
        - True  -> l'utente non vuole l'assistente (CONTINUA interazione)
    """ 
    from microphone_utils import ascolto_risposta

    if emozione in emozioni_negative:
        parla("Mi dispiace sentirti dire queste parole")
        pausa_vocale(PAUSA_BREVE)
        parla("Vuoi che chiami un assistente che possa aiutarti? Rispondi con 'chiama assistente' o 'no'")
        conferma = ascolto_risposta()
        
        if conferma in ["si", "sì", "ok", "va bene", "chiama", "chiama assistente"]:
            parla("Chiamo subito un assistente per te.")
            raise InterrompiFlussoException()  # STOP: chiama assistente
        
        else:
            parla("Dai, vedrai che andrà meglio")
            return True   # CONTINUA: non serve assistente

    elif emozione in emozioni_spiacevoli:
        parla("Va tutto bene? Rispondi con 'si' o 'no'")
        conferma = ascolto_risposta()
        
        if conferma in ["no", "non sto bene", "male"]:
            parla("Vuoi che chiami un assistente che possa aiutarti? rispondi con 'si' o 'no'")
            conferma = ascolto_risposta()
            
            if conferma in ["si", "sì", "ok", "va bene", "chiama", "chiama assistente"]:
                parla("Chiamo subito un assistente per te.")
                raise InterrompiFlussoException()  # STOP: chiama assistente
            
            else:
                parla("Dai, le cose si sistemeranno")
                return True   # CONTINUA
        
        else:
            parla("Okay, volevo assicurarmi che stessi bene.")
            pausa_vocale(PAUSA_BREVE)
            return True   # CONTINUA

    else:
        # Emozione "felice" o altre emozioni non problematiche
        parla("È bello vederti felice")
        return True   # CONTINUA
    



