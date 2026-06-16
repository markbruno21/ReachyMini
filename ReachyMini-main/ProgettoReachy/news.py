# news.py – versione vocale con riassunto breve, nessun HTML, usa GoogleNewsClient
import html
from google_news_api import GoogleNewsClient
from utilities import clean_html_to_text

## importato da alessio 

print("[NEWS] news.py (versione vocale) importato correttamente")

# Dizionario di categorizzazione: associa macro-argomenti a parole chiave specifiche.
# Ottimizzato per filtrare notizie di reale utilità o interesse per un target anziano.
SOGGETTI_UTILI = {
    "salute": ["salute", "sanità", "ospedale", "vaccino", "medico"],
    "meteo": ["meteo", "tempo", "allerta", "alluvione"],
    "eventi locali": ["evento", "festa", "concerto", "mercato", "inaugurazione"],
    "trasporti": ["treno", "autobus", "sciopero", "viabilità", "strada"],
    "sicurezza": ["incidente", "allerta", "protezione civile", "evacuazione"]
}

def _estrai_riassunto_breve(articolo, max_frasi=2, max_caratteri=350):
    """
    Estrae il testo informativo dall'articolo (cercando in vari campi del dizionario API),
    lo ripulisce dai tag HTML e lo accorcia per non sovraccaricare l'ascolto dell'anziano.
    """
    # Fallback sequenziale sui campi testuali restituiti dal client GNews
    testo_originale = (
        articolo.get("summary") or 
        articolo.get("description") or 
        articolo.get("content") or 
        ""
    )
    if not testo_originale:
        return "Nessun riassunto disponibile."

    # 1. Rimozione di tag HTML, link ed entità residue tramite utilities.py
    testo_pulito = clean_html_to_text(testo_originale, max_chars=max_caratteri)
    
    # 2. Tronca il testo limitandolo alle prime frasi per brevità espositiva
    frasi = testo_pulito.split(". ")
    riassunto = ". ".join(frasi[:max_frasi])
    if riassunto and not riassunto.endswith("."):
        riassunto += "."
        
    # 3. Controllo di sicurezza sulla lunghezza totale per evitare sforamenti
    if len(riassunto) > max_caratteri:
        riassunto = riassunto[:max_caratteri].rsplit(" ", 1)[0] + "…"
    return riassunto

def _cerca_notizie(query, max_results=8, when=None, language="it", country="IT"):
    """
    Gestore sicuro per l'interfaccia GoogleNewsClient. 
    Usa il costrutto 'with' per garantire la chiusura della sessione ed evita crash in caso di errore API.
    """
    print(f"[NEWS] Cerco: '{query}' when={when} max={max_results}")
    try:
        with GoogleNewsClient(language=language, country=country, 
                              requests_per_minute=60, cache_ttl=300) as client:
            if query:
                # Ricerca mirata basata sulla stringa dell'utente
                return client.search(query, when=when, max_results=max_results)
            else:
                # Fallback sulle notizie principali del giorno se la query è vuota
                return client.top_news(max_results=max_results)
    except Exception as e:
        print(f"[NEWS] ✗ Errore API: {e}")
        return []

def _filtra_per_argomento(articoli, argomento):
    """
    Scansiona i titoli e i sommari degli articoli scaricati. 
    Mantiene solo quelli che contengono almeno una parola chiave definita in SOGGETTI_UTILI.
    """
    keywords = SOGGETTI_UTILI.get(argomento.lower(), [])
    if not keywords:
        return articoli # Se l'argomento non è mappato, non applica filtri distruttivi
    out = []
    for a in articoli:
        testo = (a.get("title","") + " " + (a.get("summary") or "")).lower()
        # Verifica la presenza di una qualunque keyword pertinente all'interno del testo
        if any(k in testo for k in keywords):
            out.append(a)
    print(f"[NEWS] Filtrati {len(out)}/{len(articoli)} articoli per '{argomento}'")
    return out

def accorcia_titolo(titolo, max_len=80):
    """
    Ottimizza la leggibilità vocale dei titoli dei giornali.
    Spezza la stringa alla prima interruzione editoriale per evitare titoli prolissi o ripetitivi.
    """
    if len(titolo) <= max_len:
        return titolo
    # Taglia in corrispondenza dei separatori tipici usati nei feed giornalistici
    for sep in [' | ', ' – ', ': ', '. ']:
        if sep in titolo:
            return titolo.split(sep)[0]
    # Taglio bruteforce se non ci sono separatori, preservando l'integrità dell'ultima parola
    return titolo[:max_len].rsplit(' ', 1)[0] + '…'

