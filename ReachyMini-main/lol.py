
def presentazione(reachy: ReachyMini):
    global fraintendimento
    engine.say("Faccio parte di questa RSA.")
    time.sleep(PAUSA_BREVE)
    engine.say("Il mio scopo è quello di farti compagnia e aiutare come posso.")
    time.sleep(PAUSA_BREVE)
    engine.say("Vuoi sapere di più su di me? Rispondi con 'sì' o 'no'.")
    time.sleep(PAUSA_LUNGA)

    while fraintendimento < 3:
        risposta = ascolto_risposta().strip().lower()
        if risposta == "sì" or risposta == "si":
            engine.say("Sono un robot sociale progettato per fare compagnia.")
            time.sleep(PAUSA_BREVE)
            engine.say("Posso parlare, raccontare notizie e fare attività insieme a te.")
            break
        elif risposta == "no":
            engine.say("Ok, allora parliamo di altro.")
            break
        else:
            fraintendimento += 1
            non_capisco(reachy, "la risposta", fraintendimento)

    if fraintendimento >= 3:
        engine.say("Oggi proprio non riesco a funzionare, scusami. Parliamo di altro.")


def non_capisco(reachy: ReachyMini, contesto: str = "la risposta", fraintendimento: int = 0) -> str:
    """
    Fase di recupero XAI: il robot ammette di non aver capito
    usando un linguaggio autoironico e rassicurante, poi chiede
    di ripetere. Evita il "fallimento silenzioso" dell'interazione.

    Principio HRI applicato: trasparenza (XAI) aumenta la fiducia
    dell'utente anziano, che non si sente giudicato ma capisce
    che il limite è del robot, non suo.

    Args:
        reachy:         istanza del robot.
        contesto:       stringa opzionale per personalizzare la richiesta.
        fraintendimento: contatore degli errori consecutivi.

    Returns:
        La nuova risposta dell'utente, o stringa vuota al terzo errore.
    """
    reachy.head.turn_right(6)
    time.sleep(PAUSA_BREVE)

    match fraintendimento:
        case 1:
            engine.say("I miei circuiti sono lenti, scusami. Può ripetere?")
            time.sleep(PAUSA_LUNGA)
            reachy.head.look_forward()
            time.sleep(PAUSA_BREVE)
            return ascolto_risposta()
        case 2:
            engine.say(
                f"Scusi, oggi non riesco a sentire bene. "
                f"Potrebbe ripetere {contesto}? Voglio capire bene."
            )
            time.sleep(PAUSA_LUNGA)
            reachy.head.look_forward()
            time.sleep(PAUSA_BREVE)
            return ascolto_risposta()
