# ╔══════════════════════════════════════════════════════════════════════╗
# ║         REACHY MINI  –  "Gioco delle Parole" con Nonna Carmela      ║
# ║         Progetto HRI –  RSA del futuro 2035                         ║
# ║         Attività:       Associazione di Parole                      ║
# ╚══════════════════════════════════════════════════════════════════════╝
#
# ISTRUZIONI DI AVVIO (all'interno di ReachyEMU):
#   1. Attivare il venv:   .venv/Scripts/activate.ps1   (PowerShell)
#   2. Avviare il daemon:  reachy-mini-daemon --sim      (finestra separata)
#   3. Eseguire:           python interazione_reachy.py
 
import time
import random
import unicodedata
from reachy_mini import ReachyMini
 
# ─────────────────────────────────────────────────────────────
#  CONFIGURAZIONE – parametri globali dell'interazione
# ─────────────────────────────────────────────────────────────
 
NOME_UTENTE = "Carmela"          # Nome della persona anziana
VELOCITA_PARLATA = 1.4           # Secondi di pausa dopo ogni battuta. Rispettare i tempi di elaborazione di un utente anziano senza risultare incalzante
PAUSA_BREVE = 0.8                # Pausa breve tra azioni multimodali, per lasciare a Carmela il tempo necessario per rispondere senza stress
PAUSA_LUNGA = 2.5                # Pausa lunga per lasciare rispondere
 
# Numero massimo di ripetizioni prima di passare oltre (XAI – trasparenza)
MAX_TENTATIVI_INCOMPRENSIONE = 2
 
# Una "banca dati" strutturata con categorie autobiografiche (Estate, Cucina, Musica) progettate per stimolare la memoria semantica senza frustrazione
PAROLE_GIOCO = {
    "estate": {
        "attese": ["sole", "mare", "caldo", "spiaggia", "vacanze", "gelato", "ombrellone"],
        "feedback_positivo": [
            "Ah, che bella parola! Anch'io adoro {risposta} d'estate!",
            "Bravissima! {risposta} mi fa venire voglia di vacanze!",
            "Certo! {risposta}… mi fa pensare a momenti felici!",
        ],
        "feedback_inatteso": "Interessante! Non ci avevo pensato, ma ha senso!"
    },
    "cucina": {
        "attese": ["profumo", "pasta", "mamma", "calore", "ricetta", "famiglia", "sugo", "pane"],
        "feedback_positivo": [
            "Ecco sì, {risposta}! Sento quasi il profumo!",
            "Che bella! {risposta}… la cucina è proprio il cuore della casa.",
            "{risposta}! Lei cucina ancora? Mi piacerebbe sentire le sue ricette!",
        ],
        "feedback_inatteso": "Che associazione originale! Non smette mai di sorprendermi!"
    },
    "musica": {
        "attese": ["ballo", "gioia", "canto", "radio", "ricordi", "cuore", "danza", "melodia"],
        "feedback_positivo": [
            "Oh, {risposta}! La musica fa proprio questo, vero?",
            "{risposta}… già. La musica ci porta sempre in un posto speciale.",
            "Proprio così! {risposta}. Che bel pensiero!",
        ],
        "feedback_inatteso": "Wow, non me lo aspettavo! È una visione molto personale, mi piace!"
    }
}
 
 
# ─────────────────────────────────────────────────────────────
#  FUNZIONE: normalizza l'input dell'utente. Questo assicura che il robot capisca la risposta anche se Carmela commette piccoli errori di digitazione o accento
# ─────────────────────────────────────────────────────────────
 
def normalizza_input(testo: str) -> str:
    """
    Normalizza la stringa in ingresso per rendere il matching
    robusto rispetto a maiuscole, spazi e accenti.
 
    Operazioni applicate:
      1. strip()  – rimuove spazi iniziali/finali
      2. lower()  – uniforma a minuscolo
      3. NFD + rimozione diacritici – "sì" → "si", "è" → "e"
         (evita che un anziano che non trova l'accento sulla tastiera
          venga trattato come input non riconosciuto)
 
    Returns:
        Stringa pulita pronta per il matching con keyword.
    """
    testo = testo.strip().lower()
    # Scomposizione unicode: separa carattere base da diacritico
    testo_nfd = unicodedata.normalize("NFD", testo)
    # Mantieni solo i caratteri base (categoria "Ll", "Lu", "Nd", spazi, punteggiatura)
    testo_pulito = "".join(
        c for c in testo_nfd
        if unicodedata.category(c) != "Mn"  # Mn = Mark, Nonspacing (diacritici)
    )
    return testo_pulito
 
 
