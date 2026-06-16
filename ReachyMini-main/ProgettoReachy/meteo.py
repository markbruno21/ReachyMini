import requests
import json

## importato da alessio
# --- NUOVI IMPORT ---
from audio_utils import parla, pausa_vocale
from microphone_utils import ascolto_risposta

print("[METEO] meteo.py importato correttamente")

# ─── CARICAMENTO PROVINCE ─────────────────────────────────────────────────────
# Carica un file JSON locale contenente le province italiane per filtrare le ricerche
# e ridurre i falsi positivi durante l'interazione vocale.
with open('province.json', 'r', encoding='utf-8') as f:
    province_dict = json.load(f)
# Crea un set di nomi in minuscolo per una ricerca rapida (O(1)) ed evitare errori di case-sensitivity
NOMI_PROVINCE = {nome.lower() for nome in province_dict.values()} 

# ─── MAPPA CODICI METEO ───────────────────────────────────────────────────────
def descrivi_tempo(codice):
    """
    Traduce i codici numerici standard WMO restituiti dall'API di Open-Meteo
    in descrizioni testuali in italiano, leggibili dal motore TTS.
    """
    tabella = {
        0: "cielo sereno",           1: "prevalentemente sereno",
        2: "parzialmente nuvoloso",  3: "nuvoloso",
        45: "nebbia",                48: "nebbia con brina",
        51: "pioggerellina",         61: "pioggia leggera",
        63: "pioggia moderata",      65: "pioggia intensa",
        71: "neve leggera",          73: "neve moderata",
        75: "neve intensa",          80: "acquazzoni",
        95: "temporale",
    }
    # Restituisce "tempo variabile" se il codice non è mappato nella tabella
    risultato = tabella.get(codice, "tempo variabile")
    print(f"[METEO] Codice WMO {codice} → '{risultato}'")
    return risultato

# ─── GEOCODING ────────────────────────────────────────────────────────────────
def cerca_citta(nome):
    """
    Interroga l'API di geocoding di Open-Meteo per convertire il nome della città
    in coordinate geografiche (latitudine e longitudine).
    """
    url = (f"https://geocoding-api.open-meteo.com/v1/search"
           f"?name={nome}&count=5&language=it&format=json")
    print(f"[GEO] Cerco '{nome}' → {url}")
    
    # Gestione robusta delle eccezioni di rete per evitare crash dello script
    try:
        risposta = requests.get(url, timeout=5)
        print(f"[GEO] HTTP {risposta.status_code}")
        risultati = risposta.json().get("results", [])
        print(f"[GEO] Trovati {len(risultati)} risultati")
        
        # Log dei risultati trovati a scopo di debug
        for r in risultati:
            prov = r.get("admin2", "—")
            reg  = r.get("admin1", "—")
            print(f"[GEO]   • {r['name']} | provincia: {prov} | regione: {reg} "
                  f"| lat: {r['latitude']} lon: {r['longitude']}")
        return risultati
        
    except requests.exceptions.Timeout:
        print("[GEO] ✗ Timeout — server non risponde")
        return []
    except requests.exceptions.ConnectionError:
        print("[GEO] ✗ Nessuna connessione internet")
        return []
    except Exception as e:
        print(f"[GEO] ✗ Errore inatteso: {e}")
        return []

# ─── DISAMBIGUAZIONE CITTÀ ────────────────────────────────────────────────────
def scegli_citta(risultati, citta_richiesta, parla, chiedi):
    """
    Risolve casi di omonimia tra città filtrando per nazione e chiedendo 
    eventuali chiarimenti all'utente. Ottimizzata per un target anziano.
    """
    # Isola solo i risultati situati sul suolo italiano
    risultati_ita = [r for r in risultati if r.get("country_code") == "IT"]
    
    if not risultati_ita:
        print("[SCELTA] Nessun risultato in Italia, prendo il primo assoluto")
        return risultati[0]

    # Bypass disambiguazione se c'è un solo risultato o se la città richiesta
    # è formalmente una provincia nota presente nel file JSON.
    if len(risultati_ita) == 1 or citta_richiesta.lower() in NOMI_PROVINCE:
        scelta = risultati_ita[0]['name']
        print(f"[SCELTA] Trovata provincia o risultato unico: {scelta}")
        return risultati_ita[0]

    # Se ci sono più città omonime, chiede di specificare la provincia
    print(f"[SCELTA] Trovati {len(risultati_ita)} omonimi per {citta_richiesta}")
    parla(f"Ho trovato più posti che si chiamano {citta_richiesta}.")
    
    # Due tentativi per far rispondere correttamente l'utente
    for tentativo in range(1, 3):
        parla("In quale provincia si trova?")
        risposta_provincia = ascolto_risposta()
        print(f"[SCELTA] L'utente ha risposto: '{risposta_provincia}'")
        
        # Ignora risposte vuote e riprova
        if not risposta_provincia:
            continue

        # Cerca la stringa della risposta all'interno del campo provincia ('admin2') dell'API
        for r in risultati_ita:
            provincia_api = r.get("admin2", "").lower()
            if risposta_provincia in provincia_api or provincia_api in risposta_provincia:
                print(f"[SCELTA] ✓ Match trovato: {r['name']} ({provincia_api})")
                return r
                
        parla("Non ho trovato corrispondenze con questa provincia. Riproviamo.")

    # Fallback in caso di mancata comprensione: sceglie il risultato più popoloso/rilevante (il primo)
    print("[SCELTA] Tentativi falliti, seleziono il primo risultato italiano")
    parla("Prendo il risultato più probabile.")
    return risultati_ita[0]

