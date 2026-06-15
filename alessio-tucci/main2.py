# main2.py – Assistente vocale con input da tastiera e scelta motore TTS (locale / cloud)
import pyttsx3
import asyncio
import edge_tts
import signal
import sys
import os
from meteo import controlla_meteo
from news import leggi_notizie

# Stato globale per la gestione del ciclo di esecuzione
running = True

# ─── GESTIONE SEGNALI DI INTERRUZIONE ─────────────────────────────────────────
def signal_handler(sig, frame):
    global running
    print("\n[INFO] Uscita controllata su richiesta dell'utente (Ctrl+C)...")
    running = False
    sys.exit(0)

# Associa il segnale di interruzione da tastiera (Ctrl+C) al gestore personalizzato
signal.signal(signal.SIGINT, signal_handler)

# ─── CONFIGURAZIONE GLOBALE TTS ───────────────────────────────────────────────
USE_EDGE_TTS = False  # True = Edge TTS (Cloud), False = pyttsx3 (Locale)

def imposta_voce_ita(engine):
    """Configura il motore pyttsx3 locale impostando la prima voce italiana trovata."""
    for v in engine.getProperty('voices'):
        if 'italian' in v.name.lower():
            engine.setProperty('voice', v.id)
            return

# ─── LOGICA AUDIO EDGE TTS (CLOUD ASINCRONA) ──────────────────────────────────
async def _edge_speak_async(testo, voce="it-IT-GiuseppeNeural"):
    """Genera un file audio temporaneo tramite l'API di Edge TTS e lo riproduce con Pygame."""
    import tempfile
    import pygame
    import uuid

    unique_id = uuid.uuid4().hex
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3", prefix=f"tts_{unique_id}_") as tmp:
        tmp_path = tmp.name

    try:
        # Sintetizza il testo e salva il file MP3 sul disco
        communicate = edge_tts.Communicate(testo, voce)
        await communicate.save(tmp_path)
        
        # Gestione della riproduzione audio
        pygame.mixer.init()
        pygame.mixer.music.load(tmp_path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            await asyncio.sleep(0.05)
        pygame.mixer.quit()
    finally:
        # Rimozione forzata del file temporaneo dopo l'uso
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)

def edge_speak(testo):
    """Wrapper sincrono per avviare la coroutine asincrona di Edge TTS."""
    asyncio.run(_edge_speak_async(testo))

# ─── FUNZIONI CORE INTERAZIONE ────────────────────────────────────────────────
def parla(testo):
    """Invia il testo al motore di sintesi vocale attivo (Locale o Cloud)."""
    print(f"[REACHY] → {testo}")
    if USE_EDGE_TTS:
        edge_speak(testo)
    else:
        # Inizializzazione locale dell'istanza pyttsx3 per prevenire blocchi su Windows
        engine = pyttsx3.init()
        engine.setProperty('rate', 125)  # Velocità calibrata per anziani
        imposta_voce_ita(engine)
        engine.say(testo)
        engine.runAndWait()

def chiedi(domanda):
    """Pronuncia una domanda ed esegue il blocco di input sequenziale da tastiera."""
    parla(domanda)
    return input("[TU] ").strip().lower()

# ─── CONFIGURAZIONE UTENTE ────────────────────────────────────────────────────
def scegli_modalita():
    """Configura l'output del sistema in base alle preferenze dell'utente."""
    global USE_EDGE_TTS
    print("\n=== CONFIGURAZIONE ASSISTENTE ===")
    print("Scegli il motore di sintesi vocale (TTS):")
    print("1. Voce Locale (pyttsx3 – offline, più robotica)")
    print("2. Voce Cloud  (Edge TTS – richiede internet, molto naturale)")
    
    scelta = input("Scegli [1/2]: ").strip()
    if scelta == "2":
        USE_EDGE_TTS = True
        print("[CONFIG] Sincronizzazione con Edge TTS completata.")
        try:
            edge_speak("Sintesi vocale avanzata attiva.")
        except Exception as e:
            print(f"[ERRORE] Edge TTS fallito: {e}. Ripiego su voce locale.")
            USE_EDGE_TTS = False
    else:
        USE_EDGE_TTS = False
        print("[CONFIG] Voce locale attivata.")
        parla("Userò la voce locale.")

# ─── LOGICA DI INTERAZIONE ────────────────────────────────────────────────────
def test_interazione():
    """Ciclo principale dell'applicazione."""
    scegli_modalita()
    
    parla("Test audio avviato. Buongiorno.")
    nome = chiedi("Come ti chiami?")
    parla(f"Piacere di conoscerti, {nome}.")
    
    while running:
        scelta = chiedi("Cosa vuoi testare? Scrivi meteo, notizie, oppure esci.")
        
        if scelta == "esci":
            parla("Test terminato. Arrivederci.")
            break
        elif "meteo" in scelta:
            citta = chiedi("Di quale città vuoi sapere il meteo?")
            controlla_meteo(citta, parla, chiedi)
        elif "notizie" in scelta or "news" in scelta:
            print("[MENU] → Avvio modulo notizie")
            leggi_notizie(parla, chiedi)
        else:
            parla("Comando non riconosciuto, riprova.")

if __name__ == "__main__":
    test_interazione()