# ─────────────────────────────────────────────────────────────
#  FUNZIONE: gestione trasparente dell'incomprensione (XAI). 
# Se l'input è nullo o confuso, Reachy ammette il limite ("i miei circuiti sono lenti") inclinando la testa. Questo implementa la trasparenza (Explainability) l'utente capisce che il problema è del robot, non suo, aumentando la fiducia nel sistema
# ─────────────────────────────────────────────────────────────
 
def non_capisco(reachy: ReachyMini, contesto: str = "risposta") -> str:
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
 
 
# ─────────────────────────────────────────────────────────────
#  FUNZIONE: mostra comportamento "in ascolto"
# ─────────────────────────────────────────────────────────────
 
def ascolto_attivo(reachy: ReachyMini):
    """
    Movimenti del robot che segnalano attenzione e ascolto:
    - testa leggermente inclinata a sinistra (postura empatica)
    - LED occhi in colore caldo (attenzione)
    """
    reachy.head.turn_left(10)         # inclinazione empatica
    time.sleep(PAUSA_BREVE)
    reachy.left_eye.look_at(0, 0)     # contatto visivo centrato
 
 
# ─────────────────────────────────────────────────────────────
#  FUNZIONE: gesto di entusiasmo (risposta corretta)
# ─────────────────────────────────────────────────────────────
 
def gesto_entusiasmo(reachy: ReachyMini):
    """
    Piccolo movimento delle braccia verso l'alto per comunicare
    sorpresa positiva e approvazione; la testa si sposta in avanti.
    """
    reachy.head.look_forward()
    time.sleep(PAUSA_BREVE * 0.5)
    reachy.right_arm.raise_up(30)    # braccio su (gesto apertura)
    time.sleep(0.4)
    reachy.right_arm.lower()
    reachy.head.nod()                # annuire
 
 
# ─────────────────────────────────────────────────────────────
#  FUNZIONE: gesto di incoraggiamento (risposta inattesa)
# ─────────────────────────────────────────────────────────────
 
def gesto_incoraggiamento(reachy: ReachyMini):
    """
    La testa si sposta leggermente di lato (curiosità),
    poi annuisce dolcemente.
    """
    reachy.head.turn_right(8)
    time.sleep(PAUSA_BREVE)
    reachy.head.nod()
    time.sleep(0.3)
    reachy.head.look_forward()
 
 
# ─────────────────────────────────────────────────────────────
#  FUNZIONE: parla – stampa testo e simula la pausa parlata
# ─────────────────────────────────────────────────────────────
 
def parla(testo: str, pausa: float | None = None):
    """
    Stampa il testo del robot su console con prefisso visivo
    e attende il tempo necessario per una cadenza naturale.
    
    Args:
        testo:  Frase da pronunciare.
        pausa:  Secondi di attesa (default: VELOCITA_PARLATA).
    """
    print(f"\n🤖  Reachy: \"{testo}\"")
    time.sleep(pausa if pausa is not None else VELOCITA_PARLATA)
 
 
# ─────────────────────────────────────────────────────────────
#  FUNZIONE: raccoglie input dell'utente (con timeout simulato)
# ─────────────────────────────────────────────────────────────
 
def ascolta_risposta(prompt: str = "") -> str:
    """
    Acquisisce la risposta dell'anziano da tastiera e la normalizza.
 
    Normalizzazione applicata via normalizza_input():
      - minuscolo, strip degli spazi, rimozione diacritici
      => "Sì!" → "si", "Benissimo " → "benissimo", "è" → "e"
    Questo evita falsi negativi nel keyword-matching causati da
    maiuscole, accenti mancanti o spazi accidentali.
 
    Returns:
        La stringa della risposta normalizzata, pronta per il matching.
    """
    print(f"\n👤  {NOME_UTENTE}: ", end="")
    risposta_grezza = input(prompt)
    # ── separazione visiva: pausa DOPO l'input, PRIMA della reazione
    # garantisce che il turno di parola dell'utente sia concluso
    # prima che il robot risponda (requisito timing HRI)
    time.sleep(PAUSA_BREVE)
    return normalizza_input(risposta_grezza)
 
 