def controlla_meteo():
    print(f"\n[METEO] ════ Avvio modulo meteo ════")
    # 0. Acquisizione della città
    parla("Di quale città vuole sapere il meteo?")
    citta = ascolto_risposta()
    
	#if non citta or citta == "non ho capito":
    #    parla("Scusi, non ho sentito bene la città. Annulliamo la ricerca per ora.")
    #    return

    # 1. Geocoding
    print(f"[METEO] Step 1: geocoding per '{citta}'...")
    risultati = cerca_citta(citta)
    if not risultati:
        print("[METEO] ✗ Nessuna città trovata — esco")
        parla(f"Non riesco a trovare nessun posto che si chiami {citta}.")
        return

    # 2. Scelta città
    print("[METEO] Step 2: scelgo la città...")
    dati_citta = scegli_citta(risultati, citta)
    lat       = dati_citta["latitude"]
    lon       = dati_citta["longitude"]
    nome      = dati_citta["name"]
    provincia = dati_citta.get("admin2", "")
    
    # Costruisce il nome completo del luogo evitando ridondanze (es. "Roma, Roma")
    luogo     = f"{nome}, {provincia}" if (provincia and provincia != nome) else nome
    print(f"[METEO] Città scelta: {luogo} (lat={lat}, lon={lon})")

    # Step 3: Richiesta all'API di Open-Meteo usando le coordinate esatte
    # I parametri passati (hourly, daily) estraggono metriche orarie e giornaliere specifiche
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        f"&current_weather=true"
        f"&hourly=apparent_temperature,relative_humidity_2m,uv_index,visibility"
        f"&daily=temperature_2m_max,temperature_2m_min,"
        f"precipitation_probability_max,sunrise,sunset,windgusts_10m_max"
        f"&timezone=Europe%2FRome&forecast_days=1"
    )
    print(f"[METEO] Step 3: chiamata API meteo → {url}")
    
    # Gestione delle eccezioni di rete per la chiamata meteo
    try:
        risposta = requests.get(url, timeout=5)
        print(f"[METEO] HTTP {risposta.status_code}")
    except requests.exceptions.Timeout:
        print("[METEO] ✗ Timeout API meteo")
        parla("Non riesco a connettermi al servizio meteo. Riprova tra un momento.")
        return
    except requests.exceptions.ConnectionError:
        print("[METEO] ✗ Nessuna connessione internet")
        parla("Non c'è connessione. Riprova quando sei connesso.")
        return

    # Verifica che la chiamata sia andata a buon fine
    if risposta.status_code != 200:
        print(f"[METEO] ✗ Status code non OK: {risposta.status_code}")
        parla("Qualcosa è andato storto. Riprova tra un momento.")
        return

    # Step 4: Estrazione dei dati meteorologici dal payload JSON
    print("[METEO] Step 4: estraggo i dati...")
    dati   = risposta.json()
    att    = dati["current_weather"]
    daily  = dati["daily"]
    hourly = dati["hourly"]

    # Mapping delle variabili
    temp         = att["temperature"]
    vento        = att["windspeed"]
    codice       = att["weathercode"]
    condiz       = descrivi_tempo(codice)
    t_max        = daily["temperature_2m_max"][0]
    t_min        = daily["temperature_2m_min"][0]
    prob_pioggia = daily["precipitation_probability_max"][0]
    alba         = daily["sunrise"][0][11:16] # Taglio stringa per avere solo HH:MM
    tramonto     = daily["sunset"][0][11:16]  # Taglio stringa per avere solo HH:MM
    raffiche     = daily["windgusts_10m_max"][0]
    percepita    = hourly["apparent_temperature"][0]
    umidita      = hourly["relative_humidity_2m"][0]
    uv           = hourly["uv_index"][0]
    visibilita   = hourly["visibility"][0]

    # Log interno dei parametri
    print(f"[METEO] Dati estratti:")
    print(f"[METEO]   temp={temp}°C | percepita={percepita}°C | condizioni={condiz}")
    print(f"[METEO]   min={t_min}°C | max={t_max}°C | pioggia={prob_pioggia}%")
    print(f"[METEO]   vento={vento}km/h | raffiche={raffiche}km/h")
    print(f"[METEO]   umidita={umidita}% | UV={uv} | visibilita={visibilita}m")
    print(f"[METEO]   alba={alba} | tramonto={tramonto}")

    # Step 5: Generazione dinamica della risposta vocale (Text-To-Speech)
    print("[METEO] Step 5: racconto vocale...")
    parla(f"Sentiamo un po' cosa dice il cielo su {luogo}.")
    parla(f"Adesso c'è {condiz}, con {temp} gradi. "
          f"Ma si percepiscono {percepita:.0f} gradi.")
    parla(f"Oggi la minima sarà di {t_min} gradi e la massima di {t_max}.")
    parla(f"Il sole sorge alle {alba} e tramonta alle {tramonto}.")

    # Condizionali basati su soglie fisiche mirate agli anziani
    # Temperature estreme
    if percepita < 5:
        parla("Freddo pungente. Cappotto pesante, sciarpa e guanti, non si discute.")
    elif percepita < 12:
        parla("Fa freschetto. Copri bene la gola prima di uscire.")
    elif t_max > 35:
        parla("Caldo pericoloso. Meglio restare in casa nelle ore centrali "
              "e bere molta acqua anche se non hai sete.")
    elif t_max > 30:
        parla("Caldo afoso nel pomeriggio. Esci la mattina presto e stai all'ombra.")

    # Pioggia
    if prob_pioggia >= 60:
        parla(f"Pioggia molto probabile, {prob_pioggia} percento. Ombrello obbligatorio.")
    elif prob_pioggia >= 30:
        parla(f"Qualche goccia possibile, {prob_pioggia} percento. Tienilo in borsa.")

    # Vento forte (rischio cadute e dolori articolari)
    if raffiche > 60:
        parla(f"Raffiche di vento forti, fino a {raffiche:.0f} chilometri all'ora. "
              f"Attento, può farti perdere l'equilibrio.")
    elif vento > 25:
        parla(f"Venticello sostenuto a {vento:.0f} chilometri all'ora. "
              f"Con questo vento i dolori alle ossa si fanno sentire di più.")

    # Umidità alta (rischio respiratorio)
    if umidita > 80:
        parla(f"Aria molto umida, {umidita} percento. "
              f"Chi ha problemi ai polmoni può sentirsi peggio.")

    # Raggi UV
    if uv >= 6:
        parla(f"Raggi ultravioletti alti, indice {uv:.0f}. "
              f"Cappello, maniche lunghe e occhiali da sole se esci di giorno.")
    elif uv >= 3:
        parla(f"Raggi ultravioletti moderati, indice {uv:.0f}. "
              f"Occhiali da sole consigliati nelle ore centrali.")

    # Visibilità ridotta (rischio incidenti)
    if visibilita < 500:
        parla(f"Nebbia fitta, solo {int(visibilita)} metri di visibilità. "
              f"Meglio non guidare.")
    elif visibilita < 2000:
        parla("Un po' di foschia. Attento se devi prendere la macchina.")

    # Chiusura e reindirizzamento al listener
    parla("Questo è tutto quello che so sul tempo di oggi. "
          "Posso aiutarti con qualcos'altro?")
    print("[METEO] ✓ controlla_meteo completato")

# ─── TEST STANDALONE ─────────────────────────────────────────────────────────
# Questo blocco viene eseguito solo se il file viene avviato direttamente (python meteo.py).
# Se il file viene importato in main.py, questo blocco viene ignorato.
if __name__ == "__main__":
    print("[METEO] Esecuzione in modalità test (senza microfono)")
    
    # Mock delle funzioni vocali per permettere il test testuale su riga di comando
    def parla_test(t): print(f"  [ROBOT DICE] {t}")
    def chiedi_test(d):
        print(f"  [ROBOT CHIEDE] {d}")
        return input("  [TU] ")
        
    citta = input("Città da testare: ")
    controlla_meteo(citta, parla_test, chiedi_test)