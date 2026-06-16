import os
import json
import speech_recognition as sr
from vosk import Model, KaldiRecognizer
from emozioni import rileva_emozione, gestisci_emozione

# Configurazione globale
MODEL_PATH = "model_it"
RECOGNIZER = sr.Recognizer()

# Caricamento del modello locale una sola volta all'avvio del modulo
if os.path.exists(MODEL_PATH):
    print("[MIC-SETUP] Caricamento modello Vosk locale in corso...")
    MODELLO_VOSK = Model(MODEL_PATH)
    print("[MIC-SETUP] Modello Vosk pronto.")
else:
    print(f"[MIC-SETUP] ⚠ Modello non trovato in '{MODEL_PATH}'. Fallback offline disabilitato.")
    MODELLO_VOSK = None


def ascolto_risposta() -> str:
    """Ascolta il microfono, tenta con Google e ripiega su Vosk in caso di errore."""
    with sr.Microphone() as source:
        print("[MIC] Calibrazione rumore ambientale (0.5s)...")
        RECOGNIZER.adjust_for_ambient_noise(source, duration=0.5)
        # vai partire un suono
        print("[MIC] In ascolto...")
        
        try:
            # Tempi di ascolto estesi per gli anziani
            audio = RECOGNIZER.listen(source, timeout=8, phrase_time_limit=15)
            print("[MIC] ✓ Audio catturato, avvio elaborazione...")
        except sr.WaitTimeoutError:
            print("[MIC] ✗ Timeout: nessun audio rilevato.")
            return ""

    # 1. Tentativo Cloud (Google API)
    try:
        testo = RECOGNIZER.recognize_google(audio, language="it-IT").lower()
        print(f"[STT-GOOGLE] Trascritto: '{testo}'")
        # Trovare un modo per adattare il trascritto a quello che ci serve
        return testo
    except sr.UnknownValueError:
        print("[STT-GOOGLE] ✗ Audio non compreso (UnknownValueError).")
    except sr.RequestError as e:
        print(f"[STT-GOOGLE] ✗ Errore di rete/API: {e}")

    # 2. Fallback Locale (Vosk)
    if MODELLO_VOSK:
        print("[STT-VOSK] Avvio fallback offline...")
        try:
            rec = KaldiRecognizer(MODELLO_VOSK, audio.sample_rate)
            rec.AcceptWaveform(audio.get_wav_data())
            risultato = json.loads(rec.Result())
            testo = risultato.get("text", "").lower()
            
            if testo:
                print(f"[STT-VOSK] Trascritto: '{testo}'")
                return testo
            else:
                print("[STT-VOSK] ✗ Nessun testo rilevato.")
        except Exception as ex:
            print(f"[STT-VOSK] ✗ Errore irreversibile: {ex}")

    # Se falliscono entrambi i metodi
    print("[MIC] ✗ Riconoscimento fallito totalmente.")
    return "non ho capito"


def ascolto_risposta_empatico() -> str:
    """Esegue l'ascolto e analizza l'emozione della risposta."""
    risposta = ascolto_risposta()
    
    # Processa le emozioni solo se c'è una risposta valida
    if risposta and risposta != "non ho capito":
        print(f"[EMOZIONI] Analisi per: '{risposta}'")
        emozione = rileva_emozione(risposta)
        if emozione:
            gestisci_emozione(emozione)
            
    return risposta