# ─────────────────────────────────────────────────────────────
#  FASE 1 – SALUTO  (approccio proattivo)
# ─────────────────────────────────────────────────────────────
 
def fase_saluto(reachy: ReachyMini):
    """
    FASE 1 – SALUTO (approccio proattivo).
 
    Il robot si avvicina con gradualità (pausa iniziale di 1.5s che
    simula il rallentamento del carrello prima di parlare), stabilisce
    il contatto visivo e saluta usando il nome proprio dell'utente.
 
    Gestione input (due tipi):
      - Tipo A (risposta positiva): nod() + frase entusiasta + gesto apertura
      - Tipo B (risposta neutra/negativa): ascolto_attivo() + risposta empatica
      - Tipo C (input vuoto): recovery XAI con non_capisco()
    """
    print("\n" + "═" * 60)
    print("  FASE 1 · SALUTO")
    print("═" * 60)
 
    # Simulazione avvicinamento graduale: pausa prima di parlare
    # (principio HRI: non irrompere nella conversazione – evita Uncanny Cliff)
    reachy.head.look_forward()
    time.sleep(1.5)          # ← gesto completato; solo ora il robot parla
    reachy.head.nod()        # cenno di saluto
    time.sleep(PAUSA_BREVE)  # ← pausa post-gesto prima della voce
 
    parla(f"Buona mattina, {NOME_UTENTE}! Come sta oggi?", pausa=2.0)
 
    risposta = ascolta_risposta()
 
    # Recovery XAI: se l'input è vuoto, il robot chiede gentilmente
    if not risposta:
        risposta = non_capisco(reachy, contesto="come si sente")
 
    # Gestione Tipo A (positiva) vs. Tipo B (neutro/negativo)
    if any(kw in risposta for kw in ["bene", "benissimo", "abbastanza", "buona", "bello"]):
        reachy.head.nod()
        time.sleep(PAUSA_BREVE)          # ← pausa: gesto separato dalla voce
        parla("Che bello sentire questo! Anch'io sono molto contento di vederla.")
        gesto_entusiasmo(reachy)
    else:
        ascolto_attivo(reachy)
        time.sleep(PAUSA_BREVE)          # ← postura completata prima di rispondere
        parla("Mi dispiace… ma sono qui con lei. Magari insieme ci tiriamo su, no?")
 
    time.sleep(PAUSA_BREVE)
 
 
# ─────────────────────────────────────────────────────────────
#  FASE 2 – PROPOSTA DELL'ATTIVITÀ  (invito amichevole)
# ─────────────────────────────────────────────────────────────
 
