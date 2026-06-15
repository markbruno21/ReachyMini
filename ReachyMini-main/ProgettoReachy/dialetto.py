
DIALETTI = {
    "Piemonte": "<prosody rate='90%'>Cume stèje, <break time='250ms'/> car?</prosody>",
    "Valle_d_Aosta": "<prosody rate='90%'>Coment <break time='200ms'/> ve lo?</prosody>",
    "Lombardia": "<prosody rate='90%'>Fém dü ciàcher <break time='300ms'/> insema?</prosody>",
    "Veneto": "<prosody rate='90%'>Cossa te gà in mente <break time='250ms'/> de belo?</prosody>",
    "Trentino_Alto_Adige": "<prosody rate='90%'>Come stat, <break time='200ms'/> tut a post?</prosody>",
    "Friuli_Venezia_Giulia": "<prosody rate='90%'>Mandi, <break time='200ms'/> come va?</prosody>",
    "Liguria": "<prosody rate='90%'>Cöse gh'æ da mangiâ <break time='250ms'/> de bon?</prosody>",
    "Emilia_Romagna": "<prosody rate='90%'>Com'andela, <break time='250ms'/> vècia?</prosody>",
    "Toscana": "<prosody rate='90%'>Oh, <break time='200ms'/> tu come stai oggi?</prosody>",
    "Umbria": "<prosody rate='90%'>Com'è ita, <break time='200ms'/> oggi?</prosody>",
    "Marche": "<prosody rate='90%'>Com'andemo, <break time='200ms'/> caru?</prosody>",
    "Lazio": "<prosody rate='95%' pitch='+5%'>Aò, <break time='200ms'/> come te senti oggi?</prosody>",
    "Abruzzo": "<prosody rate='90%'>Comu stèje, <break time='250ms'/> cumparì?</prosody>",
    "Molise": "<prosody rate='90%'>Che se dice <break time='200ms'/> de bello?</prosody>",
    "Campania": "<prosody rate='90%' pitch='+5%'>Comm' <break time='250ms'/> è bell' a te vedè!</prosody>",
    "Puglia": "<prosody rate='90%'>Comu stai, <break time='250ms'/> de mmi?</prosody>",
    "Basilicata": "<prosody rate='90%'>Uè, <break time='200ms'/> com'è ita?</prosody>",
    "Calabria": "<prosody rate='90%'>Comu va, <break time='250ms'/> picciottu?</prosody>",
    "Sicilia": "<prosody rate='85%'>Comu staju, <break time='300ms'/> beddu?</prosody>",
    "Sardegna": "<prosody rate='90%'>Cumente ses, <break time='250ms'/> caru?</prosody>"
}

def ottieni_regione(input_utente):
    testo=input_utente.lower()
    
    if "piemonte" in testo or "torino" in testo: 
        return "Piemonte"
    elif "valle d'aosta" in testo or "aosta" in testo: 
        return "Valle_d_Aosta"
    elif "lombardia" in testo or "milano" in testo: 
        return "Lombardia"
    elif "veneto" in testo or "venezia" in testo or "verona" in testo: 
        return "Veneto"
    elif "trentino" in testo or "trento" in testo: 
        return "Trentino_Alto_Adige"
    elif "friuli" in testo or "trieste" in testo or "udine" in testo: 
        return "Friuli_Venezia_Giulia"
    elif "liguria" in testo or "genova" in testo: 
        return "Liguria"
    elif "emilia" in testo or "romagna" in testo or "bologna" in testo: 
        return "Emilia_Romagna"
    elif "toscana" in testo or "firenze" in testo: 
        return "Toscana"
    elif "umbria" in testo or "perugia" in testo: 
        return "Umbria"
    elif "marche" in testo or "ancona" in testo: 
        return "Marche"
    elif "lazio" in testo or "roma" in testo: 
        return "Lazio"
    elif "abruzzo" in testo or "pescara" in testo: 
        return "Abruzzo"
    elif "molise" in testo or "campobasso" in testo: 
        return "Molise"
    elif "campania" in testo or "napoli" in testo: 
        return "Campania"
    elif "puglia" in testo or "bari" in testo: 
        return "Puglia"
    elif "basilicata" in testo or "potenza" in testo: 
        return "Basilicata"
    elif "calabria" in testo or "catanzaro" in testo: 
        return "Calabria"
    elif "sicilia" in testo or "palermo" in testo: 
        return "Sicilia"
    elif "sardegna" in testo or "cagliari" in testo: 
        return "Sardegna"
    else:
        return "Complimenti. Che bel posto!"