def _scegli_articolo(articoli, parla, chiedi):
    """
    Presenta all'utente l'elenco dei titoli disponibili e converte la risposta 
    vocale (numerica o testuale) nell'indice dell'articolo corrispondente.
    """
    if not articoli:
        return None
    if len(articoli) == 1:
        return articoli[0]
    
    # Costruzione dell'elenco dei titoli da leggere all'anziano
    mess = "Ho trovato più articoli. Dimmi quale vuoi ascoltare: "
    for i, a in enumerate(articoli[:5]):
        titolo_completo = html.unescape(a.get("title", "Senza titolo"))
        titolo_breve = accorcia_titolo(titolo_completo)
        mess += f"{i+1}: {titolo_breve}. "
    parla(mess)
    
    risposta = chiedi("Quale numero preferisci?").lower()
    
    # Mappatura fonetica per interpretare correttamente la risposta del microfono
    mappa = {"1":0, "uno":0, "2":1, "due":1, "3":2, "tre":2, "4":3, "quattro":3, "5":4, "cinque":4}
    for token, idx in mappa.items():
        if token in risposta:
            if idx < len(articoli):
                return articoli[idx]
                
    # Fallback di usabilità: se l'anziano esita o il TTS non capisce, legge comunque la prima notizia
    parla("Non ho capito bene, ti leggo il primo articolo.")
    return articoli[0]

# ──────────────────────────────────────────────────────────────────────────
# TODO: modificare la chiamata a questa funzione !!
# ──────────────────────────────────────────────────────────────────────────
def leggi_notizie(parla, chiedi, topic=None, when=None):
    """
    Interfaccia principale del modulo notizie. Gestisce l'interazione end-to-end:
    richiesta argomento -> download -> filtraggio -> scelta utente -> lettura riassunto.
    """
    print(f"\n[NEWS] ═══ leggi_notizie(topic='{topic}') ═══")
    
    # Se il main non passa un argomento predefinito, lo richiede direttamente all'utente
    if not topic:
        topic = chiedi("Dimmi di che argomento vuoi le notizie, ad esempio: salute, meteo o eventi locali. ").strip()
        if not topic:
            topic = "generale"
    
    parla(f"Cerco le ultime notizie su {topic}.")
    
    # 1. Download degli articoli tramite API
    articoli = _cerca_notizie(topic, max_results=10, when=when, language="it", country="IT")
    
    if not articoli:
        parla("Non ho trovato nulla al momento.")
        return
    
    # 2. Scrematura semantica degli articoli basata sul dizionario locale
    articoli = _filtra_per_argomento(articoli, topic)
    
    # 3. Fallback: se il filtro è troppo stringente e svuota la lista, recupera le top news nazionali
    if not articoli:
        parla("Non ci sono articoli specifici. Ti leggo i titoli principali della giornata.")
        articoli = _cerca_notizie("", max_results=5, language="it", country="IT")
        if not articoli:
            parla("Nessuna notizia disponibile al momento.")
            return
    
    # 4. Output di tracciamento dei titoli sul log di debug a schermo
    for i, a in enumerate(articoli[:5]):
        titolo = html.unescape(a.get("title", "Titolo mancante"))
        print(f"[NEWS] {i+1}. {titolo}")
    
    # 5. Avvio della procedura interattiva di scelta dell'articolo
    scelto = _scegli_articolo(articoli, parla, chiedi)
    if not scelto:
        parla("Non ho potuto selezionare nessun articolo.")
        return
    
    # 6. Estrazione dei metadati editoriali
    titolo_pulito = html.unescape(scelto.get("title", "Titolo mancante"))
    fonte = scelto.get("source") or scelto.get("source_name") or scelto.get("publisher") or "fonte sconosciuta"
    data = scelto.get("published") or scelto.get("published_date") or "data non specificata"
    
    # Estrazione e pulizia del riassunto (Redundancy bug risolto qui)
    riassunto_breve = _estrai_riassunto_breve(scelto, max_frasi=2, max_caratteri=350)
    
    # Controllo di ridondanza: evita di ripetere il titolo se il sommario coincide con esso
    if (len(riassunto_breve) < 20 or 
        riassunto_breve.lower().startswith(titolo_pulito.lower()[:30])):
        riassunto_breve = ""
    
    # 7. Generazione del testo finale e attivazione del TTS (Missing call bug risolto qui)
    testo_voce = f"Ecco l'articolo scelto. {titolo_pulito}. "
    testo_voce += f"Fonte: {fonte}. "
    if riassunto_breve:
        testo_voce += f"Riassunto: {riassunto_breve}"
        
    parla(testo_voce)
    print("[NEWS] ✓ leggi_notizie completato")

# ──────────────────────────────────────────────────────────────────────────
# TEST STANDALONE
# ──────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("[NEWS] Modalità test vocale (simulata)")
    def parla_test(t): print(f"  [ROBOT DICE] {t}")
    def chiedi_test(d):
        print(f"  [ROBOT CHIEDE] {d}")
        return input("  [TU] ").strip().lower()
    
    topic_test = input("Argomento (invio per generico): ").strip() or None
    when_test = input("Periodo (es. 24h, 7d) invio per default: ").strip() or None
    leggi_notizie(parla_test, chiedi_test, topic=topic_test, when=when_test)