def fase_proposta(reachy: ReachyMini) -> bool:
    """
    FASE 2 – PROPOSTA DELL'ATTIVITÀ (invito non impositivo).
 
    Il robot presenta il gioco con due frasi brevi separate da una
    pausa, per non sovraccaricare la comprensione. La proposta finale
    usa una domanda aperta che lascia piena libertà di rifiutare.
 
    Gestione input (due tipi):
      - Tipo A (accetta): gesto_entusiasmo() + conferma verbale → return True
      - Tipo B (rifiuta o input vuoto): risposta empatica → return False
    La biforcazione permette di attivare flusso_chiacchiera() come
    "Piano B" senza fallimento totale dell'interazione.
 
    Returns:
        True se l'utente accetta il gioco, False altrimenti.
    """
    print("\n" + "═" * 60)
    print("  FASE 2 · PROPOSTA ATTIVITÀ")
    print("═" * 60)
 
    reachy.head.look_forward()
    time.sleep(PAUSA_BREVE)              # ← sguardo stabilito prima di parlare
    parla("Ho pensato che potremmo fare qualcosa di divertente insieme…")
    time.sleep(0.6)
    parla("Conosce il gioco delle parole? Uno dice una parola, "
          "l'altro risponde con la prima cosa che gli viene in mente.")
 
    parla(f"Le va di giocare un po' con me, {NOME_UTENTE}? "
          "Non ci sono risposte giuste o sbagliate, promesso!", pausa=PAUSA_LUNGA)
 
    risposta = ascolta_risposta()
 
    # Tipo A – accettazione esplicita
    if any(kw in risposta for kw in ["si", "certo", "va bene", "ok", "volentieri",
                                      "dai", "perche no", "sure", "magari"]):
        gesto_entusiasmo(reachy)
        time.sleep(PAUSA_BREVE)          # ← gesto completo prima della risposta verbale
        parla("Fantastico! Sapevo che era curiosa!")
        return True
    else:
        # Tipo B – rifiuto o incertezza: attiva Piano B (flusso_chiacchiera)
        ascolto_attivo(reachy)
        time.sleep(PAUSA_BREVE)          # ← postura stabilita prima di parlare
        parla("Nessun problema, capisco. Vuole che restiamo un po' a chiacchierare allora?")
        return False
 
 
# ─────────────────────────────────────────────────────────────
#  FASE 3 – SPIEGAZIONE DEL TASK  (istruzioni chiare)
# ─────────────────────────────────────────────────────────────
 
def fase_spiegazione(reachy: ReachyMini):
    """
    FASE 3 – SPIEGAZIONE DELLE REGOLE.
 
    Le istruzioni sono spezzate in frasi brevi (max 20 parole ciascuna)
    con pause intermedie, per rispettare i limiti di processing dell'anziano.
    Un esempio concreto ("inverno" → "freddo") riduce l'astrazione.
 
    Timing voce-gesto:
      - look_forward() completato con pausa PRIMA del primo parlato
      - nod() completato con pausa PRIMA della conferma verbale
 
    Gestione input (due tipi):
      - Tipo A (comprende): nod() + pausa + conferma breve
      - Tipo B (incerto o silenzio): rassicurazione; il gioco parte comunque
    """
    print("\n" + "═" * 60)
    print("  FASE 3 · SPIEGAZIONE REGOLE")
    print("═" * 60)
 
    reachy.head.look_forward()
    time.sleep(PAUSA_BREVE)              # ← sguardo stabilito prima di parlare
    parla("Funziona così: le dico una parola…", pausa=1.2)
    parla("…e lei mi dice la prima parola che le passa per la testa. Subito, senza pensarci troppo!")
    time.sleep(0.5)
    parla("Per esempio: se dico 'inverno'… lei potrebbe pensare a 'freddo', "
          "o 'camino', o magari a qualcosa di completamente diverso. Va benissimo così!")
 
    parla("Ha capito? Si sente pronta?", pausa=PAUSA_LUNGA)
 
    risposta = ascolta_risposta()
 
    # Tipo A – comprensione confermata
    # Nota: normalizza_input() ha già tolto accenti, quindi "si" cattura anche "sì"
    if any(kw in risposta for kw in ["si", "pronta", "certo", "capito", "ok", "chiaro"]):
        reachy.head.nod()
        time.sleep(PAUSA_BREVE)          # ← nod() completato prima di parlare
        parla("Perfetto! Allora cominciamo!")
    else:
        # Tipo B – incertezza o silenzio: non insistere, partire comunque
        parla("Nessun problema, lo vediamo insieme con la prima parola. Ci penso io!")
 
 
# ─────────────────────────────────────────────────────────────
#  FASE 4 – SVOLGIMENTO DEL GIOCO  (3 round)
# ─────────────────────────────────────────────────────────────
 
