import time
import pyttsx3
import asyncio
import edge_tts
import pygame
import tempfile
import os

PAUSA_BREVE = 0.8
PAUSA_LUNGA = 2.5
VELOCITA_PYTTSX3 = 125
VOCE_EDGE = "it-IT-GiuseppeNeural"  # Voce maschile italiana neurale

# ─── SETUP FALLBACK LOCALE (PYTTSX3) ──────────────────────────────────────────
engine = pyttsx3.init()
engine.setProperty('rate', VELOCITA_PYTTSX3)

for v in engine.getProperty('voices'):
    if 'italian' in v.name.lower():
        engine.setProperty('voice', v.id)
        break

# ─── SETUP RIPRODUZIONE AUDIO ─────────────────────────────────────────────────
pygame.mixer.init()

# ─── LOGICA CLOUD (EDGE-TTS) ──────────────────────────────────────────────────
async def _genera_e_riproduci(testo: str):
    # Crea un file temporaneo sicuro per l'MP3
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
        tmp_path = tmp.name
    
    # Sintetizza con Edge TTS
    communicate = edge_tts.Communicate(testo, VOCE_EDGE)
    await communicate.save(tmp_path)
    
    # Carica e riproduci con Pygame
    pygame.mixer.music.load(tmp_path)
    pygame.mixer.music.play()
    
    # Attendi la fine della riproduzione
    while pygame.mixer.music.get_busy():
        await asyncio.sleep(0.1)
        
    # Rilascia il file audio e cancellalo
    pygame.mixer.music.unload()
    try:
        os.remove(tmp_path)
    except OSError:
        pass  # Evita crash se Windows tiene bloccato il file per qualche millisecondo in più

# ─── FUNZIONI PUBBLICHE ESPORATE (MANTIENE LA COMPATIBILITA' COL MAIN) ────────
def parla(testo: str):
    print(f"[REACHY DICE] {testo}")
    try:
        # Tenta di eseguire la sintesi vocale neurale in cloud
        asyncio.run(_genera_e_riproduci(testo))
    except Exception as e:
        # Fallback locale in caso di disconnessione o timeout
        print(f"[TTS FALLBACK] Connessione a Edge fallita ({e}). Passo alla voce locale.")
        engine.say(testo)
        engine.runAndWait()

def pausa_vocale(secondi: float):
    time.sleep(secondi)