def fase_gioco(reachy: ReachyMini) -> list[tuple[str, str]]:
    """
    FASE 4 – SVOLGIMENTO DEL GIOCO (3 round).
 
    Per ogni parola stimolo il robot:
      1. Annuncia con enfasi (testa dritta + pausa drammatica)
      2. Si mette in ascolto_attivo() PRIMA che l'utente risponda
      3. Raccoglie e normalizza l'input
      4. Gestisce due tipi di risposta:
           - Tipo A (risposta nel vocabolario atteso):
               feedback specifico che cita la parola dell'utente
               + gesto_entusiasmo() completato con pausa prima del parlato
           - Tipo B (risposta fuori vocabolario):
               sorpresa positiva + domanda di approfondimento narrativo
               + gesto_incoraggiamento() con pausa
      5. Recovery XAI (Tipo C – input vuoto):
           loop max MAX_TENTATIVI_INCOMPRENSIONE con non_capisco()
           Se l'utente non risponde dopo i tentativi, il robot passa
           oltre senza penalizzare ("Nessun problema, andiamo avanti!")
 
    Timing voce-gesto: ogni movimento è seguito da time.sleep(PAUSA_BREVE)
    prima della frase verbale successiva, per separare i canali comunicativi.
 
    Returns:
        Lista di tuple (parola_stimolo, risposta_utente) per la Fase 5.
    """
    print("\n" + "═" * 60)
    print("  FASE 4 · SVOLGIMENTO GIOCO (3 round)")
    print("═" * 60)
 
    parole_scelte = random.sample(list(PAROLE_GIOCO.keys()), 3)
    storico_risposte = []
 
    for i, parola_stimolo in enumerate(parole_scelte, start=1):
        dati = PAROLE_GIOCO[parola_stimolo]
 
        print(f"\n  — Round {i}/3 —")
 
        # ── Annuncio della parola stimolo ────────────────────────
        reachy.head.look_forward()
        time.sleep(PAUSA_BREVE)          # ← sguardo stabilito prima del parlato
        parla(f"Ecco la parola numero {i}…", pausa=1.0)
        time.sleep(0.4)                  # pausa drammatica prima della parola
        parla(f"« {parola_stimolo.upper()} »", pausa=PAUSA_LUNGA)
 
        # Postura di ascolto PRIMA che l'utente risponda
        ascolto_attivo(reachy)
        time.sleep(PAUSA_BREVE)          # ← postura completata prima dell'input
 
        # ── Raccolta input con recovery XAI ─────────────────────
        risposta = ascolta_risposta()
        tentativi = 0
        while not risposta and tentativi < MAX_TENTATIVI_INCOMPRENSIONE:
            # Tipo C – input vuoto: recovery trasparente (XAI)
            risposta = non_capisco(reachy, contesto="la sua parola")
            tentativi += 1
 
        if not risposta:
            # Esauriti i tentativi: il robot passa oltre senza creare imbarazzo
            reachy.head.nod()
            time.sleep(PAUSA_BREVE)
            parla("Nessun problema, andiamo avanti!")
            storico_risposte.append((parola_stimolo, "—"))
            continue
 
        # ── Feedback differenziato: Tipo A vs Tipo B ────────────
        if any(attesa in risposta for attesa in dati["attese"]):
            # Tipo A – risposta nel vocabolario atteso
            template = random.choice(dati["feedback_positivo"])
            # Estrae la keyword specifica trovata per personalizzare il messaggio
            parola_trovata = next(
                (a for a in dati["attese"] if a in risposta),
                risposta.split()[0] if risposta else risposta
            )
            messaggio = template.format(risposta=parola_trovata)
            gesto_entusiasmo(reachy)
            time.sleep(PAUSA_BREVE)      # ← gesto completato prima del parlato
            parla(messaggio)
        else:
            # Tipo B – risposta creativa/inattesa: sorpresa positiva
            gesto_incoraggiamento(reachy)
            time.sleep(PAUSA_BREVE)      # ← gesto completato prima del parlato
            parla(dati["feedback_inatteso"])
            time.sleep(0.6)
            # Domanda di approfondimento: usa la parola specifica dell'utente
            parla(f"'{risposta}'… mi racconti: cosa le ha fatto venire in mente "
                  "questa parola?", pausa=PAUSA_LUNGA)
            approfondimento = ascolta_risposta()
            if approfondimento:
                ascolto_attivo(reachy)
                time.sleep(PAUSA_BREVE)  # ← postura completata prima del parlato
                parla("Che storia bella. Grazie per avermelo raccontato.")
 
        storico_risposte.append((parola_stimolo, risposta))
        time.sleep(PAUSA_BREVE)
 
    return storico_risposte
 
 
# ─────────────────────────────────────────────────────────────
#  FASE 5 – DOMANDA DI APPROFONDIMENTO  (conversazione)
# ─────────────────────────────────────────────────────────────
 
def fase_approfondimento(reachy: ReachyMini, storico: list[tuple[str, str]]):
    """
    FASE 5 – APPROFONDIMENTO CONVERSAZIONALE (memoria narrativa).
 
    Il robot dimostra "memoria" richiamando una risposta specifica del gioco,
    aprendo così uno spazio di narrazione autobiografica. Questo è il momento
    emotivamente più significativo: l'anziano si sente davvero ascoltato.
 
    Principio HRI applicato: il robot non fa solo domande generiche, ma
    collega la domanda a qualcosa che Carmela ha già detto → senso di essere
    stati "visti" (riduzione del senso di invisibilità tipico della RSA).
 
    Timing: ascolto_attivo() completato con pausa PRIMA di ogni frase;
    nel branch narrativo il robot lascia spazio con PAUSA_LUNGA.
 
    Gestione input (due tipi):
      - Tipo A (racconto articolato, > 2 caratteri): spazio per continuare
      - Tipo B (risposta breve o silenzio): risposta empatica e discreta
    """
    print("\n" + "═" * 60)
    print("  FASE 5 · APPROFONDIMENTO CONVERSAZIONALE")
    print("═" * 60)
 
    # Sceglie una risposta significativa dallo storico (esclude i round saltati)
    storico_valido = [(s, r) for s, r in storico if r != "—"]
    parola_stimolo, risposta_utente = random.choice(storico_valido if storico_valido else storico)
 
    ascolto_attivo(reachy)
    time.sleep(PAUSA_BREVE)              # ← postura completata prima di parlare
    parla("È stato bellissimo giocare con lei!")
    time.sleep(0.6)
    parla(f"Ho notato che ha detto '{risposta_utente}' quando ho detto '{parola_stimolo}'…")
    time.sleep(0.5)
    parla("Questa parola le ha ricordato qualcosa in particolare? Un posto, una persona…?",
          pausa=PAUSA_LUNGA)
 
    risposta = ascolta_risposta()
 
    # Tipo A – racconto articolato
    if risposta and len(risposta) > 2:
        ascolto_attivo(reachy)
        time.sleep(PAUSA_BREVE)          # ← postura completata prima di parlare
        parla("Grazie per condividere questo con me. Questi ricordi sono un tesoro.")
        time.sleep(0.8)
        parla("Ne parla ancora, se vuole. Ho tutto il tempo del mondo per ascoltarla.",
              pausa=PAUSA_LUNGA)
        ascolta_risposta()               # raccoglie eventuale racconto aggiuntivo
        gesto_incoraggiamento(reachy)
        time.sleep(PAUSA_BREVE)          # ← gesto completato prima di parlare
        parla("Davvero bellissimo. Si vede che ha vissuto tanto.")
    else:
        # Tipo B – silenzio o risposta brevissima: rispettare la riservatezza
        reachy.head.nod()
        time.sleep(PAUSA_BREVE)
        parla("Capisco. Certe cose è bello tenerle nel cuore, non c'è bisogno di parole.")
 
 
# ─────────────────────────────────────────────────────────────
#  FASE 6 – CHIUSURA  (saluto finale positivo)
# ─────────────────────────────────────────────────────────────
 
def fase_chiusura(reachy: ReachyMini):
    """
    FASE 6 – CHIUSURA (saluto finale positivo).
 
    Il robot chiude l'interazione con tre elementi chiave:
      1. Ringraziamento personalizzato (cita il nome)
      2. Riconoscimento del valore della persona ("mi insegna qualcosa")
      3. Congedo fisico: wave() + promessa di ritorno
 
    Timing: look_forward() e wave() sono sempre seguiti da time.sleep()
    per dare al gesto il suo spazio prima della parola successiva.
    La promessa di ritorno ("ci rivediamo presto") riduce l'ansia
    da abbandono tipica dell'anziano istituzionalizzato.
    """
    print("\n" + "═" * 60)
    print("  FASE 6 · CHIUSURA")
    print("═" * 60)
 
    reachy.head.look_forward()
    time.sleep(PAUSA_BREVE)              # ← sguardo stabilito prima di parlare
 
    parla(f"Grazie mille, {NOME_UTENTE}. Ho davvero goduto questo tempo con lei.")
    time.sleep(0.5)
    parla("È speciale, sa? Ogni conversazione con lei mi insegna qualcosa di nuovo.")
 
    # Gesto di congedo: inclinazione + wave() + pausa prima della frase finale
    reachy.head.turn_left(5)
    time.sleep(PAUSA_BREVE)              # ← gesto completato prima del wave
    reachy.right_arm.wave()
    time.sleep(0.6)                      # ← wave completato prima di parlare
    reachy.head.look_forward()
 
    parla("Ci rivediamo presto. Si prenda cura di sé!", pausa=2.0)
 
    # Post-interazione: robot torna in posizione neutra e si spegne
    reachy.head.look_forward()
    reachy.turn_off()
    print("\n✓  Interazione completata. Robot disattivato.\n")
 
 
# ─────────────────────────────────────────────────────────────
#  FLUSSO ALTERNATIVO – rifiuto del gioco
# ─────────────────────────────────────────────────────────────
 
def flusso_chiacchiera(reachy: ReachyMini):
    """
    PIANO B – FLUSSO ALTERNATIVO (chiacchierata libera).
 
    Attivato quando l'utente rifiuta il gioco nella Fase 2.
    Garantisce che l'interazione non termini in un "fallimento":
    il robot apre uno spazio di conversazione libera, dimostrando
    che la sua presenza ha valore anche senza un'attività strutturata.
 
    Principio HRI: un robot sociale non deve avere un solo script.
    La flessibilità aumenta la percezione di intelligenza e calore.
 
    Timing: ascolto_attivo() e gesto_incoraggiamento() sono seguiti
    da time.sleep(PAUSA_BREVE) prima di ogni frase successiva.
    """
    print("\n" + "═" * 60)
    print("  PIANO B · CHIACCHIERATA LIBERA")
    print("═" * 60)
 
    ascolto_attivo(reachy)
    time.sleep(PAUSA_BREVE)              # ← postura completata prima di parlare
    parla("Va benissimo così. A cosa sta pensando in questi giorni?", pausa=PAUSA_LUNGA)
    risposta = ascolta_risposta()
 
    if risposta:
        parla(f"Capisco… '{risposta}' è davvero importante. "
              "Mi racconti di più, se le va.", pausa=PAUSA_LUNGA)
        ascolta_risposta()
        gesto_incoraggiamento(reachy)
        time.sleep(PAUSA_BREVE)          # ← gesto completato prima di parlare
        parla("La sto ascoltando con tutto il cuore.")
 
    fase_chiusura(reachy)
 
 
# ─────────────────────────────────────────────────────────────
#  ENTRY POINT – main()
# ─────────────────────────────────────────────────────────────
 
def main():
    """
    Orchestratore principale dell'interazione.
    Esegue le fasi in sequenza rispettando il flow progettato.
    """
    print("\n" + "╔" + "═" * 58 + "╗")
    print("║   REACHY MINI · Attività di Associazione di Parole      ║")
    print("║   RSA del Futuro 2035 – Scenario HRI Anziani            ║")
    print("╚" + "═" * 58 + "╝\n")
 
    # Connessione al simulatore
    reachy = inizializza_robot()
 
    # ── Flow principale ──────────────────────────────────────
    fase_saluto(reachy)                            # 1. Saluto proattivo
 
    accetta = fase_proposta(reachy)                # 2. Proposta del gioco
 
    if accetta:
        fase_spiegazione(reachy)                   # 3. Regole
        storico = fase_gioco(reachy)               # 4. Gioco (3 round)
        fase_approfondimento(reachy, storico)      # 5. Approfondimento
        fase_chiusura(reachy)                      # 6. Chiusura
    else:
        flusso_chiacchiera(reachy)                 # Flusso alternativo
    # ────────────────────────────────────────────────────────
 
 
if __name__ == "__main__":
    main()